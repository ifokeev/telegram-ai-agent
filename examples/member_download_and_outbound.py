import asyncio
import logging
import os
import json
from dotenv import load_dotenv
from telegram_ai_agent import TelegramAIAgent, TelegramConfig
from telegram_ai_agent.session import TelegramClient
from telegram_ai_agent.utils import setup_logging
from phi.assistant.assistant import Assistant
from phi.llm.openai.chat import OpenAIChat


# Load environment variables and setup logging
load_dotenv()
setup_logging()
logger = logging.getLogger(__name__)

# Load environment variables
API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
API_HASH = os.getenv("TELEGRAM_API_HASH", "")
PHONE_NUMBER = os.getenv("TELEGRAM_PHONE_NUMBER", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
CHAT_NAME = os.getenv(
    "CHAT_NAME", ""
)  # Name of the chat/channel to download members from

# File to store member list
MEMBERS_FILE = "chat_members.json"


async def get_chat_members(client, chat_name):
    if os.path.exists(MEMBERS_FILE):
        with open(MEMBERS_FILE, "r") as f:
            return json.load(f)

    logger.info(f"Downloading members from {chat_name}")
    members = await client.get_chat_members(chat_name, MEMBERS_FILE)
    return members


# Create OpenAI assistant
openai_chat = OpenAIChat(api_key=OPENAI_API_KEY)
assistant = Assistant(
    llm=openai_chat,
    run_id="telegram_member_outbound",
    description="You are a helpful AI assistant for Telegram users.",
    instructions=[
        "Rephrase the given message in a unique way for each user.",
        "Keep the core meaning of the message intact.",
        "Vary the tone and style slightly for each rephrasing.",
        "Keep the rephrased message concise, ideally under 50 words.",
    ],
)

# Create Telegram configuration
telegram_config = TelegramConfig(
    session_name="member_download_session",
    api_id=API_ID,
    api_hash=API_HASH,
    phone_number=PHONE_NUMBER,
)


async def generate_unique_message(assistant, default_message):
    response = assistant.chat(
        messages=[
            {
                "role": "system",
                "content": "Rephrase the following message in a unique way:",
            },
            {"role": "user", "content": default_message},
        ]
    )
    return response.content


async def main():
    try:
        # Create and start the Telegram AI Agent
        agent = TelegramAIAgent(assistant, telegram_config, logger=logger)
        await agent.start()

        # Download members
        members = await get_chat_members(agent.client, CHAT_NAME)

        # Prepare default message for outbound sending
        default_message = "Hello! This is a test message from our AI assistant. We're excited to connect with you and share updates about our services."

        # Send message to all members
        for member in members:
            try:
                # Generate a unique message for each user
                unique_message = await generate_unique_message(
                    assistant, default_message
                )

                if member["username"]:
                    await agent.send_messages([member["username"]], unique_message)
                    logger.info(f"Sent unique message to @{member['username']}")
                else:
                    # If no username, use the user's ID
                    await agent.send_messages([member["id"]], unique_message)
                    logger.info(f"Sent unique message to user ID: {member['id']}")

                # Add a delay to avoid flooding
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(
                    f"Failed to send message to {member.get('username', member['id'])}: {str(e)}"
                )

        logger.info("Finished sending unique messages to all members")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
    finally:
        if agent.client:
            await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
