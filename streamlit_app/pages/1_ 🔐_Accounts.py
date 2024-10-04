import streamlit as st
import asyncio
from pathlib import Path
from telegram_ai_agent import TelegramConfig
from telegram_ai_agent.session import TelegramSession
from streamlit_app.utils.database import (
    save_telegram_config,
    get_all_telegram_configs,
    delete_telegram_config,
)
from streamlit_app.utils.logging_utils import setup_logger

logger = setup_logger(__name__)

current_dir = Path(__file__).parents[1].resolve()
SESSIONS_FOLDER = current_dir / "sessions"

st.set_page_config(page_title="Manage Accounts", page_icon="🔐")

st.markdown("# Manage Telegram Accounts")

tab1, tab2 = st.tabs(["Add Account", "Manage Accounts"])

with tab1:
    st.header("Add New Account")
    phone_number = st.text_input("Phone Number")
    api_id = st.text_input("API ID")
    api_hash = st.text_input("API Hash", type="password")

    if st.button("Authorize"):
        SESSIONS_FOLDER.mkdir(parents=True, exist_ok=True)
        session_path = SESSIONS_FOLDER / f"session_{phone_number}"

        config = TelegramConfig(
            session_name=str(session_path),
            api_id=int(api_id),
            api_hash=api_hash,
            phone_number=phone_number,
        )

        async def authorize():
            session = TelegramSession(config, logger=logger)
            try:
                await session.start()
                save_telegram_config(phone_number, api_id, api_hash, str(session_path))
                logger.info(f"Telegram user '{phone_number}' authorized successfully!")
                st.success(f"Telegram user '{phone_number}' authorized successfully!")
            except Exception as e:
                logger.error(f"Error during authorization: {str(e)}")
                st.error(f"An error occurred: {str(e)}")
            finally:
                await session.stop()

        asyncio.run(authorize())

with tab2:
    st.header("Manage Existing Accounts")
    accounts = get_all_telegram_configs()
    for account in accounts:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"Phone: {account.phone_number}")
        with col2:
            if st.button("Delete", key=f"delete_{account.phone_number}"):
                delete_telegram_config(account.phone_number)
                st.rerun()
