from copy import deepcopy

from sqlalchemy.orm import joinedload
from sqlalchemy.orm.session import make_transient

from .models import Assistant
from .session import get_db_session


def save_assistant(
    telegram_config_id,
    name,
    api_key,
    description,
    instructions,
    proxy_scheme=None,
    proxy_hostname=None,
    proxy_port=None,
    timeout=30,
    set_typing=True,
    typing_delay_factor=0.05,
    typing_delay_max=30.0,
    inter_chunk_delay_min=1.5,
    inter_chunk_delay_max=4.0,
    min_messages=1,
    max_messages=3,
    min_typing_speed=100.0,
    max_typing_speed=200.0,
    min_burst_length=5,
    max_burst_length=15,
    min_pause_duration=0.5,
    max_pause_duration=2.0,
    read_delay_factor=0.05,
    min_read_delay=0.5,
    max_read_delay=2.0,
    chat_history_limit=100,
):
    with get_db_session() as session:
        assistant = Assistant(
            telegram_config_id=telegram_config_id,
            name=name,
            api_key=api_key,
            description=description,
            instructions=instructions,
            proxy_scheme=proxy_scheme,
            proxy_hostname=proxy_hostname,
            proxy_port=proxy_port,
            # Advanced settings
            timeout=timeout,
            set_typing=set_typing,
            typing_delay_factor=typing_delay_factor,
            typing_delay_max=typing_delay_max,
            inter_chunk_delay_min=inter_chunk_delay_min,
            inter_chunk_delay_max=inter_chunk_delay_max,
            min_messages=min_messages,
            max_messages=max_messages,
            min_typing_speed=min_typing_speed,
            max_typing_speed=max_typing_speed,
            min_burst_length=min_burst_length,
            max_burst_length=max_burst_length,
            min_pause_duration=min_pause_duration,
            max_pause_duration=max_pause_duration,
            read_delay_factor=read_delay_factor,
            min_read_delay=min_read_delay,
            max_read_delay=max_read_delay,
            chat_history_limit=chat_history_limit,
        )
        session.add(assistant)
        session.flush()
        detached = deepcopy(assistant)
        make_transient(detached)
        return detached


def get_assistants(telegram_config_id):
    with get_db_session() as session:
        assistants = (
            session.query(Assistant)
            .options(joinedload(Assistant.telegram_config))
            .filter_by(telegram_config_id=telegram_config_id)
            .all()
        )
        # Create detached copies
        detached_assistants = []
        for assistant in assistants:
            detached = deepcopy(assistant)
            make_transient(detached)
            detached_assistants.append(detached)
        return detached_assistants


def get_all_assistants():
    with get_db_session() as session:
        assistants = (
            session.query(Assistant)
            .options(joinedload(Assistant.telegram_config))
            .all()
        )
        # Create detached copies
        detached_assistants = []
        for assistant in assistants:
            detached = deepcopy(assistant)
            make_transient(detached)
            detached_assistants.append(detached)
        return detached_assistants


def get_assistant_by_id(assistant_id):
    with get_db_session() as session:
        assistant = (
            session.query(Assistant)
            .options(joinedload(Assistant.telegram_config))
            .filter_by(id=assistant_id)
            .first()
        )
        if assistant:
            # Create a detached copy
            detached = deepcopy(assistant)
            make_transient(detached)
            return detached
        return None


def update_assistant(
    assistant_id,
    name,
    api_key,
    description,
    instructions,
    proxy_scheme=None,
    proxy_hostname=None,
    proxy_port=None,
    timeout=30,
    set_typing=True,
    typing_delay_factor=0.05,
    typing_delay_max=30.0,
    inter_chunk_delay_min=1.5,
    inter_chunk_delay_max=4.0,
    min_messages=1,
    max_messages=3,
    min_typing_speed=100.0,
    max_typing_speed=200.0,
    min_burst_length=5,
    max_burst_length=15,
    min_pause_duration=0.5,
    max_pause_duration=2.0,
    read_delay_factor=0.05,
    min_read_delay=0.5,
    max_read_delay=2.0,
    chat_history_limit=100,
):
    with get_db_session() as session:
        assistant = session.query(Assistant).filter_by(id=assistant_id).first()
        if assistant:
            assistant.name = name
            assistant.api_key = api_key
            assistant.description = description
            assistant.instructions = instructions
            assistant.proxy_scheme = proxy_scheme
            assistant.proxy_hostname = proxy_hostname
            assistant.proxy_port = proxy_port
            # Update advanced settings
            assistant.timeout = timeout
            assistant.set_typing = set_typing
            assistant.typing_delay_factor = typing_delay_factor
            assistant.typing_delay_max = typing_delay_max
            assistant.inter_chunk_delay_min = inter_chunk_delay_min
            assistant.inter_chunk_delay_max = inter_chunk_delay_max
            assistant.min_messages = min_messages
            assistant.max_messages = max_messages
            assistant.min_typing_speed = min_typing_speed
            assistant.max_typing_speed = max_typing_speed
            assistant.min_burst_length = min_burst_length
            assistant.max_burst_length = max_burst_length
            assistant.min_pause_duration = min_pause_duration
            assistant.max_pause_duration = max_pause_duration
            assistant.read_delay_factor = read_delay_factor
            assistant.min_read_delay = min_read_delay
            assistant.max_read_delay = max_read_delay
            assistant.chat_history_limit = chat_history_limit
            session.flush()
            detached = deepcopy(assistant)
            make_transient(detached)
            return detached
        return None


def delete_assistant(assistant_id):
    with get_db_session() as session:
        assistant = session.query(Assistant).filter_by(id=assistant_id).first()
        if assistant:
            session.delete(assistant)


def update_assistant_status(assistant_id, status, pid):
    with get_db_session() as session:
        assistant = session.query(Assistant).filter_by(id=assistant_id).first()
        if assistant:
            assistant.status = status
            assistant.pid = pid
            session.flush()
            # Create a detached copy
            detached = deepcopy(assistant)
            make_transient(detached)
            return detached
        return None
