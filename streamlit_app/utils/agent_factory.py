from telegram_ai_agent import TelegramAIAgent, TelegramConfig
from streamlit_app.utils.assistant_factory import create_phi_assistant
from streamlit_app.utils.database.telegram_config import get_telegram_config_by_id


async def create_telegram_ai_agent(assistant_data, logger=None):
    """
    Factory method to create a TelegramAIAgent instance from assistant_data.

    Args:
        assistant_data: An object containing assistant attributes.
        logger (optional): A logger instance.

    Returns:
        TelegramAIAgent: An instance of the Telegram AI Agent.
    """
    # Create the phi_assistant using the factory method
    phi_assistant = create_phi_assistant(assistant_data)

    # Get Telegram configuration data
    telegram_config_data = get_telegram_config_by_id(assistant_data.telegram_config_id)

    # Create TelegramConfig instance
    telegram_config = TelegramConfig(
        session_name=telegram_config_data.session_file,
        api_id=telegram_config_data.api_id,
        api_hash=telegram_config_data.api_hash,
        phone_number=telegram_config_data.phone_number,
    )

    # Create the Telegram AI Agent
    agent = TelegramAIAgent(phi_assistant, telegram_config, logger=logger)
    return agent
