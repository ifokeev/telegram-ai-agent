import streamlit as st
from streamlit_app.utils.logging_utils import setup_logger
from streamlit_app.utils.database.assistant import get_all_assistants
from streamlit_app.utils.assistant_factory import create_phi_assistant

logger = setup_logger(__name__)

st.set_page_config(page_title="Assistant Playground", page_icon="🎮")

st.markdown("# Assistant Playground")

# Get all assistants
assistants = get_all_assistants()
if not assistants:
    st.warning("No assistants found. Please create an assistant first.")
else:
    selected_assistant_name = st.selectbox(
        "Select Assistant", [assistant.name for assistant in assistants]
    )

    assistant_data = next(
        (a for a in assistants if a.name == selected_assistant_name), None
    )

    if assistant_data:
        st.subheader(f"Chatting with: {assistant_data.name}")

        if str(assistant_data.description) != "":
            st.write(f"Description: {assistant_data.description}")

        if str(assistant_data.instructions) != "":
            st.write("Instructions:")
            for instruction in assistant_data.instructions.split("\n"):
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
            st.session_state.messages.append({"role": "user", "content": prompt})

            try:
                # Create the phi_assistant using the factory method
                phi_assistant = create_phi_assistant(assistant_data)
                # Run the assistant to get a response
                response = phi_assistant.run(
                    messages=st.session_state.messages, stream=False
                )

                # Display assistant response in chat message container
                with st.chat_message("assistant"):
                    st.markdown(response)
                # Add assistant response to chat history
                st.session_state.messages.append(
                    {"role": "assistant", "content": response}
                )
            except Exception as e:
                logger.error(f"Error in assistant response: {str(e)}")
                st.error(f"An error occurred: {str(e)}")

        # Option to clear chat history
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
