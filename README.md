# Telegram AI Agent Library

This Python library provides a framework for creating AI-powered Telegram bots using the Telegram Core API and the [phi](https://github.com/phidatahq/phidata) library for AI integration.

## Features

- Secure authentication with Telegram servers
- Inbound message processing with AI integration using [phi](https://github.com/phidatahq/phidata)
- Outbound messaging capabilities
- Chat history support for context-aware responses
- Configurable proxy and timeout settings
- Asynchronous operations using asyncio
- Typing indicators for a more natural conversation flow
- Function calling for AI-powered tools
- Customizable logging
- Streamlit UI for easy interaction with the agent

## Installation

To install the library, follow these steps:

1. Clone the repository:
   ```sh
   git clone https://github.com/ifokeev/telegram-ai-agent.git
   cd telegram-ai-agent
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```sh
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   ```

3. Install the package in editable mode:
   ```sh
   pip install -e .
   ```

This will install the library and its dependencies, allowing you to use it in your projects and make changes to the source code if needed.

Note: Make sure you have Python 3.11 or higher installed on your system before proceeding with the installation.

## Streamlit UI

To run the Streamlit UI, run the following command:

```sh
streamlit run streamlit_app/Home.py
```

and navigate to `http://localhost:8501` in your web browser.

## Configuration

To configure the Telegram AI Agent library, you need to set up environment variables. You can do this by either creating a `.env` file or copying from the provided `.env.example` file.

### Option 1: Create a new .env file


Create a `.env` file in the root directory of your project with the following content:

```
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here
TELEGRAM_PHONE_NUMBER=your_phone_number_here
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Proxy settings
# PROXY_SCHEME=socks5
# PROXY_HOSTNAME=localhost
# PROXY_PORT=9150

# Optional: Custom timeout (in seconds)
# TELEGRAM_TIMEOUT=60
```

Replace the placeholder values with your actual Telegram API credentials and OpenAI API key.

### Option 2: Copy from .env.example

If you prefer not to create a new file, you can copy the `.env.example` file to `.env` and modify the values as needed.

## Usage

Here's a basic example of how to use the Telegram AI Agent:

```python
import asyncio
import logging
from dotenv import load_dotenv
import os
from telegram_ai_agent import TelegramAIAgent, TelegramConfig
from telegram_ai_agent.utils import setup_logging
from phi.assistant.assistant import Assistant
from phi.llm.openai.chat import OpenAIChat

# Load environment variables and setup logging
load_dotenv()
setup_logging()
logger = logging.getLogger(__name__)

# Create OpenAI assistant
openai_chat = OpenAIChat(api_key=os.getenv("OPENAI_API_KEY"))
assistant = Assistant(
    llm=openai_chat,
    run_id="telegram_ai_agent",
    description="Sales representative for a tech company",
    instructions=["You are a sales representative for a tech company. You are tasked with selling a product to the user."]
)

# Create Telegram configuration
telegram_config = TelegramConfig(
    session_name="session_1",
    api_id=int(os.getenv("TELEGRAM_API_ID")),
    api_hash=os.getenv("TELEGRAM_API_HASH"),
    phone_number=os.getenv("TELEGRAM_PHONE_NUMBER"),
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
        # Run agent inbound processing until disconnected
        await agent.run()
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
    finally:
        if agent.session:
            await agent.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

For more detailed examples, check the `examples` directory.

## Testing

This project uses pytest for unit testing. To run the tests, first install the development dependencies:

```sh
pip install -e .[dev]
```

Then, you can run the tests using:

```sh
pytest tests/
```

The test suite includes unit tests for the `TelegramAIAgent` class, covering initialization, starting, stopping, sending messages, and processing incoming messages.

To add new tests or modify existing ones, check the `tests/test_agent.py` file.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.