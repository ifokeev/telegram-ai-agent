import multiprocessing
import os
import signal
import asyncio
import logging
from .assistant import get_assistant_by_id, update_assistant_status
from ..agent_factory import create_telegram_ai_agent


def run_agent_process(assistant_id):
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(f"AgentProcess-{assistant_id}")

    # Get the assistant data from the database
    assistant_data = get_assistant_by_id(assistant_id)

    async def async_run():
        # Create the Telegram AI Agent using the factory method
        agent = await create_telegram_ai_agent(assistant_data, logger=logger)

        try:
            await agent.run()
        except Exception as e:
            logger.error(f"Agent {assistant_data.name} encountered an error: {e}")
        finally:
            # Update the assistant status in the database
            update_assistant_status(assistant_id, status="Stopped", pid=None)

    # Run the async function
    asyncio.run(async_run())


def start_agent_process(assistant_id):
    # Start the agent process
    p = multiprocessing.Process(target=run_agent_process, args=(assistant_id,))
    p.start()

    # Update the assistant's status and pid in the database
    update_assistant_status(assistant_id, status="Running", pid=p.pid)


def stop_agent_process(assistant_id):
    # Get the assistant's PID from the database
    assistant_data = get_assistant_by_id(assistant_id)
    if assistant_data and assistant_data.pid:
        pid = assistant_data.pid
        if assistant_data.status == "Running":
            try:
                os.kill(pid, signal.SIGTERM)
                update_assistant_status(assistant_id, status="Stopped", pid=None)
                logging.info(f"Stopped agent process with PID {pid}")
            except ProcessLookupError:
                logging.warning(f"Process with PID {pid} not found")
                update_assistant_status(assistant_id, status="Stopped", pid=None)
            except Exception as e:
                logging.error(f"Error stopping agent process {pid}: {e}")
        else:
            logging.warning(f"Agent {assistant_id} is not running")
    else:
        logging.warning(f"No running process found for assistant ID {assistant_id}")
