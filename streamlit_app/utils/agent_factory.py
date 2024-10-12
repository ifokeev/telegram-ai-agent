from telegram_ai_agent import TelegramAIAgent, TelegramConfig
from streamlit_app.utils.assistant_factory import create_phi_assistant
from typing import Optional, Callable
import asyncio
from pathlib import Path
from streamlit_app.utils.auth_utils import try_auth

current_dir = Path(__file__).parents[1].resolve()
SESSIONS_FOLDER = current_dir / "sessions"


async def create_telegram_ai_agent(
    assistant_data,
    logger=None,
    session_name: Optional[str] = None,
    code_callback: Optional[Callable[[], asyncio.Future[str]]] = None,
    twofa_password_callback: Optional[Callable[[], asyncio.Future[str]]] = None,
):
    """
    Factory method to create a TelegramAIAgent instance from assistant_data.

    Args:
        assistant_data: An object containing assistant attributes.
        logger (optional): A logger instance.
        session_name (optional): Name for the session.
        code_callback (optional): Callback function for getting authentication code.
        twofa_password_callback (optional): Callback function for getting 2FA password.

    Returns:
        TelegramAIAgent: An instance of the Telegram AI Agent.
    """
    if not assistant_data:
        raise ValueError("Assistant data is required")

    if not assistant_data.telegram_config:
        raise ValueError("Telegram config is required")

    # Create the phi_assistant using the factory method
    phi_assistant = create_phi_assistant(assistant_data)

    # Create TelegramConfig instance
    telegram_config = TelegramConfig(
        session_name=session_name or assistant_data.telegram_config.session_file,
        api_id=assistant_data.telegram_config.api_id,
        api_hash=assistant_data.telegram_config.api_hash,
        phone_number=assistant_data.telegram_config.phone_number,
    )

    auth_success, session = await try_auth(telegram_config, logger)

    if not auth_success or session is None:
        raise ValueError("Failed to authorize. Please try again.")

    # Create the Telegram AI Agent
    agent = TelegramAIAgent(
        phi_assistant,
        telegram_config,
        logger=logger,
        session=session,
        code_callback=code_callback,
        twofa_password_callback=twofa_password_callback,
    )
    return agent
