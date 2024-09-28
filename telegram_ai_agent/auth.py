import asyncio
import logging
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from typing import Optional
from .config import TelegramConfig


class TelegramAuth:
    def __init__(self, config: TelegramConfig, logger: Optional[logging.Logger] = None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)

    async def authenticate(self) -> TelegramClient:
        self.logger.info("Connecting to Telegram servers...")
        if self.config.proxy:
            client = TelegramClient(
                self.config.session_name,
                self.config.api_id,
                self.config.api_hash,
                proxy=self.config.proxy,
            )
        else:
            client = TelegramClient(
                self.config.session_name, self.config.api_id, self.config.api_hash
            )

        try:
            await asyncio.wait_for(client.connect(), timeout=self.config.timeout)

            self.logger.info("Connected. Checking authorization...")
            if not await client.is_user_authorized():
                self.logger.info("User not authorized. Sending code request...")
                await client.send_code_request(self.config.phone_number)
                self.logger.info(
                    "Code request sent. Check your Telegram app for the code."
                )
                code = input("Enter the code you received: ")
                try:
                    self.logger.info("Signing in with the provided code...")
                    await client.sign_in(self.config.phone_number, code)
                except SessionPasswordNeededError:
                    self.logger.info(
                        "Two-step verification enabled. Enter your password."
                    )
                    password = input("Enter your password: ")
                    await client.sign_in(password=password)

            self.logger.info(
                f"Successfully authenticated for {self.config.phone_number}"
            )
            return client
        except asyncio.TimeoutError:
            self.logger.error(
                f"Connection timed out after {self.config.timeout} seconds."
            )
            raise
        except Exception as e:
            self.logger.error(f"Authentication failed: {str(e)}")
            if client.is_connected():
                await client.disconnect()
            raise
