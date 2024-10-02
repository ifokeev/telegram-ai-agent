import streamlit as st
from phi.assistant.assistant import Assistant
from phi.llm.openai.chat import OpenAIChat
from streamlit_app.utils.logging_utils import setup_logger

logger = setup_logger(__name__)

st.set_page_config(page_title="Manage Assistants", page_icon="🤖")

st.markdown("# Manage AI Assistants")

tab1, tab2 = st.tabs(["Create Assistant", "Manage Assistants"])

with tab1:
    st.header("Create New Assistant")
    name = st.text_input("Assistant Name")
    api_key = st.text_input("OpenAI API Key", type="password")
    description = st.text_area("Assistant Description")
    instructions = st.text_area("Instructions (one per line)")

    if st.button("Create Assistant"):
        try:
            openai_chat = OpenAIChat(api_key=api_key)
            assistant = Assistant(
                llm=openai_chat,
                run_id=name,
                description=description,
                instructions=[
                    line.strip() for line in instructions.split("\n") if line.strip()
                ],
                add_datetime_to_instructions=True,
            )
            st.session_state.assistants = st.session_state.get("assistants", {})
            st.session_state.assistants[name] = assistant
            logger.info(f"Assistant '{name}' created successfully!")
            st.success(f"Assistant '{name}' created successfully!")
        except Exception as e:
            logger.error(f"Error creating assistant: {str(e)}")
            st.error(f"An error occurred: {str(e)}")

with tab2:
    st.header("Manage Existing Assistants")
    assistants = st.session_state.get("assistants", {})
    for name, assistant in assistants.items():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"Name: {name}")
            st.write(f"Description: {assistant.description}")
        with col2:
            if st.button("Delete", key=f"delete_{name}"):
                del st.session_state.assistants[name]
                st.rerun()
