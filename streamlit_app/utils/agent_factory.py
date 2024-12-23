import asyncio

from pathlib import Path
from typing import Callable, Optional

from streamlit_app.utils.assistant_factory import create_phi_assistant
from streamlit_app.utils.auth_utils import try_auth
from telegram_ai_agent import TelegramAIAgent, TelegramConfig


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

    # Create proxy dict if proxy settings are provided
    proxy = None
    if (
        assistant_data.proxy_type
        and assistant_data.proxy_addr
        and assistant_data.proxy_port
    ):
        proxy = {
            "proxy_type": assistant_data.proxy_type,
            "addr": assistant_data.proxy_addr,
            "port": assistant_data.proxy_port,
            "rdns": assistant_data.proxy_rdns,
        }

        # Add authentication if provided
        if assistant_data.proxy_username and assistant_data.proxy_password:
            proxy["username"] = assistant_data.proxy_username
            proxy["password"] = assistant_data.proxy_password

    # Create TelegramConfig instance with all advanced settings
    telegram_config = TelegramConfig(
        session_name=session_name or assistant_data.telegram_config.session_file,
        api_id=assistant_data.telegram_config.api_id,
        api_hash=assistant_data.telegram_config.api_hash,
        phone_number=assistant_data.telegram_config.phone_number,
        proxy=proxy,
        # Add all advanced settings from the Assistant model
        timeout=assistant_data.timeout,
        set_typing=assistant_data.set_typing,
        typing_delay_factor=assistant_data.typing_delay_factor,
        typing_delay_max=assistant_data.typing_delay_max,
        inter_chunk_delay_min=assistant_data.inter_chunk_delay_min,
        inter_chunk_delay_max=assistant_data.inter_chunk_delay_max,
        min_messages=assistant_data.min_messages,
        max_messages=assistant_data.max_messages,
        min_typing_speed=assistant_data.min_typing_speed,
        max_typing_speed=assistant_data.max_typing_speed,
        min_burst_length=assistant_data.min_burst_length,
        max_burst_length=assistant_data.max_burst_length,
        min_pause_duration=assistant_data.min_pause_duration,
        max_pause_duration=assistant_data.max_pause_duration,
        read_delay_factor=assistant_data.read_delay_factor,
        min_read_delay=assistant_data.min_read_delay,
        max_read_delay=assistant_data.max_read_delay,
        chat_history_limit=assistant_data.chat_history_limit,
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
