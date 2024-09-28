import asyncio
import random
from telethon import TelegramClient
from telethon.tl.functions.messages import SetTypingRequest
from telethon.tl.types import SendMessageTypingAction
from langchain_experimental.text_splitter import SemanticChunker
from langchain.embeddings import OpenAIEmbeddings
from typing import List, AsyncGenerator
from .config import TelegramConfig


class MessagesHandler:
    def __init__(self, client: TelegramClient, config: TelegramConfig):
        self.client = client
        self.config = config
        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = SemanticChunker(embeddings=self.embeddings)

    def balance_chunks(self, text: str) -> List[str]:
        chunks = self.text_splitter.split_text(text)
        target_messages = random.randint(
            self.config.min_messages, min(self.config.max_messages, len(chunks))
        )

        while len(chunks) > target_messages:
            shortest = min(range(len(chunks)), key=lambda i: len(chunks[i]))
            if shortest > 0:
                chunks[shortest - 1] += " " + chunks.pop(shortest)
            else:
                chunks[shortest] += " " + chunks.pop(shortest + 1)

        return chunks

    async def simulate_typing(self, text: str, user):
        avg_typing_speed = random.uniform(
            self.config.min_typing_speed, self.config.max_typing_speed
        )
        words = text.split()
        total_words = len(words)
        words_typed = 0

        while words_typed < total_words:
            burst_length = min(
                random.randint(
                    self.config.min_burst_length, self.config.max_burst_length
                ),
                total_words - words_typed,
            )

            await self.client(
                SetTypingRequest(peer=user, action=SendMessageTypingAction())
            )

            for _ in range(burst_length):
                word = words[words_typed]
                word_length = len(word)
                base_delay = (60 / avg_typing_speed) * (word_length / 5)
                variation = random.uniform(-0.1, 0.1)
                typing_delay = base_delay * (1 + variation)
                await asyncio.sleep(typing_delay)
                words_typed += 1

            if words_typed < total_words:
                pause_duration = random.uniform(
                    self.config.min_pause_duration, self.config.max_pause_duration
                )
                await asyncio.sleep(pause_duration)

    async def simulate_conversation(self, text: str, user) -> AsyncGenerator[str, None]:
        chunks = self.balance_chunks(text)

        for chunk in chunks:
            if self.config.set_typing:
                await self.simulate_typing(chunk, user)

            yield chunk

            think_time = random.uniform(
                self.config.inter_chunk_delay_min, self.config.inter_chunk_delay_max
            )
            await asyncio.sleep(think_time)
