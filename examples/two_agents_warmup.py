import asyncio
import logging
import os
import random

from datetime import datetime, timedelta

from dotenv import load_dotenv
from phi.assistant.assistant import Assistant
from phi.llm.openai.chat import OpenAIChat

from telegram_ai_agent import TelegramAIAgent, TelegramConfig
from telegram_ai_agent.utils import setup_logging


# Load environment variables and setup logging
load_dotenv()
setup_logging()
logger = logging.getLogger(__name__)

# Load environment variables
API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
API_HASH = os.getenv("TELEGRAM_API_HASH", "")
PHONE_NUMBER_1 = os.getenv("TELEGRAM_PHONE_NUMBER_1", "")
PHONE_NUMBER_2 = os.getenv("TELEGRAM_PHONE_NUMBER_2", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Create OpenAI assistants with different personalities
openai_chat = OpenAIChat(api_key=OPENAI_API_KEY)
assistant1 = Assistant(
    llm=openai_chat,
    run_id="agent1",
    description="You are a curious and friendly AI assistant named Alex.",
)
assistant2 = Assistant(
    llm=openai_chat,
    run_id="agent2",
    description="You are a knowledgeable and slightly sarcastic AI assistant named Sam.",
)

# Create Telegram configurations
config1 = TelegramConfig(
    session_name="agent1_session",
    api_id=API_ID,
    api_hash=API_HASH,
    phone_number=PHONE_NUMBER_1,
)
config2 = TelegramConfig(
    session_name="agent2_session",
    api_id=API_ID,
    api_hash=API_HASH,
    phone_number=PHONE_NUMBER_2,
)


async def simulate_conversation(agent1, agent2, topic, turns=3):
    agents = [agent1, agent2]
    current_agent = random.choice(agents)
    other_agent = agent2 if current_agent == agent1 else agent1

    context = f"Start a conversation about {topic}. Be concise in your responses."

    for _ in range(turns):
        # Generate and send a message
        message = current_agent.assistant.run(
            messages=[{"role": "user", "content": context}]
        )
        logger.info(f"{current_agent.config.session_name} says: {message}")
        await current_agent.send_messages([other_agent.config.phone_number], message)

        # Wait for the message to be processed
        await asyncio.sleep(2)

        # Generate a response
        context = f"Respond to this message: '{message}'. Keep the conversation going about {topic}."
        response = other_agent.assistant.run(
            messages=[{"role": "user", "content": context}]
        )
        logger.info(f"{other_agent.config.session_name} responds: {response}")
        await other_agent.send_messages([current_agent.config.phone_number], response)

        # Wait for the response to be processed
        await asyncio.sleep(2)

        # Switch roles for the next turn
        current_agent, other_agent = other_agent, current_agent
        context = (
            f"Continue the conversation about {topic} based on the previous message."
        )


async def warmup_agents(agent1, agent2):
    start_date = datetime.now()
    end_date = start_date + timedelta(weeks=3)
    current_date = start_date

    topics = [
        "the importance of AI ethics",
        "the future of space exploration",
        "the impact of social media on society",
        "climate change and sustainable technologies",
        "the role of art in the digital age",
    ]

    while current_date < end_date:
        logger.info(f"Starting conversation on {current_date}")
        topic = random.choice(topics)
        await simulate_conversation(agent1, agent2, topic)

        # Generate a random number of hours between 2 and 12
        hours_until_next = random.randint(2, 12)
        current_date += timedelta(hours=hours_until_next)

        logger.info(f"Next conversation in {hours_until_next} hours")

        # Calculate sleep time in seconds, capped at 1 hour real time
        sleep_time = min(hours_until_next * 60, 3600)
        await asyncio.sleep(sleep_time)


async def get_code():
    return input("Enter the code you received: ")


async def get_password():
    return input("Enter your password: ")


async def main():
    try:
        # Create and start the Telegram AI Agents
        agent1 = TelegramAIAgent(
            assistant1,
            config1,
            logger=logger,
            code_callback=get_code,
            twofa_password_callback=get_password,
        )
        agent2 = TelegramAIAgent(
            assistant2,
            config2,
            logger=logger,
            code_callback=get_code,
            twofa_password_callback=get_password,
        )

        await agent1.start()
        await agent2.start()

        # Run the warmup process
        await warmup_agents(agent1, agent2)

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
    finally:
        if agent1.session:
            await agent1.stop()
        if agent2.session:
            await agent2.stop()


if __name__ == "__main__":
    asyncio.run(main())
