import streamlit as st
import asyncio
from telegram_ai_agent.session import TelegramSession
from telegram_ai_agent import TelegramConfig


def authorize(config: TelegramConfig, logger):
    code_placeholder = st.empty()
    password_placeholder = st.empty()

    async def try_auth():
        async def code_callback():
            return code_placeholder.text_input("Enter the authentication code:")

        async def password_callback():
            return password_placeholder.text_input(
                "Enter the 2FA password:", type="password"
            )

        session = TelegramSession(
            config,
            code_callback=code_callback,
            twofa_password_callback=password_callback,
            logger=logger,
        )
        try:
            st.write("Connecting to Telegram...")
            await session.start()
            st.success(f"Successfully authorized for {config.phone_number}")
            return True, session
        except Exception as e:
            st.error(f"Authorization failed: {str(e)}")
            return False, None

    return asyncio.run(try_auth())
