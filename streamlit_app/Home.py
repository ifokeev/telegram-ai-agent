import streamlit as st

st.set_page_config(
    page_title="Telegram AI Agent Dashboard",
    page_icon="🤖",
)

st.write("# Welcome to Telegram AI Agent Dashboard! 👋")

st.sidebar.success("Select a page above.")

st.markdown(
    """
    This dashboard allows you to manage your Telegram AI Agent. You can:
    
    - Manage Telegram accounts
    - View and interact with chats
    - Set up AI assistants
    - Create and manage campaigns
    
    Choose a function from the sidebar to get started!
    """
)
