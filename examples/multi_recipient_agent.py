import asyncio
import logging
import os
from dotenv import load_dotenv
from telegram_ai_agent import TelegramAIAgent, TelegramConfig
from telegram_ai_agent.utils import setup_logging
from phi.assistant.assistant import Assistant
from phi.llm.openai.chat import OpenAIChat
import threading

# Load environment variables and setup logging
load_dotenv()
setup_logging()
logger = logging.getLogger(__name__)

# Load environment variables
API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
API_HASH = os.getenv("TELEGRAM_API_HASH", "")
PHONE_NUMBER = os.getenv("TELEGRAM_PHONE_NUMBER", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# List of recipient usernames or phone numbers
RECIPIENTS = [
    "@user1",
    "@user2",
    "@user3",
    "@user4",
    "@user5",
    "@user6",
    "@user7",
    "@user8",
    "@user9",
    "@user10",
]

# Create OpenAI assistant
openai_chat = OpenAIChat(api_key=OPENAI_API_KEY)
assistant = Assistant(
    llm=openai_chat,
    run_id="multi_recipient_agent",
    description="You are a helpful AI assistant for multiple Telegram users.",
)

# Create Telegram configuration
telegram_config = TelegramConfig(
    session_name="multi_recipient_session",
    api_id=API_ID,
    api_hash=API_HASH,
    phone_number=PHONE_NUMBER,
)


async def send_messages(agent):
    welcome_prompt = (
        "Generate a unique and friendly welcome message for a new user joining "
        "an AI-powered chat. Introduce yourself as an AI assistant and encourage "
        "them to ask questions or discuss any topics they're interested in. "
        "Keep the message concise but engaging."
    )

    follow_up_prompts = [
        "Create a message that highlights your ability to answer questions on various topics.",
        "Craft an engaging message that encourages the user to ask you anything.",
    ]

    for recipient in RECIPIENTS:
        try:
            # Generate and send a unique welcome message
            unique_welcome = agent.assistant.run(
                messages=[{"role": "user", "content": welcome_prompt}]
            )
            await agent.send_messages([recipient], unique_welcome, throttle=1)
            logger.info(f"Sent unique welcome message to {recipient}: {unique_welcome}")

            # Generate and send follow-up messages
            for prompt in follow_up_prompts:
                unique_message = agent.assistant.run(
                    messages=[{"role": "user", "content": prompt}]
                )
                await agent.send_messages([recipient], unique_message, throttle=1)
                logger.info(f"Sent unique message to {recipient}: {unique_message}")

            await asyncio.sleep(5)  # Wait 5 seconds between recipients
        except Exception as e:
            logger.error(f"Error sending messages to {recipient}: {str(e)}")


async def listen_for_messages(agent):
    try:
        await agent.process_incoming_messages()
    except Exception as e:
        logger.error(f"Error processing incoming messages: {str(e)}")


def run_listen_thread(agent):
    asyncio.run(listen_for_messages(agent))


async def get_code():
    return input("Enter the code you received: ")


async def get_password():
    return input("Enter your password: ")


async def main():
    agent = None
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

        # Start listening for incoming messages in a separate thread
        listen_thread = threading.Thread(target=run_listen_thread, args=(agent,))
        listen_thread.start()

        # Send messages to recipients
        await send_messages(agent)

        # Keep the main thread running
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt. Stopping the agent...")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
    finally:
        if agent and agent.session:
            await agent.stop()
        if "listen_thread" in locals() and listen_thread.is_alive():
            listen_thread.join(timeout=5)


if __name__ == "__main__":
    asyncio.run(main())
