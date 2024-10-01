import streamlit as st
import asyncio
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
from telegram_ai_agent import TelegramAIAgent, TelegramConfig
from telegram_ai_agent.session import TelegramSession
from telegram_ai_agent.utils import setup_logging
from phi.assistant.assistant import Assistant
from phi.llm.openai.chat import OpenAIChat
from telegram_ai_agent.tools import TelegramTools
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Get the directory of the current script (app.py)
current_dir = Path(__file__).parent.resolve()

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logging()

# Set sessions folder as a constant relative to the current directory
SESSIONS_FOLDER = current_dir / "sessions"

# Set the SQLite database path relative to the current directory
DB_PATH = current_dir / "sqlite.db"

# Ensure the directory for the database exists
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# Initialize session state
if "assistants" not in st.session_state:
    st.session_state.assistants = {}
if "telegram_users" not in st.session_state:
    st.session_state.telegram_users = {}

# Database setup
Base = declarative_base()


class TelegramConfigDB(Base):
    __tablename__ = "telegram_configs"

    id = Column(Integer, primary_key=True)
    phone_number = Column(String, unique=True)
    api_id = Column(Integer)
    api_hash = Column(String)
    session_file = Column(String)


# Use absolute path for database file
try:
    engine = create_engine(
        f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    logger.info(f"Database initialized at {DB_PATH}")
except Exception as e:
    logger.error(f"Error initializing database: {str(e)}")
    st.error(f"Error initializing database: {str(e)}")
    sys.exit(1)


def save_telegram_config(phone_number, api_id, api_hash, session_file):
    try:
        session = Session()
        config = TelegramConfigDB(
            phone_number=phone_number,
            api_id=api_id,
            api_hash=api_hash,
            session_file=session_file,
        )
        session.add(config)
        session.commit()
        logger.info(f"Saved Telegram config for {phone_number}")
    except Exception as e:
        logger.error(f"Error saving Telegram config: {str(e)}")
        st.error(f"Error saving Telegram config: {str(e)}")
    finally:
        session.close()


def get_telegram_config(phone_number):
    try:
        session = Session()
        config = (
            session.query(TelegramConfigDB).filter_by(phone_number=phone_number).first()
        )
        return config
    except Exception as e:
        logger.error(f"Error getting Telegram config: {str(e)}")
        st.error(f"Error getting Telegram config: {str(e)}")
        return None
    finally:
        session.close()


def get_all_telegram_configs():
    try:
        session = Session()
        configs = session.query(TelegramConfigDB).all()
        return configs
    except Exception as e:
        logger.error(f"Error getting all Telegram configs: {str(e)}")
        st.error(f"Error getting all Telegram configs: {str(e)}")
        return []
    finally:
        session.close()


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
        # Create the session folder if it doesn't exist
        SESSIONS_FOLDER.mkdir(parents=True, exist_ok=True)

        session_path = SESSIONS_FOLDER / f"session_{phone_number}"

        config = TelegramConfig(
            session_name=str(session_path),
            api_id=int(api_id),
            api_hash=api_hash,
            phone_number=phone_number,
        )

        # try to start session
        session = TelegramSession(config, logger=logger)
        await session.start()

        # Save config to database
        save_telegram_config(phone_number, api_id, api_hash, str(session_path))

        st.success(f"Telegram user '{phone_number}' authorized successfully!")
        st.info(f"Session file saved in: {session_path}")


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

    # Get all configs from database
    configs = get_all_telegram_configs()
    if not configs:
        st.warning(
            "No Telegram accounts found. Please authorize a Telegram account first."
        )
        return

    selected_phone = st.selectbox(
        "Select Telegram Account", [config.phone_number for config in configs]
    )
    chat_identifier = st.text_input("Channel/Group ID or Username")
    file_name = st.text_input("Save to File", "members.csv")

    include_kick_ban = st.checkbox("Include kicked and banned members")

    if st.button("Download Members"):
        config = get_telegram_config(selected_phone)
        if not config:
            st.error(f"No configuration found for {selected_phone}")
            return

        telegram_config = TelegramConfig(
            session_name=config.session_file,
            api_id=config.api_id,
            api_hash=config.api_hash,
            phone_number=config.phone_number,
        )
        session = TelegramSession(telegram_config, logger=logger)

        try:
            await session.start()
            if not session.client:
                raise Exception("Failed to start session")

            tools = TelegramTools(session.client, logger=logger)

            member_count = await tools.get_chat_members(
                chat_identifier,
                file_name,
                include_kick_ban=include_kick_ban,
                output_dir=str(current_dir),
            )
            st.success(f"Downloaded {member_count} members to {file_name}")
        finally:
            await session.stop()


async def show_available_chats():
    logger.info("Showing available chats")
    st.header("Available Chats")
    st.write(
        "This section shows your available chats and their last messages.\n\n"
        "Instructions:\n"
        "1. Select the Telegram session to use.\n"
        "2. Click 'Show Chats' to display the list of available chats."
    )

    configs = get_all_telegram_configs()
    if not configs:
        st.warning(
            "No Telegram accounts found. Please authorize a Telegram account first."
        )
        return

    selected_phone = st.selectbox(
        "Select Telegram Account", [config.phone_number for config in configs]
    )
    limit = st.number_input(
        "Number of chats to show", min_value=1, max_value=100, value=20
    )

    if st.button("Show Chats"):
        config = get_telegram_config(selected_phone)
        if not config:
            st.error(f"No configuration found for {selected_phone}")
            return

        telegram_config = TelegramConfig(
            session_name=config.session_file,
            api_id=config.api_id,
            api_hash=config.api_hash,
            phone_number=config.phone_number,
        )
        session = TelegramSession(telegram_config, logger=logger)

        try:
            await session.start()
            if not session.client:
                raise Exception("Failed to start session")

            tools = TelegramTools(session.client, logger=logger)

            dialogs = await tools.get_dialogs(limit=limit)

            df = pd.DataFrame([{**d, "id": str(d["id"])} for d in dialogs])
            st.dataframe(df)
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

    # Get all configs from database
    configs = get_all_telegram_configs()
    if not configs:
        st.warning(
            "No Telegram accounts found. Please authorize a Telegram account first."
        )
        return

    file_name = st.selectbox(
        "Select Members File", [f.name for f in current_dir.iterdir() if f.is_file()]
    )
    selected_phone = st.selectbox(
        "Select Telegram Account", [config.phone_number for config in configs]
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

        config = get_telegram_config(selected_phone)
        if not config:
            st.error(f"No configuration found for {selected_phone}")
            return

        telegram_config = TelegramConfig(
            session_name=config.session_file,
            api_id=config.api_id,
            api_hash=config.api_hash,
            phone_number=config.phone_number,
        )
        assistant = st.session_state.assistants[assistant_name]
        agent = TelegramAIAgent(assistant, telegram_config, logger=logger)

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
