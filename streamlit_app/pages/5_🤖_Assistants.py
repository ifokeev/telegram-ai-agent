import streamlit as st
from phi.assistant.assistant import Assistant
from phi.llm.openai.chat import OpenAIChat
from streamlit_app.utils.logging_utils import setup_logger
from streamlit_app.utils.database import (
    get_all_telegram_configs,
    get_telegram_config,
    save_assistant,
    get_assistants,
    update_assistant,
    delete_assistant,
)

logger = setup_logger(__name__)

st.set_page_config(page_title="Manage Assistants", page_icon="🤖")

st.markdown("# Manage AI Assistants")

# Get all Telegram configs
configs = get_all_telegram_configs()
if not configs:
    st.warning("No Telegram accounts found. Please add an account first.")
else:
    selected_phone = st.selectbox(
        "Select Telegram Account", [config.phone_number for config in configs]
    )

    config = get_telegram_config(selected_phone)

    if config:
        tab1, tab2, tab3 = st.tabs(
            ["Create Assistant", "Edit Assistant", "Manage Assistants"]
        )

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
                            line.strip()
                            for line in instructions.split("\n")
                            if line.strip()
                        ],
                        add_datetime_to_instructions=True,
                    )
                    assistant.print_response("Hello, how are you?")

                    save_assistant(config.id, name, api_key, description, instructions)
                    logger.info(
                        f"Assistant '{name}' created successfully for {selected_phone}!"
                    )
                    st.success(
                        f"Assistant '{name}' created successfully for {selected_phone}!"
                    )
                except Exception as e:
                    logger.error(f"Error creating assistant: {str(e)}")
                    st.error(f"An error occurred: {str(e)}")

        with tab2:
            st.header("Edit Assistant")
            assistants = get_assistants(config.id)
            if assistants:
                assistant_to_edit = st.selectbox(
                    "Select Assistant to Edit", [a.name for a in assistants]
                )
                selected_assistant = next(
                    (a for a in assistants if a.name == assistant_to_edit), None
                )

                if selected_assistant:
                    new_name = st.text_input("New Name", value=selected_assistant.name)
                    new_api_key = st.text_input(
                        "New OpenAI API Key",
                        type="password",
                        value=selected_assistant.api_key,
                    )
                    new_description = st.text_area(
                        "New Description", value=selected_assistant.description
                    )
                    new_instructions = st.text_area(
                        "New Instructions", value=selected_assistant.instructions
                    )

                    if st.button("Update Assistant"):
                        try:
                            update_assistant(
                                selected_assistant.id,
                                new_name,
                                new_api_key,
                                new_description,
                                new_instructions,
                            )
                            logger.info(
                                f"Assistant '{selected_assistant.name}' updated successfully!"
                            )
                            st.success(
                                f"Assistant '{selected_assistant.name}' updated successfully!"
                            )
                            st.rerun()
                        except Exception as e:
                            logger.error(f"Error updating assistant: {str(e)}")
                            st.error(f"An error occurred: {str(e)}")
            else:
                st.info(
                    "No assistants found for this account. Create one in the 'Create Assistant' tab."
                )

        with tab3:
            st.header("Manage Existing Assistants")
            assistants = get_assistants(config.id)
            if assistants:
                for assistant in assistants:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"Name: {assistant.name}")
                        st.write(f"Description: {assistant.description}")
                    with col2:
                        if st.button("Delete", key=f"delete_{assistant.id}"):
                            try:
                                delete_assistant(assistant.id)
                                logger.info(
                                    f"Assistant '{assistant.name}' deleted successfully!"
                                )
                                st.success(
                                    f"Assistant '{assistant.name}' deleted successfully!"
                                )
                                st.rerun()
                            except Exception as e:
                                logger.error(f"Error deleting assistant: {str(e)}")
                                st.error(f"An error occurred: {str(e)}")
            else:
                st.info(
                    "No assistants found for this account. Create one in the 'Create Assistant' tab."
                )
