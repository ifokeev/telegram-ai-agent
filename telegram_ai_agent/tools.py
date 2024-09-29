import csv
import logging
from telethon import TelegramClient as TelethonClient


class TelegramTools:
    def __init__(self, client: TelethonClient, logger=None):
        self.client = client
        self.logger = logger or logging.getLogger(__name__)

    async def get_chat_members(self, chat_name: str, output_file: str):
        self.logger.info(f"Fetching members from {chat_name}")

        try:
            chat = await self.client.get_entity(chat_name)

            members = []
            async for member in self.client.iter_participants(chat, aggressive=True):
                members.append(
                    {
                        "id": member.id,
                        "username": member.username,
                        "first_name": member.first_name,
                        "last_name": member.last_name,
                        "phone": member.phone,
                    }
                )

            with open(output_file, "w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(
                    file,
                    fieldnames=["id", "username", "first_name", "last_name", "phone"],
                )
                writer.writeheader()
                for member in members:
                    writer.writerow(member)

            self.logger.info(
                f"Successfully saved {len(members)} members to {output_file}"
            )
            return len(members)

        except Exception as e:
            self.logger.error(f"Error fetching members: {str(e)}")
            raise

    async def get_dialogs(self, limit=None):
        self.logger.info("Fetching dialogs...")
        dialogs = []
        async for dialog in self.client.iter_dialogs(limit=limit):
            last_message = dialog.message.message if dialog.message else "No messages"
            dialogs.append(
                {
                    "id": dialog.id,
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
