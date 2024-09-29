import logging
from typing import Optional
from phi.assistant.assistant import Assistant
from .inbound import InboundMessaging
from .outbound import OutboundMessaging
from .config import TelegramConfig
from .session import TelegramSession
from .tools import TelegramTools


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
        self.session = TelegramSession(self.config, logger=self.logger)
        self.client = None

    async def start(self):
        try:
            self.logger.info("Starting Telegram AI Agent...")
            await self.session.start()

            if not self.session.client:
                raise RuntimeError("Something went wrong. Client not started.")

            self.client = self.session.client

            self.inbound = InboundMessaging(
                self.client, self.config, logger=self.logger
            )
            self.outbound = OutboundMessaging(
                self.client, self.config, logger=self.logger
            )
            self.tools = TelegramTools(self.client, logger=self.logger)

            self.logger.info(
                "Successfully started and authorized the Telegram AI Agent."
            )
        except Exception as e:
            self.logger.error(f"An error occurred while starting the agent: {e}")
            raise

    async def stop(self):
        self.logger.info("Stopping Telegram AI Agent...")
        await self.session.stop()
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
