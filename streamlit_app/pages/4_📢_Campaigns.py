import streamlit as st
import asyncio
import json
from pathlib import Path
from telegram_ai_agent import TelegramAIAgent, TelegramConfig
from streamlit_app.utils.database.telegram_config import (
    get_all_telegram_configs,
    get_telegram_config,
)
from streamlit_app.utils.logging_utils import setup_logger

logger = setup_logger(__name__)

current_dir = Path(__file__).parents[1].resolve()

st.set_page_config(page_title="Manage Campaigns", page_icon="📢")

st.markdown("# Manage Campaigns")

configs = get_all_telegram_configs()
if not configs:
    st.warning("No Telegram accounts found. Please add an account first.")
else:
    file_name = st.selectbox(
        "Select Members File",
        [f.name for f in current_dir.iterdir() if f.suffix == ".csv"],
    )
    selected_phone = st.selectbox(
        "Select Telegram Account", [config.phone_number for config in configs]
    )
    assistant_name = st.selectbox(
        "Select Assistant", list(st.session_state.get("assistants", {}).keys())
    )
    message = st.text_area("Message Template")
    make_unique = st.checkbox("Make every message unique")
    limit = st.number_input("Limit (0 for no limit)", min_value=0, value=0)
    throttle = st.number_input("Throttle (seconds)", min_value=0.0, value=1.0)

    if st.button("Start Campaign"):
        config = get_telegram_config(selected_phone)
        if config and assistant_name in st.session_state.get("assistants", {}):
            telegram_config = TelegramConfig(
                session_name=str(config.session_file),
                api_id=int(config.api_id),
                api_hash=str(config.api_hash),
                phone_number=str(config.phone_number),
            )
            assistant = st.session_state.assistants[assistant_name]

            async def run_campaign():
                try:
                    agent = TelegramAIAgent(assistant, telegram_config, logger=logger)
                    await agent.start()
                    with open(current_dir / file_name, "r") as f:
                        members = json.load(f)
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
                    logger.info(
                        f"Campaign completed. Sent messages to {sent_count} members."
                    )
                    return sent_count
                except Exception as e:
                    logger.error(f"Error running campaign: {str(e)}")
                    st.error(f"An error occurred: {str(e)}")
                    return 0

            sent_count = asyncio.run(run_campaign())
            st.success(f"Campaign completed. Sent messages to {sent_count} members.")
