import multiprocessing
import os
import signal
import asyncio
from .assistant import get_assistant_by_id, update_assistant_status
from .telegram_config import get_telegram_config_by_id
from telegram_ai_agent import TelegramAIAgent, TelegramConfig
from phi.llm.openai.chat import OpenAIChat
from phi.assistant.assistant import Assistant
import logging


def run_agent_process(assistant_id):
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(f"AgentProcess-{assistant_id}")

    # Get the assistant and telegram config from the database
    assistant_data = get_assistant_by_id(assistant_id)
    telegram_config_data = get_telegram_config_by_id(assistant_data.telegram_config_id)

    # Create Assistant and TelegramConfig instances
    openai_chat = OpenAIChat(api_key=assistant_data.api_key)
    assistant = Assistant(
        llm=openai_chat,
        run_id=assistant_data.name,
        description=assistant_data.description,
        instructions=assistant_data.instructions.split("\n"),
        add_datetime_to_instructions=True,
    )

    telegram_config = TelegramConfig(
        session_name=telegram_config_data.session_file,
        api_id=telegram_config_data.api_id,
        api_hash=telegram_config_data.api_hash,
        phone_number=telegram_config_data.phone_number,
    )

    async def run_agent():
        try:
            agent = TelegramAIAgent(assistant, telegram_config, logger=logger)
            await agent.run()
        except Exception as e:
            logger.error(f"Agent {assistant_data.name} encountered an error: {e}")
        finally:
            # Update the assistant status in the database
            update_assistant_status(assistant_id, status="Stopped", pid=None)

    asyncio.run(run_agent())


def start_agent_process(assistant_id):
    # Start the agent process
    p = multiprocessing.Process(target=run_agent_process, args=(assistant_id,))
    p.start()

    # Update the assistant's status and pid in the database
    update_assistant_status(assistant_id, status="Running", pid=p.pid)


def stop_agent_process(assistant_id):
    # Get the assistant's PID from the database
    assistant_data = get_assistant_by_id(assistant_id)
    pid = assistant_data.pid
    if assistant_data.status == "Running" and pid:
        try:
            os.kill(pid, signal.SIGTERM)
            update_assistant_status(assistant_id, status="Stopped", pid=None)
            logging.info(f"Stopped agent process with PID {pid}")
        except Exception as e:
            logging.error(f"Error stopping agent process {pid}: {e}")
    else:
        logging.warning(f"No running process found for assistant ID {assistant_id}")
