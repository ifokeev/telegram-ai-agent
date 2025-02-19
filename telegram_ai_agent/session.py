import asyncio
import logging

from typing import Callable, Optional

from telethon import TelegramClient as TelethonClient
from telethon.errors import SessionPasswordNeededError

from .config import TelegramConfig


class TelegramSession(TelethonClient):
    def __init__(
        self,
        config: TelegramConfig,
        code_callback: Optional[Callable[[], asyncio.Future[str]]] = None,
        twofa_password_callback: Optional[Callable[[], asyncio.Future[str]]] = None,
        logger=None,
    ):
        self.logger = logger or logging.getLogger(__name__)
        self.verify_config(config)

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
        self.code_callback = code_callback
        self.twofa_password_callback = twofa_password_callback

    def verify_config(self, config: TelegramConfig):
        if not config.session_name:
            raise ValueError("session_name is required in TelegramConfig")
        if not config.api_id:
            raise ValueError("api_id is required in TelegramConfig")
        if not config.api_hash:
            raise ValueError("api_hash is required in TelegramConfig")
        if not config.phone_number:
            raise ValueError("phone_number is required in TelegramConfig")

        # Verify api_id is an integer
        if not isinstance(config.api_id, int):
            raise ValueError("api_id must be an integer")

        # Verify api_hash is a string
        if not isinstance(config.api_hash, str):
            raise ValueError("api_hash must be a string")

        # Verify phone_number format (basic check)
        if not config.phone_number.startswith("+"):
            raise ValueError("phone_number must start with '+'")

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
                self.logger.info("Code request sent. Check your Telegram app.")

                if not self.code_callback:
                    raise ValueError(
                        "No code_callback provided for receiving the code."
                    )

                code = await self.code_callback()

                try:
                    self.logger.info("Signing in with the provided code...")
                    await self.sign_in(self.config.phone_number, code)
                except SessionPasswordNeededError as e:
                    self.logger.info("Two-step verification is enabled.")
                    if not self.twofa_password_callback:
                        raise ValueError(
                            "No twofa_password_callback provided for receiving the password."
                        ) from e

                    password = await self.twofa_password_callback()
                    await self.sign_in(password=password)

            self.logger.info(
                f"Successfully authenticated for {self.config.phone_number}"
            )
        except asyncio.TimeoutError as e:
            self.logger.error(
                f"Connection timed out after {self.config.timeout} seconds."
            )
            raise e from e
        except Exception as e:
            self.logger.error(f"Authentication failed in start(): {str(e)}")
            await self.disconnect()
            raise e from e

    async def sign_in(self, phone=None, code=None, password=None):
        try:
            if phone and code:
                await super().sign_in(phone, code)
            elif password:
                await super().sign_in(password=password)
            else:
                raise ValueError("Code or password must be provided")
        except SessionPasswordNeededError as e:
            self.logger.info("Two-step verification enabled. Password required.")
            raise e from e
        except Exception as e:
            self.logger.error(f"Authentication failed during sign-in: {str(e)}")
            raise e from e

    async def stop(self):
        if self.is_connected():
            await self.disconnect()
            self.logger.info("Telegram client stopped")
        else:
            self.logger.info("Telegram client was not connected")

    def set_code_callback(self, code_callback: Callable[[], asyncio.Future[str]]):
        self.code_callback = code_callback

    def set_twofa_password_callback(
        self, twofa_password_callback: Callable[[], asyncio.Future[str]]
    ):
        self.twofa_password_callback = twofa_password_callback
