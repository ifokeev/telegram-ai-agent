import asyncio

from pathlib import Path

import pandas as pd
import streamlit as st

from streamlit_app.utils.auth_utils import try_auth
from streamlit_app.utils.database.telegram_config import (
    get_all_telegram_configs,
    get_telegram_config,
)
from streamlit_app.utils.logging_utils import setup_logger
from telegram_ai_agent import TelegramConfig
from telegram_ai_agent.tools import TelegramTools


logger = setup_logger(__name__)

current_dir = Path(__file__).parents[1].resolve()

st.set_page_config(page_title="Manage Chats", page_icon="💬")

st.markdown("# Manage Chats")

configs = get_all_telegram_configs()
if not configs:
    st.warning("No Telegram accounts found. Please add an account first.")
else:
    selected_phone = st.selectbox(
        "Select Telegram Account", [config.phone_number for config in configs]
    )

    tab1, tab2, tab3 = st.tabs(["View Chats", "Download Members", "Open Chat"])

    with tab1:
        st.header("View Available Chats")
        limit = st.number_input(
            "Number of chats to show", min_value=1, max_value=100, value=20
        )

        if st.button("Show Chats"):
            config = get_telegram_config(selected_phone)
            if config:
                telegram_config = TelegramConfig(
                    session_name=str(config.session_file),
                    api_id=int(config.api_id),
                    api_hash=str(config.api_hash),
                    phone_number=str(config.phone_number),
                )

                async def show_chats():
                    auth_success, session = await try_auth(telegram_config, logger)
                    if not auth_success:
                        return []

                    if session is None:
                        st.error("Failed to authorize. Please try again.")
                        return []

                    tools = TelegramTools(session, logger=logger)
                    dialogs = await tools.get_dialogs(limit=limit)
                    await session.stop()
                    return dialogs

                dialogs = asyncio.run(show_chats())
                print(dialogs)
                if dialogs:
                    df = pd.DataFrame([{**d, "id": str(d["id"])} for d in dialogs])
                    st.dataframe(df)

    with tab2:
        st.header("Download Channel Members")
        chat_identifier = st.text_input("Channel/Group ID or Username")
        file_name = st.text_input("Save to File", "members.csv")
        include_kick_ban = st.checkbox("Include kicked and banned members")

        if st.button("Download Members"):
            config = get_telegram_config(selected_phone)
            if config:
                telegram_config = TelegramConfig(
                    session_name=str(config.session_file),
                    api_id=int(config.api_id),
                    api_hash=str(config.api_hash),
                    phone_number=str(config.phone_number),
                )

                async def download_members():
                    auth_success, session = await try_auth(telegram_config, logger)

                    if not auth_success or session is None:
                        st.error("Failed to authorize. Please try again.")
                        return 0

                    tools = TelegramTools(session, logger=logger)
                    count = await tools.get_chat_members(
                        chat_identifier,
                        file_name,
                        include_kick_ban=include_kick_ban,
                        output_dir=str(current_dir),
                    )
                    await session.stop()
                    return count

                member_count = asyncio.run(download_members())
                st.success(f"Downloaded {member_count} members to {file_name}")

    with tab3:
        st.header("Open Chat")
        chat_id = st.text_input("Enter Chat ID or Username")
        message_limit = st.number_input(
            "Number of messages to fetch", min_value=1, max_value=100, value=10
        )

        if "chat_messages" not in st.session_state:
            st.session_state.chat_messages = []

        if st.button("Open Chat"):
            config = get_telegram_config(selected_phone)
            if config:
                telegram_config = TelegramConfig(
                    session_name=str(config.session_file),
                    api_id=int(config.api_id),
                    api_hash=str(config.api_hash),
                    phone_number=str(config.phone_number),
                )

                async def open_chat():
                    auth_success, session = await try_auth(telegram_config, logger)

                    if not auth_success or session is None:
                        st.error("Failed to authorize. Please try again.")
                        return None, []

                    tools = TelegramTools(session, logger=logger)
                    chat = await tools.find_chat(chat_id)
                    messages = await session.get_messages(chat, limit=message_limit)
                    await session.stop()
                    return chat, messages

                chat, messages = asyncio.run(open_chat())
                st.session_state.chat = chat
                st.session_state.chat_messages = messages

        if "chat_messages" in st.session_state and st.session_state.chat_messages:
            chat = st.session_state.chat
            if hasattr(chat, "title"):
                st.subheader(f"Chat: {chat.title}")
            elif hasattr(chat, "first_name"):
                st.subheader(f"User: {chat.first_name} {chat.last_name or ''}")
            else:
                st.subheader(f"Chat ID: {chat.id}")

            st.write("### Messages")
            for msg in reversed(st.session_state.chat_messages):
                sender = msg.sender
                sender_name = getattr(sender, "first_name", None) or getattr(
                    sender, "title", "Unknown"
                )
                username = getattr(sender, "username", None)

                col1, col2 = st.columns([1, 4])
                with col1:
                    if username:
                        st.markdown(f"**{sender_name}** (@{username})")
                    else:
                        st.markdown(f"**{sender_name}**")
                with col2:
                    st.markdown(f"{msg.text}")
                st.markdown("---")

            user_message = st.text_input("Type your message")
            if st.button("Send"):
                config = get_telegram_config(selected_phone)
                if config:
                    telegram_config = TelegramConfig(
                        session_name=str(config.session_file),
                        api_id=int(config.api_id),
                        api_hash=str(config.api_hash),
                        phone_number=str(config.phone_number),
                    )

                    async def send_message():
                        auth_success, session = await try_auth(telegram_config, logger)

                        if not auth_success or session is None:
                            st.error("Failed to authorize. Please try again.")
                            return []

                        await session.send_message(st.session_state.chat, user_message)

                        new_messages = await session.get_messages(
                            st.session_state.chat, limit=message_limit
                        )
                        await session.stop()
                        return new_messages

                    st.session_state.chat_messages = asyncio.run(send_message())
                    st.success("Message sent!")
                    st.rerun()

        if st.button("Close Chat"):
            for key in ["chat", "chat_messages"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
