import csv
import logging
import asyncio
from telethon import TelegramClient as TelethonClient
from telethon.errors import SessionPasswordNeededError
from telegram_ai_agent.config import TelegramConfig


class TelegramSession:
    def __init__(self, config: TelegramConfig, logger=None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.client = None

    async def start(self) -> TelethonClient:
        self.logger.info("Connecting to Telegram servers...")
        if self.config.proxy:
            self.client = TelethonClient(
                self.config.session_name,
                self.config.api_id,
                self.config.api_hash,
                proxy=self.config.proxy,
            )
        else:
            self.client = TelethonClient(
                self.config.session_name, self.config.api_id, self.config.api_hash
            )

        try:
            await asyncio.wait_for(self.client.connect(), timeout=self.config.timeout)

            self.logger.info("Connected. Checking authorization...")
            if not await self.client.is_user_authorized():
                self.logger.info("User not authorized. Sending code request...")
                await self.client.send_code_request(self.config.phone_number)
                self.logger.info(
                    "Code request sent. Check your Telegram app for the code."
                )
                code = input("Enter the code you received: ")
                try:
                    self.logger.info("Signing in with the provided code...")
                    await self.client.sign_in(self.config.phone_number, code)
                except SessionPasswordNeededError:
                    self.logger.info(
                        "Two-step verification enabled. Enter your password."
                    )
                    password = input("Enter your password: ")
                    await self.client.sign_in(password=password)

            self.logger.info(
                f"Successfully authenticated for {self.config.phone_number}"
            )
            return self.client
        except asyncio.TimeoutError:
            self.logger.error(
                f"Connection timed out after {self.config.timeout} seconds."
            )
            raise
        except Exception as e:
            self.logger.error(f"Authentication failed: {str(e)}")
            if self.client.is_connected():
                await self.client.disconnect()
            raise

    async def stop(self):
        if self.client:
            await self.client.disconnect()
            self.logger.info("Telegram client stopped")
