import streamlit as st
from phi.assistant.assistant import Assistant
from phi.llm.openai.chat import OpenAIChat
from streamlit_app.utils.logging_utils import setup_logger
from streamlit_app.utils.database import (
    get_assistants,
    get_all_telegram_configs,
    get_telegram_config,
)

logger = setup_logger(__name__)

st.set_page_config(page_title="Assistant Playground", page_icon="🎮")

st.markdown("# Assistant Playground")

# Get all Telegram configs (assuming we're still linking assistants to Telegram accounts)
configs = get_all_telegram_configs()
if not configs:
    st.warning("No Telegram accounts found. Please add an account first.")
else:
    selected_phone = st.selectbox(
        "Select Telegram Account", [config.phone_number for config in configs]
    )

    config = get_telegram_config(selected_phone)

    if config:
        assistants = get_assistants(config.id)
        if not assistants:
            st.warning(
                "No assistants found for this account. Please create an assistant first."
            )
        else:
            selected_assistant = st.selectbox(
                "Select Assistant", [assistant.name for assistant in assistants]
            )

            assistant = next(
                (a for a in assistants if a.name == selected_assistant), None
            )

            if assistant:
                st.subheader(f"Chatting with: {assistant.name}")
                st.write(f"Description: {assistant.description}")
                st.write("Instructions:")
                for instruction in assistant.instructions.split("\n"):
                    st.write(f"- {instruction}")

                # Initialize chat history
                if "messages" not in st.session_state:
                    st.session_state.messages = []

                # Display chat messages from history on app rerun
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

                # React to user input
                if prompt := st.chat_input("What is your message?"):
                    # Display user message in chat message container
                    st.chat_message("user").markdown(prompt)
                    # Add user message to chat history
                    st.session_state.messages.append(
                        {"role": "user", "content": prompt}
                    )

                    try:
                        openai_chat = OpenAIChat(api_key=assistant.api_key)
                        phi_assistant = Assistant(
                            llm=openai_chat,
                            run_id=assistant.name,
                            description=assistant.description,
                            instructions=assistant.instructions,
                            add_datetime_to_instructions=True,
                        )
                        response = phi_assistant.chat(
                            messages=st.session_state.messages
                        )

                        # Display assistant response in chat message container
                        with st.chat_message("assistant"):
                            st.markdown(response.content)
                        # Add assistant response to chat history
                        st.session_state.messages.append(
                            {"role": "assistant", "content": response.content}
                        )
                    except Exception as e:
                        logger.error(f"Error in assistant response: {str(e)}")
                        st.error(f"An error occurred: {str(e)}")

                # Option to clear chat history
                if st.button("Clear Chat History"):
                    st.session_state.messages = []
                    st.rerun()
