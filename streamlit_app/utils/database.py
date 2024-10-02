from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path

# Get the directory of the current script
current_dir = Path(__file__).parent.resolve()

# Set the SQLite database path relative to the current directory
DB_PATH = current_dir / "sqlite.db"

# Ensure the directory for the database exists
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# Database setup
Base = declarative_base()


class TelegramConfigDB(Base):
    __tablename__ = "telegram_configs"

    id = Column(Integer, primary_key=True)
    phone_number = Column(String, unique=True)
    api_id = Column(Integer)
    api_hash = Column(String)
    session_file = Column(String)


# Create engine and session
engine = create_engine(
    f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False}
)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


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
