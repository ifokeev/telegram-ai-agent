from copy import deepcopy

from sqlalchemy.orm import joinedload
from sqlalchemy.orm.session import make_transient

from .models import Assistant
from .session import get_db_session


def save_assistant(telegram_config_id, name, api_key, description, instructions):
    with get_db_session() as session:
        assistant = Assistant(
            telegram_config_id=telegram_config_id,
            name=name,
            api_key=api_key,
            description=description,
            instructions=instructions,
        )
        session.add(assistant)
        session.flush()  # Ensure the instance has an ID
        # Create a detached copy
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


def update_assistant(assistant_id, name, api_key, description, instructions):
    with get_db_session() as session:
        assistant = session.query(Assistant).filter_by(id=assistant_id).first()
        if assistant:
            assistant.name = name
            assistant.api_key = api_key
            assistant.description = description
            assistant.instructions = instructions
            session.flush()
            # Create a detached copy
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
