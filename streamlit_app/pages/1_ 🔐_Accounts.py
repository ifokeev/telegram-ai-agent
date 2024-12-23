from pathlib import Path

import streamlit as st

from streamlit_app.utils.auth_utils import authorize
from streamlit_app.utils.database.telegram_config import (
    delete_telegram_config,
    get_all_telegram_configs,
    save_telegram_config,
)
from streamlit_app.utils.logging_utils import setup_logger
from telegram_ai_agent import TelegramConfig


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

        auth_success, _ = authorize(config, logger)

        if auth_success:
            save_telegram_config(phone_number, api_id, api_hash, str(session_path))
            logger.info(f"Telegram user '{phone_number}' authorized successfully!")

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
