from sqlalchemy.orm import joinedload

from .models import Assistant
from .session import Session


def save_assistant(telegram_config_id, name, api_key, description, instructions):
    session = Session()
    try:
        assistant = Assistant(
            telegram_config_id=telegram_config_id,
            name=name,
            api_key=api_key,
            description=description,
            instructions=instructions,
        )
        session.add(assistant)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_assistants(telegram_config_id):
    session = Session()
    try:
        return (
            session.query(Assistant)
            .options(joinedload(Assistant.telegram_config))
            .filter_by(telegram_config_id=telegram_config_id)
            .all()
        )
    finally:
        session.close()


def get_all_assistants():
    session = Session()
    try:
        return (
            session.query(Assistant)
            .options(joinedload(Assistant.telegram_config))
            .all()
        )
    finally:
        session.close()


def get_assistant_by_id(assistant_id):
    session = Session()
    try:
        return (
            session.query(Assistant)
            .options(joinedload(Assistant.telegram_config))
            .filter_by(id=assistant_id)
            .first()
        )
    finally:
        session.close()


def update_assistant(assistant_id, name, api_key, description, instructions):
    session = Session()
    try:
        assistant = session.query(Assistant).filter_by(id=assistant_id).first()
        if assistant:
            assistant.name = name
            assistant.api_key = api_key
            assistant.description = description
            assistant.instructions = instructions
            session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def delete_assistant(assistant_id):
    session = Session()
    try:
        assistant = session.query(Assistant).filter_by(id=assistant_id).first()
        if assistant:
            session.delete(assistant)
            session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def update_assistant_status(assistant_id, status, pid):
    session = Session()
    try:
        assistant = session.query(Assistant).filter_by(id=assistant_id).first()
        if assistant:
            assistant.status = status
            assistant.pid = pid
            session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
