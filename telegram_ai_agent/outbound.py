import logging
import asyncio
from telethon.tl.types import InputPeerUser
from telethon.errors import FloodWaitError
from .config import TelegramConfig
from .messages_handler import MessagesHandler


class OutboundMessaging(MessagesHandler):
    def __init__(self, client, config: TelegramConfig, logger=None):
        super().__init__(client, config)
        self.logger = logger or logging.getLogger(__name__)

    async def send_messages(self, recipients: list, message: str, throttle: float = 0):
        for recipient in recipients:
            try:
                user = await self.client.get_input_entity(recipient)
                if isinstance(user, InputPeerUser):
                    async for chunk in self.simulate_conversation(message, user):
                        await self.client.send_message(user, chunk)

                    self.logger.info(f"Message sent to {recipient}")
                else:
                    self.logger.warning(f"Skipping invalid recipient: {recipient}")

                if throttle > 0:
                    await asyncio.sleep(throttle)

            except FloodWaitError as e:
                self.logger.warning(f"FloodWaitError: Waiting for {e.seconds} seconds")
                await asyncio.sleep(e.seconds)
            except Exception as e:
                self.logger.error(f"Error sending message to {recipient}: {str(e)}")
