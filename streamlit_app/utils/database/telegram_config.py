from .session import Session
from .models import TelegramConfigDB


def save_telegram_config(phone_number, api_id, api_hash, session_file):
    session = Session()
    try:
        config = TelegramConfigDB(
            phone_number=phone_number,
            api_id=api_id,
            api_hash=api_hash,
            session_file=session_file,
        )
        session.add(config)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_telegram_config(phone_number):
    session = Session()
    try:
        return (
            session.query(TelegramConfigDB).filter_by(phone_number=phone_number).first()
        )
    finally:
        session.close()


def get_telegram_config_by_id(config_id):
    session = Session()
    try:
        return session.query(TelegramConfigDB).filter_by(id=config_id).first()
    finally:
        session.close()


def get_all_telegram_configs():
    session = Session()
    try:
        return session.query(TelegramConfigDB).all()
    finally:
        session.close()


def delete_telegram_config(phone_number):
    session = Session()
    try:
        config = (
            session.query(TelegramConfigDB).filter_by(phone_number=phone_number).first()
        )
        if config:
            session.delete(config)
            session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
