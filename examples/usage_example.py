import asyncio
import logging
import os
from dotenv import load_dotenv
from telegram_ai_agent import TelegramAIAgent, TelegramConfig
from telegram_ai_agent.utils import setup_logging
from phi.assistant.assistant import Assistant
from phi.llm.openai.chat import OpenAIChat

# Load environment variables from .env file
load_dotenv()

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Load environment variables
API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
API_HASH = os.getenv("TELEGRAM_API_HASH", "")
PHONE_NUMBER = os.getenv("TELEGRAM_PHONE_NUMBER", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
TEST_RECIPIENT = os.getenv("TEST_RECIPIENT", "@user1")

# Optional: Load proxy settings if provided
PROXY = None
if (
    os.getenv("PROXY_SCHEME")
    and os.getenv("PROXY_HOSTNAME")
    and os.getenv("PROXY_PORT")
):
    PROXY = {
        "scheme": os.getenv("PROXY_SCHEME"),
        "hostname": os.getenv("PROXY_HOSTNAME"),
        "port": int(os.getenv("PROXY_PORT")),
    }

# Optional: Load custom timeout if provided
TIMEOUT = int(os.getenv("TELEGRAM_TIMEOUT", 30))

# Create OpenAI assistant
openai_chat = OpenAIChat(api_key=OPENAI_API_KEY)
assistant = Assistant(llm=openai_chat, run_id="telegram_ai_agent")

# Create Telegram configuration
telegram_config = TelegramConfig(
    session_name="session_1",
    api_id=API_ID,
    api_hash=API_HASH,
    phone_number=PHONE_NUMBER,
    proxy=PROXY,
    timeout=TIMEOUT,
)


async def get_code():
    return input("Enter the code you received: ")


async def get_password():
    return input("Enter your password: ")


async def main():
    try:
        # Create and start the Telegram AI Agent
        agent = TelegramAIAgent(
            assistant,
            telegram_config,
            logger=logger,
            code_callback=get_code,
            twofa_password_callback=get_password,
        )
        await agent.start()

        # Example: Send a message
        await agent.send_messages([TEST_RECIPIENT], "Hello from the Telegram AI Agent!")

        # Process incoming messages
        await agent.process_incoming_messages()

        # Run the agent until disconnected
        await agent.session.run_until_disconnected()
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
    finally:
        if agent.session:
            await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
