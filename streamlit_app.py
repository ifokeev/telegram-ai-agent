import streamlit as st
import asyncio
import os
import json
from dotenv import load_dotenv
from telegram_ai_agent import TelegramAIAgent, TelegramConfig
from telegram_ai_agent.session import TelegramSession
from telegram_ai_agent.utils import setup_logging
from phi.assistant.assistant import Assistant
from phi.llm.openai.chat import OpenAIChat
from telegram_ai_agent.tools import TelegramTools
import pandas as pd

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logging()

# Initialize session state
if "assistants" not in st.session_state:
    st.session_state.assistants = {}
if "telegram_users" not in st.session_state:
    st.session_state.telegram_users = {}


def setup_assistant():
    logger.info("Setting up assistant")
    st.header("Setup Assistant")
    st.write(
        """
    In this section, you can create a new AI assistant for your Telegram bot.
    
    Instructions:
    1. Enter a unique name for your assistant.
    2. Provide a description of what the assistant should do.
    3. Enter your OpenAI API key (keep this secret!).
    4. Add instructions for the assistant (one per line).
    5. Click 'Create Assistant' to set up the new assistant.
    """
    )

    name = st.text_input("Assistant Name", help="Name of the assistant.")
    api_key = st.text_input(
        "OpenAI API Key", type="password", help="API key for OpenAI."
    )

    description = st.text_area("Assistant Description", help="Describe the assistant.")
    # New input for instructions
    instructions_text = st.text_area(
        "Instructions (one per line)",
        height=150,
        help="Enter each instruction on a new line. These will guide the assistant's behavior.",
    )

    # Convert instructions text to a list
    instructions = [
        line.strip() for line in instructions_text.split("\n") if line.strip()
    ]

    if st.button("Create Assistant"):
        openai_chat = OpenAIChat(api_key=api_key)
        assistant = Assistant(
            llm=openai_chat,
            run_id=name,
            description=description,
            instructions=instructions,  # Add instructions to the assistant
            add_datetime_to_instructions=True,
        )
        st.session_state.assistants[name] = assistant
        st.success(f"Assistant '{name}' created successfully!")

        # Display the created assistant's details
        st.write("Assistant Details:")
        st.write(f"Name: {name}")
        st.write(f"Description: {description}")
        st.write("Instructions:")
        for i, instruction in enumerate(instructions, 1):
            st.write(f"{i}. {instruction}")


async def authorize_telegram():
    logger.info("Authorizing Telegram")
    st.header("Authorize Telegram")
    st.write(
        """
    Here you can authorize a new Telegram account to use with the AI agent.
    
    Instructions:
    1. Enter the phone number associated with your Telegram account.
    2. Provide your Telegram API ID and API Hash (obtain these from https://my.telegram.org).
    3. Click 'Authorize' to add the Telegram account.
    
    Note: Keep your API ID and API Hash secret!
    """
    )

    phone_number = st.text_input("Phone Number")
    api_id = st.text_input("API ID")
    api_hash = st.text_input("API Hash", type="password")

    if st.button("Authorize"):
        config = TelegramConfig(
            session_name=f"session_{phone_number}",
            api_id=int(api_id),
            api_hash=api_hash,
            phone_number=phone_number,
        )

        # try to start session
        session = TelegramSession(config, logger=logger)
        await session.start()

        st.session_state.telegram_users[phone_number] = config
        st.success(f"Telegram user '{phone_number}' authorized successfully!")


async def download_members():
    logger.info("Downloading members")
    st.header("Download Channel Members")
    st.write(
        """
    Use this section to download members from a Telegram channel or group.
    
    Instructions:
    1. Select the Telegram account to use for downloading.
    2. Enter the channel/group ID or username.
    3. Specify a file name to save the member list (default is 'members.csv').
    4. Set the maximum number of members to download (0 for all available members).
    5. Click 'Download Members' to start the process.
    
    Note: You must be a member of the channel or group to download its member list.
    For private channels, use the channel ID (a negative integer, e.g., -1001234567890).
    For public channels or groups, you can use either the username (without @) or the ID.
    The download process may take some time for large groups.
    """
    )

    phone_number = st.selectbox(
        "Select Telegram User", list(st.session_state.telegram_users.keys())
    )
    chat_identifier = st.text_input("Channel/Group ID or Username")
    file_name = st.text_input("Save to File", "members.csv")

    include_kick_ban = st.checkbox("Include kicked and banned members")

    if st.button("Download Members"):
        config = st.session_state.telegram_users[phone_number]
        session = TelegramSession(config, logger=logger)

        try:
            await session.start()
            if not session.client:
                raise Exception("Failed to start session")

            tools = TelegramTools(session.client, logger=logger)

            member_count = await tools.get_chat_members(
                chat_identifier, file_name, include_kick_ban=include_kick_ban
            )
            st.success(f"Downloaded {member_count} members to {file_name}")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
        finally:
            await session.stop()


async def show_available_chats():
    logger.info("Showing available chats")
    st.header("Available Chats")
    st.write(
        """
    This section shows your available chats and their last messages.
    
    Instructions:
    1. Select the Telegram account to use.
    2. Click 'Show Chats' to display the list of available chats.
    """
    )

    phone_number = st.selectbox(
        "Select Telegram User", list(st.session_state.telegram_users.keys())
    )
    limit = st.number_input(
        "Number of chats to show", min_value=1, max_value=100, value=20
    )

    if st.button("Show Chats"):
        config = st.session_state.telegram_users[phone_number]
        session = TelegramSession(config, logger=logger)

        try:
            await session.start()
            if not session.client:
                raise Exception("Failed to start session")

            tools = TelegramTools(session.client, logger=logger)

            dialogs = await tools.get_dialogs(limit=limit)

            # Convert the 'id' field to string
            for dialog in dialogs:
                dialog["id"] = str(dialog["id"])

            df = pd.DataFrame(dialogs)
            st.dataframe(df)

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
        finally:
            await session.stop()


def send_messages():
    logger.info("Sending messages")
    st.header("Send Messages")
    st.write(
        """
    This section allows you to send messages to members of a channel or group.
    
    Instructions:
    1. Select the file containing the member list.
    2. Choose the Telegram account to use for sending messages.
    3. Select the AI assistant to generate messages (if making unique messages).
    4. Enter a message template.
    5. Choose whether to make each message unique.
    6. Set a limit on the number of messages to send (0 for no limit).
    7. Set a delay between messages to avoid flooding.
    8. Click 'Send Messages' to start the process.
    
    Note: Be responsible when sending messages to avoid spamming users.
    """
    )

    file_name = st.selectbox("Select Members File", os.listdir())
    phone_number = st.selectbox(
        "Select Telegram User", list(st.session_state.telegram_users.keys())
    )
    assistant_name = st.selectbox(
        "Select Assistant", list(st.session_state.assistants.keys())
    )
    message = st.text_area("Message Template")
    make_unique = st.checkbox("Make every message unique")
    limit = st.number_input("Limit (0 for no limit)", min_value=0, value=0)
    throttle = st.number_input("Throttle (seconds)", min_value=0.0, value=1.0)

    if st.button("Send Messages"):
        with open(file_name, "r") as f:
            members = json.load(f)

        config = st.session_state.telegram_users[phone_number]
        assistant = st.session_state.assistants[assistant_name]
        agent = TelegramAIAgent(assistant, config, logger=logger)

        async def send_messages_async():
            await agent.start()
            sent_count = 0
            for member in members:
                if limit > 0 and sent_count >= limit:
                    break

                if make_unique:
                    unique_message = await assistant.achat(
                        messages=[
                            {
                                "role": "system",
                                "content": "Rephrase the following message in a unique way:",
                            },
                            {"role": "user", "content": message},
                        ]
                    )
                    send_message = unique_message.content
                else:
                    send_message = message

                await agent.send_messages(
                    [member["username"] or member["id"]], send_message
                )
                sent_count += 1
                await asyncio.sleep(throttle)

            await agent.stop()
            st.success(f"Sent messages to {sent_count} members")

        asyncio.run(send_messages_async())


def main():
    logger.info("Starting Telegram AI Agent Dashboard")
    st.title("Telegram AI Agent Dashboard")
    st.write(
        """
    Welcome to the Telegram AI Agent Dashboard! This tool allows you to set up AI assistants,
    authorize Telegram accounts, download channel members, and send messages using AI-generated content.
    
    Use the sidebar to navigate between different functions.
    """
    )

    menu = [
        "Authorize Telegram",
        "Show Available Chats",
        "Download Members",
        "Setup Assistant",
        "Send Messages",
    ]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Setup Assistant":
        setup_assistant()
    elif choice == "Authorize Telegram":
        asyncio.run(authorize_telegram())
    elif choice == "Show Available Chats":
        asyncio.run(show_available_chats())
    elif choice == "Download Members":
        asyncio.run(download_members())
    elif choice == "Send Messages":
        send_messages()


if __name__ == "__main__":
    main()
