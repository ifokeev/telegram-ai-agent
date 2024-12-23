import time

from pathlib import Path

import pandas as pd
import streamlit as st

from streamlit_app.utils.auth_utils import authorize
from streamlit_app.utils.database.agent_process import (
    start_agent_process,
    stop_agent_process,
)
from streamlit_app.utils.database.assistant import (
    get_all_assistants,
)
from streamlit_app.utils.logging_utils import setup_logger
from telegram_ai_agent import TelegramConfig


# Define the sessions folder
current_dir = Path(__file__).parents[0].resolve()
SESSIONS_FOLDER = current_dir / "sessions"

st.set_page_config(
    page_title="Telegram AI Agent Dashboard",
    page_icon="🤖",
)

logger = setup_logger(__name__)
st.write("# Welcome to Telegram AI Agent Dashboard! 👋")

st.sidebar.success("Select a page above.")

st.markdown(
    """
    This dashboard allows you to manage your Telegram AI Agent. You can:

    - 🔐 Manage Telegram accounts
    - 💬 View and interact with chats
    - 👥 Create and manage user segments
    - 📢 Set up and run campaigns
    - 🤖 Set up AI assistants
    - 🎮 Test your assistants in the playground

    Choose a function from the sidebar to get started!
    """
)

# Agent management
st.subheader("Manage Agents")

# Display existing assistants and their statuses
assistants = get_all_assistants()
if not assistants:
    st.info("No assistants found. Please create assistants first.")
else:
    assistant_data = []
    for assistant in assistants:
        assistant_data.append(
            {
                "Assistant ID": assistant.id,
                "Name": assistant.name,
                "Status": assistant.status,
                "PID": assistant.pid,
            }
        )
    df = pd.DataFrame(assistant_data)
    st.table(df)

    # Buttons to start or stop agents
    for assistant in assistants:
        st.markdown("---")  # Add a horizontal line for better separation
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write(f"Assistant: {assistant.name}")
        with col2:
            if assistant.status == "Running":
                if st.button(
                    "Stop", key=f"stop_{assistant.id}", use_container_width=True
                ):
                    stop_agent_process(assistant.id)
                    st.success(f"Stopping assistant '{assistant.name}'")
                    time.sleep(1)
                    st.rerun()
        with col3:
            if assistant.status != "Running":
                if st.button(
                    "Start", key=f"start_{assistant.id}", use_container_width=True
                ):
                    # Create a unique session file name for this agent process
                    process_session_file = (
                        SESSIONS_FOLDER / f"agent_process_{assistant.id}"
                    )

                    # Create TelegramConfig
                    config = TelegramConfig(
                        session_name=str(process_session_file),
                        api_id=assistant.telegram_config.api_id,
                        api_hash=assistant.telegram_config.api_hash,
                        phone_number=assistant.telegram_config.phone_number,
                    )

                    # Run authorization
                    auth_success, session = authorize(config, logger, stop_session=True)
                    if auth_success:
                        # Start the agent process with the unique session file
                        start_agent_process(assistant.id, str(process_session_file))
                        st.success(f"Starting assistant '{assistant.name}'")
                        time.sleep(1)
                        st.rerun()
