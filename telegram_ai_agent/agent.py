import logging
from typing import Optional
from phi.assistant.assistant import Assistant
from .auth import TelegramAuth
from .inbound import InboundMessaging
from .outbound import OutboundMessaging
from .config import TelegramConfig


class TelegramAIAgent:
    def __init__(
        self,
        assistant: Assistant,
        config: TelegramConfig,
        logger: Optional[logging.Logger] = None,
    ):
        self.assistant = assistant
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.auth = TelegramAuth(config, logger=self.logger)
        self.client = None
        self.inbound = None
        self.outbound = None

    async def start(self):
        try:
            self.logger.info("Starting Telegram AI Agent...")
            self.client = await self.auth.authenticate()

            self.inbound = InboundMessaging(
                self.client, self.config, logger=self.logger
            )
            self.outbound = OutboundMessaging(
                self.client, self.config, logger=self.logger
            )

            self.logger.info(
                "Successfully started and authorized the Telegram AI Agent."
            )
        except Exception as e:
            self.logger.error(f"An error occurred while starting the agent: {e}")
            raise

    async def stop(self):
        self.logger.info("Stopping Telegram AI Agent...")
        if self.client and self.client.is_connected():
            await self.client.disconnect()
        self.logger.info("Telegram AI Agent stopped.")

    async def send_messages(self, recipients, message, throttle=0):
        if not self.outbound:
            raise RuntimeError("Agent not started. Call start() first.")
        await self.outbound.send_messages(recipients, message, throttle)

    async def process_incoming_messages(self):
        if not self.inbound:
            raise RuntimeError("Agent not started. Call start() first.")
        await self.inbound.process_messages(self.assistant)

    async def run(self):
        await self.start()
        await self.process_incoming_messages()
        if self.client:
            await self.client.run_until_disconnected()
