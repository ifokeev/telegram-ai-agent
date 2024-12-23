import streamlit as st

from streamlit_app.utils.assistant_factory import create_phi_assistant
from streamlit_app.utils.database.assistant import (
    delete_assistant,
    get_assistants,
    save_assistant,
    update_assistant,
)
from streamlit_app.utils.database.models import Assistant as AssistantModel
from streamlit_app.utils.database.telegram_config import (
    get_all_telegram_configs,
    get_telegram_config,
)
from streamlit_app.utils.logging_utils import setup_logger


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

        def test_assistant(assistant_data):
            try:
                # Use the factory method to create the assistant
                phi_assistant = create_phi_assistant(assistant_data)
                # Test the assistant with a sample prompt
                test_prompt = "Hello, how are you?"
                response = phi_assistant.run(
                    messages=[{"role": "user", "content": test_prompt}], stream=False
                )
                st.write(f"**Test Prompt:** {test_prompt}")
                st.write(f"**Assistant Response:** {response}")
            except Exception as e:
                st.error(f"An error occurred during testing: {str(e)}")

        def render_proxy_fields(
            prefix="",
            proxy_type=None,
            proxy_addr=None,
            proxy_port=None,
            proxy_username=None,
            proxy_password=None,
            proxy_rdns=True,
        ):
            """Render proxy configuration fields"""
            st.subheader("Proxy Configuration (Optional)")

            col1, col2 = st.columns(2)
            with col1:
                proxy_type = st.selectbox(
                    "Proxy Type",
                    options=["", "socks5", "socks4", "http"],
                    key=f"{prefix}proxy_type",
                    index=(
                        0
                        if not proxy_type
                        else ["", "socks5", "socks4", "http"].index(proxy_type)
                    ),
                )

                proxy_addr = st.text_input(
                    "Proxy Address",
                    value=proxy_addr or "",
                    key=f"{prefix}proxy_addr",
                    help="IP address or hostname of the proxy",
                )

                proxy_port = st.number_input(
                    "Proxy Port",
                    min_value=0,
                    max_value=65535,
                    value=proxy_port or 0,
                    key=f"{prefix}proxy_port",
                )

            with col2:
                proxy_username = st.text_input(
                    "Proxy Username (Optional)",
                    value=proxy_username or "",
                    key=f"{prefix}proxy_username",
                )

                proxy_password = st.text_input(
                    "Proxy Password (Optional)",
                    value=proxy_password or "",
                    type="password",
                    key=f"{prefix}proxy_password",
                )

                proxy_rdns = st.checkbox(
                    "Remote DNS Resolution",
                    value=proxy_rdns,
                    key=f"{prefix}proxy_rdns",
                    help="Whether to use remote or local DNS resolution",
                )

            return (
                proxy_type,
                proxy_addr,
                proxy_port if proxy_port > 0 else None,
                proxy_username or None,
                proxy_password or None,
                proxy_rdns,
            )

        def render_advanced_config(prefix="", assistant=None):
            """Render advanced configuration fields in an expander"""
            with st.expander("Advanced Configuration", expanded=False):
                st.markdown("### Timing and Behavior Settings")

                col1, col2 = st.columns(2)
                with col1:
                    timeout = st.number_input(
                        "Timeout (seconds)",
                        min_value=1,
                        max_value=300,
                        value=assistant.timeout if assistant else 30,
                        key=f"{prefix}timeout",
                    )

                    set_typing = st.checkbox(
                        "Show typing indicator",
                        value=assistant.set_typing if assistant else True,
                        key=f"{prefix}set_typing",
                    )

                with col2:
                    chat_history_limit = st.number_input(
                        "Chat History Limit",
                        min_value=1,
                        max_value=1000,
                        value=assistant.chat_history_limit if assistant else 100,
                        key=f"{prefix}chat_history_limit",
                    )

                st.markdown("### Typing Simulation")
                col1, col2, col3 = st.columns(3)

                with col1:
                    typing_delay_factor = st.number_input(
                        "Typing Delay Factor",
                        min_value=0.01,
                        max_value=1.0,
                        value=assistant.typing_delay_factor if assistant else 0.05,
                        format="%.2f",
                        key=f"{prefix}typing_delay_factor",
                    )

                    min_typing_speed = st.number_input(
                        "Min Typing Speed (WPM)",
                        min_value=10.0,
                        max_value=500.0,
                        value=assistant.min_typing_speed if assistant else 100.0,
                        key=f"{prefix}min_typing_speed",
                    )

                with col2:
                    typing_delay_max = st.number_input(
                        "Max Typing Delay",
                        min_value=1.0,
                        max_value=60.0,
                        value=assistant.typing_delay_max if assistant else 30.0,
                        key=f"{prefix}typing_delay_max",
                    )

                    max_typing_speed = st.number_input(
                        "Max Typing Speed (WPM)",
                        min_value=10.0,
                        max_value=500.0,
                        value=assistant.max_typing_speed if assistant else 200.0,
                        key=f"{prefix}max_typing_speed",
                    )

                st.markdown("### Message Chunking")
                col1, col2 = st.columns(2)

                with col1:
                    min_messages = st.number_input(
                        "Min Messages",
                        min_value=1,
                        max_value=10,
                        value=assistant.min_messages if assistant else 1,
                        key=f"{prefix}min_messages",
                    )

                    inter_chunk_delay_min = st.number_input(
                        "Min Chunk Delay",
                        min_value=0.1,
                        max_value=10.0,
                        value=assistant.inter_chunk_delay_min if assistant else 1.5,
                        format="%.1f",
                        key=f"{prefix}inter_chunk_delay_min",
                    )

                with col2:
                    max_messages = st.number_input(
                        "Max Messages",
                        min_value=1,
                        max_value=10,
                        value=assistant.max_messages if assistant else 3,
                        key=f"{prefix}max_messages",
                    )

                    inter_chunk_delay_max = st.number_input(
                        "Max Chunk Delay",
                        min_value=0.1,
                        max_value=10.0,
                        value=assistant.inter_chunk_delay_max if assistant else 4.0,
                        format="%.1f",
                        key=f"{prefix}inter_chunk_delay_max",
                    )

                st.markdown("### Natural Pauses")
                col1, col2 = st.columns(2)

                with col1:
                    min_burst_length = st.number_input(
                        "Min Burst Length",
                        min_value=1,
                        max_value=50,
                        value=assistant.min_burst_length if assistant else 5,
                        key=f"{prefix}min_burst_length",
                    )

                    min_pause_duration = st.number_input(
                        "Min Pause Duration",
                        min_value=0.1,
                        max_value=5.0,
                        value=assistant.min_pause_duration if assistant else 0.5,
                        format="%.1f",
                        key=f"{prefix}min_pause_duration",
                    )

                with col2:
                    max_burst_length = st.number_input(
                        "Max Burst Length",
                        min_value=1,
                        max_value=50,
                        value=assistant.max_burst_length if assistant else 15,
                        key=f"{prefix}max_burst_length",
                    )

                    max_pause_duration = st.number_input(
                        "Max Pause Duration",
                        min_value=0.1,
                        max_value=5.0,
                        value=assistant.max_pause_duration if assistant else 2.0,
                        format="%.1f",
                        key=f"{prefix}max_pause_duration",
                    )

                st.markdown("### Read Receipts")
                col1, col2, col3 = st.columns(3)

                with col1:
                    read_delay_factor = st.number_input(
                        "Read Delay Factor",
                        min_value=0.01,
                        max_value=1.0,
                        value=assistant.read_delay_factor if assistant else 0.05,
                        format="%.2f",
                        key=f"{prefix}read_delay_factor",
                    )

                with col2:
                    min_read_delay = st.number_input(
                        "Min Read Delay",
                        min_value=0.1,
                        max_value=10.0,
                        value=assistant.min_read_delay if assistant else 0.5,
                        format="%.1f",
                        key=f"{prefix}min_read_delay",
                    )

                with col3:
                    max_read_delay = st.number_input(
                        "Max Read Delay",
                        min_value=0.1,
                        max_value=10.0,
                        value=assistant.max_read_delay if assistant else 2.0,
                        format="%.1f",
                        key=f"{prefix}max_read_delay",
                    )

                return {
                    "timeout": timeout,
                    "set_typing": set_typing,
                    "typing_delay_factor": typing_delay_factor,
                    "typing_delay_max": typing_delay_max,
                    "inter_chunk_delay_min": inter_chunk_delay_min,
                    "inter_chunk_delay_max": inter_chunk_delay_max,
                    "min_messages": min_messages,
                    "max_messages": max_messages,
                    "min_typing_speed": min_typing_speed,
                    "max_typing_speed": max_typing_speed,
                    "min_burst_length": min_burst_length,
                    "max_burst_length": max_burst_length,
                    "min_pause_duration": min_pause_duration,
                    "max_pause_duration": max_pause_duration,
                    "read_delay_factor": read_delay_factor,
                    "min_read_delay": min_read_delay,
                    "max_read_delay": max_read_delay,
                    "chat_history_limit": chat_history_limit,
                }

        with tab1:
            st.header("Create New Assistant")
            name = st.text_input("Assistant Name")
            api_key = st.text_input("OpenAI API Key", type="password")
            description = st.text_area("Assistant Description")
            instructions = st.text_area("Instructions (one per line)")

            # Add proxy configuration
            (
                proxy_type,
                proxy_addr,
                proxy_port,
                proxy_username,
                proxy_password,
                proxy_rdns,
            ) = render_proxy_fields(prefix="create_")

            # Add advanced configuration
            advanced_config = render_advanced_config(prefix="create_")

            if st.button("Create Assistant"):
                try:
                    save_assistant(
                        config.id,
                        name,
                        api_key,
                        description,
                        instructions,
                        proxy_type,
                        proxy_addr,
                        proxy_port,
                        proxy_username,
                        proxy_password,
                        proxy_rdns,
                        **advanced_config,  # Include all advanced settings
                    )
                    logger.info(
                        f"Assistant '{name}' created successfully for {selected_phone}!"
                    )
                    st.success(
                        f"Assistant '{name}' created successfully for {selected_phone}!"
                    )
                except Exception as e:
                    logger.error(f"Error creating assistant: {str(e)}")
                    st.error(f"An error occurred: {str(e)}")

            # Add a "Test Assistant" button before creating the assistant
            if st.button("Test Assistant", key="test_new_assistant"):
                try:
                    # Create a temporary assistant_data object
                    assistant_data = AssistantModel(
                        name=name,
                        api_key=api_key,
                        description=description,
                        instructions=instructions,
                    )
                    test_assistant(assistant_data)
                except Exception as e:
                    st.error(f"An error occurred during testing: {str(e)}")

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

                    # Add proxy configuration
                    (
                        new_proxy_type,
                        new_proxy_addr,
                        new_proxy_port,
                        new_proxy_username,
                        new_proxy_password,
                        new_proxy_rdns,
                    ) = render_proxy_fields(
                        prefix="edit_",
                        proxy_type=selected_assistant.proxy_type,
                        proxy_addr=selected_assistant.proxy_addr,
                        proxy_port=selected_assistant.proxy_port,
                        proxy_username=selected_assistant.proxy_username,
                        proxy_password=selected_assistant.proxy_password,
                        proxy_rdns=selected_assistant.proxy_rdns,
                    )

                    # Add advanced configuration
                    new_advanced_config = render_advanced_config(
                        prefix="edit_", assistant=selected_assistant
                    )

                    if st.button("Update Assistant"):
                        try:
                            update_assistant(
                                selected_assistant.id,
                                new_name,
                                new_api_key,
                                new_description,
                                new_instructions,
                                new_proxy_type,
                                new_proxy_addr,
                                new_proxy_port,
                                new_proxy_username,
                                new_proxy_password,
                                new_proxy_rdns,
                                **new_advanced_config,  # Include all advanced settings
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

                    # Add a "Test Assistant" button
                    if st.button("Test Assistant", key="test_existing_assistant"):
                        try:
                            # Create an updated assistant_data object
                            assistant_data = AssistantModel(
                                name=new_name,
                                api_key=new_api_key,
                                description=new_description,
                                instructions=new_instructions,
                            )
                            test_assistant(assistant_data)
                        except Exception as e:
                            st.error(f"An error occurred during testing: {str(e)}")
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
