import logging
import asyncio
from telethon import TelegramClient as TelethonClient
from telethon.errors import SessionPasswordNeededError
from .config import TelegramConfig


class TelegramSession(TelethonClient):
    def __init__(self, config: TelegramConfig, logger=None):
        self.logger = logger or logging.getLogger(__name__)

        # Initialize client parameters
        client_params = {
            "session": config.session_name,
            "api_id": config.api_id,
            "api_hash": config.api_hash,
        }

        # Add proxy if it's present in the config
        if config.proxy:
            client_params["proxy"] = config.proxy

        super().__init__(**client_params)

        self.config = config

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()

    async def start(self):
        self.logger.info("Connecting to Telegram servers...")
        try:
            await asyncio.wait_for(self.connect(), timeout=self.config.timeout)
            self.logger.info("Connected. Checking authorization...")
            if not await self.is_user_authorized():
                self.logger.info("User not authorized. Sending code request...")
                await self.send_code_request(self.config.phone_number)
                self.logger.info(
                    "Code request sent. Check your Telegram app for the code."
                )
                code = input("Enter the code you received: ")
                try:
                    self.logger.info("Signing in with the provided code...")
                    await self.sign_in(self.config.phone_number, code)
                except SessionPasswordNeededError:
                    self.logger.info(
                        "Two-step verification enabled. Enter your password."
                    )
                    password = input("Enter your password: ")
                    await self.sign_in(password=password)
            self.logger.info(
                f"Successfully authenticated for {self.config.phone_number}"
            )
        except asyncio.TimeoutError:
            self.logger.error(
                f"Connection timed out after {self.config.timeout} seconds."
            )
            raise
        except Exception as e:
            self.logger.error(f"Authentication failed in start(): {str(e)}")
            await self.disconnect()
            raise

    async def sign_in(self, phone=None, code=None, password=None):
        try:
            if phone and code:
                await super().sign_in(phone, code)
            elif password:
                await super().sign_in(password=password)
            else:
                raise ValueError("Code or password must be provided")
            self.logger.info(
                f"Successfully authenticated for {self.config.phone_number}"
            )
        except SessionPasswordNeededError:
            self.logger.info("Two-step verification enabled. Password required.")
            raise
        except Exception as e:
            self.logger.error(f"Authentication failed during sign-in: {str(e)}")
            raise

    async def stop(self):
        await self.disconnect()
        self.logger.info("Telegram client stopped")
