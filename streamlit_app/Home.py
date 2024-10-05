import streamlit as st
import pandas as pd
from streamlit_app.utils.database.assistant import (
    get_all_assistants,
)
from streamlit_app.utils.database.agent_process import (
    start_agent_process,
    stop_agent_process,
)
import time
import threading

st.set_page_config(
    page_title="Telegram AI Agent Dashboard",
    page_icon="🤖",
)

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
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"Assistant: {assistant.name}")
        with col2:
            if assistant.status == "Running":
                if st.button("Stop", key=f"stop_{assistant.id}"):
                    stop_agent_process(assistant.id)
                    st.success(f"Stopping assistant '{assistant.name}'")
                    time.sleep(1)
                    st.rerun()
            else:
                if st.button("Start", key=f"start_{assistant.id}"):
                    start_agent_process(assistant.id)
                    st.success(f"Starting assistant '{assistant.name}'")
                    time.sleep(1)
                    st.rerun()


# Optionally, auto-refresh the page every few seconds
def auto_refresh(interval=10):
    time.sleep(interval)
    st.rerun()


# Start the auto-refresh in a separate thread
threading.Thread(target=auto_refresh).start()
