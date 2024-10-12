import streamlit as st
import asyncio
from telegram_ai_agent.session import TelegramSession
from telegram_ai_agent import TelegramConfig


async def try_auth(config: TelegramConfig, logger, stop_session=False):
    auth_placeholder = st.empty()

    async def code_callback():
        return st.text_input("Enter the authentication code:")

    async def password_callback():
        return st.text_input("Enter the 2FA password:", type="password")

    session = TelegramSession(
        config,
        code_callback=code_callback,
        twofa_password_callback=password_callback,
        logger=logger,
    )
    try:
        if not session.is_connected():
            with auth_placeholder.container():
                st.write("Connecting to Telegram...")
            await session.start()
            with auth_placeholder.container():
                st.success(f"Successfully authorized for {config.phone_number}")
            return True, session
        else:
            with auth_placeholder.container():
                st.success(f"Already authorized for {config.phone_number}")
            return True, session
    except Exception as e:
        with auth_placeholder.container():
            st.error(f"Authorization failed: {str(e)}")
        return False, None
    finally:
        if stop_session:
            await session.stop()


def authorize(config: TelegramConfig, logger, stop_session=False):
    return asyncio.run(try_auth(config, logger, stop_session))
