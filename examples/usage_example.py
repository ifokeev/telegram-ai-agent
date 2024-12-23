import asyncio
import logging
import os

from dotenv import load_dotenv
from phi.assistant.assistant import Assistant
from phi.llm.openai.chat import OpenAIChat

from telegram_ai_agent import TelegramAIAgent, TelegramConfig
from telegram_ai_agent.utils import setup_logging


# Load environment variables and setup logging
load_dotenv()
setup_logging()
logger = logging.getLogger(__name__)


def load_proxy_config():
    """Load proxy configuration from environment variables"""
    if not all(
        [os.getenv("PROXY_TYPE"), os.getenv("PROXY_ADDR"), os.getenv("PROXY_PORT")]
    ):
        return None

    proxy = {
        "proxy_type": os.getenv("PROXY_TYPE"),  # socks5, socks4, or http
        "addr": os.getenv("PROXY_ADDR"),
        "port": int(os.getenv("PROXY_PORT")),
        "rdns": os.getenv("PROXY_RDNS", "true").lower() == "true",
    }

    # Add authentication if provided
    if os.getenv("PROXY_USERNAME") and os.getenv("PROXY_PASSWORD"):
        proxy.update(
            {
                "username": os.getenv("PROXY_USERNAME"),
                "password": os.getenv("PROXY_PASSWORD"),
            }
        )

    return proxy


def load_advanced_config():
    """Load advanced configuration from environment variables"""
    return {
        "timeout": int(os.getenv("TELEGRAM_TIMEOUT", "30")),
        "set_typing": os.getenv("SET_TYPING", "true").lower() == "true",
        "typing_delay_factor": float(os.getenv("TYPING_DELAY_FACTOR", "0.05")),
        "typing_delay_max": float(os.getenv("TYPING_DELAY_MAX", "30.0")),
        "min_typing_speed": float(os.getenv("MIN_TYPING_SPEED", "100.0")),
        "max_typing_speed": float(os.getenv("MAX_TYPING_SPEED", "200.0")),
        "chat_history_limit": int(os.getenv("CHAT_HISTORY_LIMIT", "100")),
    }


async def get_code():
    return input("Enter the code you received: ")


async def get_password():
    return input("Enter your 2FA password: ")


async def main():
    # Create OpenAI assistant
    openai_chat = OpenAIChat(api_key=os.getenv("OPENAI_API_KEY"))
    assistant = Assistant(
        llm=openai_chat,
        run_id="telegram_ai_agent",
        description="Sales representative for a tech company",
        instructions=[
            "You are a sales representative for a tech company.",
            "You are tasked with selling a product to the user.",
        ],
    )

    # Load configurations
    proxy_config = load_proxy_config()
    advanced_config = load_advanced_config()

    # Create Telegram configuration
    telegram_config = TelegramConfig(
        session_name="example_session",
        api_id=int(os.getenv("TELEGRAM_API_ID")),
        api_hash=os.getenv("TELEGRAM_API_HASH"),
        phone_number=os.getenv("TELEGRAM_PHONE_NUMBER"),
        proxy=proxy_config,
        **advanced_config,
    )

    try:
        # Create and start the Telegram AI Agent
        agent = TelegramAIAgent(
            assistant,
            telegram_config,
            logger=logger,
            code_callback=get_code,
            twofa_password_callback=get_password,
        )
        # Run agent inbound processing until disconnected
        await agent.run()
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
    finally:
        if agent.session:
            await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
