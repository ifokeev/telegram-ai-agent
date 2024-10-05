import asyncio
import logging
import os
import json
import httpx
from dotenv import load_dotenv
from telegram_ai_agent import TelegramAIAgent, TelegramConfig
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
TEST_RECIPIENT = os.getenv("TEST_RECIPIENT", "@user1")


# Define tool functions
def get_weather(location: str) -> str:
    """Get the current weather for a specific location.

    Args:
        location (str): The city and country.

    Returns:
        str: Weather information for the specified location.
    """
    # This is a mock implementation. In a real scenario, you'd use a weather API.
    return f"The weather in {location} is sunny with a temperature of 25°C."


def get_news(category: str) -> str:
    """Get the latest news headlines for a specific category.

    Args:
        category (str): The news category (e.g., technology, sports, business).

    Returns:
        str: Latest news headline for the specified category.
    """
    # This is a mock implementation. In a real scenario, you'd use a news API.
    return f"Latest {category} news: New breakthrough in AI technology announced."


def get_top_hackernews_stories(num_stories: int = 5) -> str:
    """Get top stories from Hacker News.

    Args:
        num_stories (int): Number of stories to return. Defaults to 5.

    Returns:
        str: JSON string of top stories.
    """
    response = httpx.get("https://hacker-news.firebaseio.com/v0/topstories.json")
    story_ids = response.json()

    stories = []
    for story_id in story_ids[:num_stories]:
        story_response = httpx.get(
            f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
        )
        story = story_response.json()
        if "text" in story:
            story.pop("text", None)
        stories.append(story)
    return json.dumps(stories)


# Create OpenAI assistant with function tools
openai_chat = OpenAIChat(api_key=OPENAI_API_KEY)
assistant = Assistant(
    llm=openai_chat,
    description="This assistant can help you with weather information, news updates, and top Hacker News stories.",
    instructions=[
        "Answer the user's question as best as you can.",
        "If you don't know the answer, say so and ask the user to clarify.",
        "If the user asks for a specific tool, provide it.",
        "If the user asks for information, provide it.",
        "If the user asks for help, provide it.",
        "Don't be verbose. Be concise.",
        "Don't say 'As an AI assistant'.",
        "Don't say 'You asked me to help with that'.",
        "Don't say 'I'm sorry, I can't help with that'.",
        "Don't say 'I'm sorry, I'm not sure how to help with that'.",
        "Don't say 'I'm sorry, I'm not sure what you mean'.",
        "Your answers should be short and to the point. Maximum 100 words.",
    ],
    run_id="telegram_function_calling_assistant",  # Add this line
    tools=[get_weather, get_news, get_top_hackernews_stories],
    add_datetime_to_instructions=True,
    show_tool_calls=True,
    use_tools=True,
)

# Create Telegram configuration
telegram_config = TelegramConfig(
    session_name="function_calling_session",
    api_id=API_ID,
    api_hash=API_HASH,
    phone_number=PHONE_NUMBER,
)


async def main():
    try:
        # Create and start the Telegram AI Agent
        agent = TelegramAIAgent(assistant, telegram_config, logger=logger)
        await agent.start()

        # Example: Send a message
        await agent.send_messages(
            [TEST_RECIPIENT],
            "Hello! I'm ready to assist you with weather information, news updates, and top Hacker News stories.",
        )

        # Process incoming messages
        await agent.process_incoming_messages()

        # Run the agent until disconnected
        await agent.session.run_until_disconnected()  # type: ignore
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
    finally:
        if agent.session:
            await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
