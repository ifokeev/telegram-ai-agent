import asyncio
import logging

from typing import Callable, Optional

from langchain.embeddings import OpenAIEmbeddings
from langchain_experimental.text_splitter import SemanticChunker
from phi.assistant.assistant import Assistant
from phi.llm.openai.chat import OpenAIChat

from .config import TelegramConfig
from .inbound import InboundMessaging
from .outbound import OutboundMessaging
from .session import TelegramSession
from .tools import TelegramTools


class TelegramAIAgent:
    def __init__(
        self,
        assistant: Assistant,
        config: TelegramConfig,
        logger: Optional[logging.Logger] = None,
        session: Optional[TelegramSession] = None,
        code_callback: Optional[Callable[[], asyncio.Future[str]]] = None,
        twofa_password_callback: Optional[Callable[[], asyncio.Future[str]]] = None,
    ):
        if not assistant.llm:
            raise ValueError("Assistant must have an LLM")

        if not isinstance(assistant.llm, OpenAIChat):
            raise ValueError("Assistant must use OpenAI LLM")

        self.assistant = assistant
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.session = session or TelegramSession(
            self.config,
            code_callback=code_callback,
            twofa_password_callback=twofa_password_callback,
            logger=self.logger,
        )
        self.embeddings = OpenAIEmbeddings(api_key=assistant.llm.api_key)
        self.text_splitter = SemanticChunker(embeddings=self.embeddings)

        self.inbound = InboundMessaging(
            self.session,
            self.config,
            logger=self.logger,
            text_splitter=self.text_splitter,
        )
        self.outbound = OutboundMessaging(
            self.session,
            self.config,
            logger=self.logger,
            text_splitter=self.text_splitter,
        )
        self.tools = TelegramTools(self.session, logger=self.logger)

    async def start(self):
        try:
            if not self.session.is_connected():
                self.logger.info("Starting Telegram AI Agent...")
                await self.session.start()

                self.logger.info(
                    "Successfully started and authorized the Telegram AI Agent."
                )
        except Exception as e:
            self.logger.error(f"An error occurred while starting the agent: {e}")
            raise

    async def stop(self):
        self.logger.info("Stopping Telegram AI Agent...")
        if self.session:
            await self.session.stop()
        self.logger.info("Telegram AI Agent stopped.")

    async def send_messages(self, recipients, message, throttle=0):
        await self.outbound.send_messages(recipients, message, throttle)

    async def process_incoming_messages(self):
        await self.inbound.process_messages(self.assistant)

    async def run(self):
        await self.start()
        await self.process_incoming_messages()
        if self.session:
            await self.session.run_until_disconnected()
