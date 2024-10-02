import os
import csv
import logging
from telethon import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import (
    ChannelParticipantsAdmins,
    ChannelParticipantsBots,
    ChannelParticipantsSearch,
    ChannelParticipantsKicked,
    ChannelParticipantsBanned,
    User,
    Chat,
    Channel,
)


class TelegramTools:
    def __init__(self, client: TelegramClient, logger=None):
        if not isinstance(client, TelegramClient):
            raise TypeError("client must be an instance of TelegramClient")
        self.client = client
        self.logger = logger or logging.getLogger(__name__)

    async def find_chat(self, chat_identifier: str):
        self.logger.info(f"Searching for chat: {chat_identifier}")
        try:
            # Check if chat_identifier is a numeric string (channel ID)
            try:
                chat_identifier = int(chat_identifier)
            except ValueError:
                pass  # If it's not an integer, keep it as a string
            chat = await self.client.get_entity(chat_identifier)
        except ValueError:
            # If direct lookup fails, try to find the chat in the user's dialogs
            self.logger.info("Direct lookup failed. Searching in dialogs...")
            dialogs = await self.get_dialogs(limit=None)  # Get all dialogs
            chat = next(
                (
                    d
                    for d in dialogs
                    if str(d["id"]) == str(chat_identifier)
                    or d["name"] == chat_identifier
                ),
                None,
            )

            if not chat:
                raise ValueError(
                    f"Cannot find any entity corresponding to {chat_identifier}"
                )

            # Get the actual entity from the found dialog
            chat = await self.client.get_entity(int(chat["id"]))

        self.logger.info(
            f"Found chat: {getattr(chat, 'title', None) or getattr(chat, 'username', 'Unknown')}"
        )
        return chat

    async def get_chat_members(
        self,
        chat_identifier: str,
        output_file: str,
        include_kick_ban: bool = False,
        output_dir: str = None,
    ):
        self.logger.info(f"Fetching members from {chat_identifier}")

        try:
            chat = await self.find_chat(chat_identifier)

            if isinstance(chat, User):
                self.logger.info(
                    f"The provided identifier is a user, not a chat or channel."
                )
                members = [
                    (
                        chat.id,
                        chat.username,
                        chat.first_name,
                        chat.last_name,
                        chat.phone,
                    )
                ]
            elif isinstance(chat, (Chat, Channel)):
                members = await self.advanced_search_participants(
                    chat, include_kick_ban
                )
            else:
                raise ValueError(f"Unsupported chat type: {type(chat)}")

            if output_dir:
                output_path = os.path.join(output_dir, output_file)
            else:
                output_path = output_file

            with open(output_path, "w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(
                    file,
                    fieldnames=["id", "username", "first_name", "last_name", "phone"],
                )
                writer.writeheader()
                for member in members:
                    writer.writerow(
                        {
                            "id": str(member[0]),
                            "username": member[1],
                            "first_name": member[2],
                            "last_name": member[3],
                            "phone": member[4],
                        }
                    )

            self.logger.info(
                f"Successfully saved {len(members)} members to {output_path}"
            )
            return len(members)

        except Exception as e:
            self.logger.error(f"Error fetching members: {str(e)}")
            raise

    async def advanced_search_participants(self, chat, include_kick_ban=False):
        if isinstance(chat, User):
            return [
                (chat.id, chat.username, chat.first_name, chat.last_name, chat.phone)
            ]

        self.logger.info(f"Performing advanced search for participants")
        members = set()
        alphabet1 = "АБCДЕЄЖФГHИІJКЛМНОПQРСТУВWХЦЧШЩЫЮЯЗ"
        alphabet2 = "АCЕHИJЛМНОРСТУВWЫ"

        async def get_with_filter(filter_type, recurse=None, alphabet=None):
            offset = 0
            max_count = 0
            while True:
                participants = await self.client(
                    GetParticipantsRequest(
                        channel=chat,
                        filter=filter_type,
                        offset=offset,
                        limit=1024,
                        hash=0,
                    )
                )
                if participants.count > max_count:
                    max_count = participants.count
                for user in participants.users:
                    members.add(
                        (
                            user.id,
                            user.username,
                            user.first_name,
                            user.last_name,
                            user.phone,
                        )
                    )
                offset += len(participants.participants)
                if offset >= participants.count or not participants.participants:
                    break

            self.logger.info(
                f"GetParticipants({getattr(filter_type, 'q', '')}) "
                f"returned {participants.count}/{max_count}. "
                f"Accumulated count: {len(members)}"
            )

            if recurse and (
                participants.count < max_count - 100
                or participants.count in (200, 1000)
            ):
                for c in alphabet or "":
                    await get_with_filter(
                        recurse(filter_type, c),
                        recurse,
                        alphabet2 if c == "А" else alphabet,
                    )

        # Fetch admins and bots
        await get_with_filter(ChannelParticipantsAdmins())
        await get_with_filter(ChannelParticipantsBots())

        # Fetch regular members
        await get_with_filter(
            ChannelParticipantsSearch(""),
            lambda f, c: ChannelParticipantsSearch(f.q + c),
            alphabet1,
        )

        if include_kick_ban:
            await get_with_filter(
                ChannelParticipantsKicked(""),
                lambda f, c: ChannelParticipantsKicked(f.q + c),
                alphabet1,
            )
            await get_with_filter(
                ChannelParticipantsBanned(""),
                lambda f, c: ChannelParticipantsBanned(f.q + c),
                alphabet1,
            )

        return list(members)

    async def get_dialogs(self, limit=None):
        self.logger.info("Fetching dialogs...")
        dialogs = []
        async for dialog in self.client.iter_dialogs(limit=limit):
            last_message = dialog.message.message if dialog.message else "No messages"
            dialogs.append(
                {
                    "id": str(dialog.id),
                    "name": dialog.name,
                    "last_message": (
                        last_message[:50] + "..."
                        if len(last_message) > 50
                        else last_message
                    ),
                    "unread_count": dialog.unread_count,
                    "type": (
                        str(dialog.entity.ENTITY_TYPE)
                        if hasattr(dialog.entity, "ENTITY_TYPE")
                        else "Unknown"
                    ),
                }
            )
        return dialogs
