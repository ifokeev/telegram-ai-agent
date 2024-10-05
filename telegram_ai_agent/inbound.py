import asyncio
import random
from typing import List, Dict, Any
from telethon import events
from phi.assistant.assistant import Assistant
from .messages_handler import MessagesHandler


class InboundMessaging(MessagesHandler):
    async def get_chat_history(self, user_id: int) -> List[Dict[str, Any]]:
        messages = []
        async for message in self.session.iter_messages(
            user_id, limit=self.config.chat_history_limit
        ):
            role = "user" if message.out else "assistant"
            messages.append({"role": role, "content": message.text})
        return messages[::-1]  # Reverse to get chronological order

    async def process_messages(self, assistant: Assistant):
        @self.session.on(events.NewMessage(incoming=True))
        async def handle_new_message(event):
            try:
                sender = await event.get_sender()
                user_id = sender.id

                self.logger.info(f"Received from {sender.username}: {event.text}")

                read_delay = len(
                    event.text
                ) * self.config.read_delay_factor + random.uniform(
                    self.config.min_read_delay, self.config.max_read_delay
                )
                await asyncio.sleep(read_delay)
                await self.session.send_read_acknowledge(sender, event.message)

                chat_history = await self.get_chat_history(user_id)
                messages = [*chat_history, {"role": "user", "content": event.text}]
                response = assistant.run(messages=messages, stream=False)

                first_message = True
                async for message in self.simulate_conversation(str(response), sender):
                    if first_message:
                        await event.reply(message)
                        first_message = False
                    else:
                        await self.session.send_message(sender, message)

                self.logger.info(f"Sent to {sender.username}: {response}")
            except Exception as e:
                self.logger.error(f"Error processing message: {str(e)}")

        self.logger.info("Started processing incoming messages")
