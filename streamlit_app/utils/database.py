from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
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

    assistants = relationship("Assistant", back_populates="telegram_config")


class Segment(Base):
    __tablename__ = "segments"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(String)
    users = relationship("SegmentUser", back_populates="segment")


class SegmentUser(Base):
    __tablename__ = "segment_users"

    id = Column(Integer, primary_key=True)
    segment_id = Column(Integer, ForeignKey("segments.id"))
    user_id = Column(String)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    phone = Column(String)

    segment = relationship("Segment", back_populates="users")


class Assistant(Base):
    __tablename__ = "assistants"

    id = Column(Integer, primary_key=True)
    telegram_config_id = Column(Integer, ForeignKey("telegram_configs.id"))
    name = Column(String, unique=True)
    api_key = Column(String)
    description = Column(String)
    instructions = Column(String)

    telegram_config = relationship("TelegramConfigDB", back_populates="assistants")


# Create engine and session
engine = create_engine(
    f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False}
)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


# Existing Telegram config methods
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


# New segment-related methods
def create_segment(name, description):
    session = Session()
    try:
        segment = Segment(name=name, description=description)
        session.add(segment)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_all_segments():
    session = Session()
    try:
        return session.query(Segment).all()
    finally:
        session.close()


def add_users_to_segment(segment_id, user_data):
    session = Session()
    try:
        for user in user_data:
            segment_user = SegmentUser(
                segment_id=segment_id,
                user_id=user["id"],
                username=user["username"],
                first_name=user["first_name"],
                last_name=user["last_name"],
                phone=user["phone"],
            )
            session.add(segment_user)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_segment_user_count(segment_id):
    session = Session()
    try:
        return session.query(SegmentUser).filter_by(segment_id=segment_id).count()
    finally:
        session.close()


def update_segment(segment_id, new_name, new_description):
    session = Session()
    try:
        segment = session.query(Segment).filter_by(id=segment_id).first()
        if segment:
            segment.name = new_name
            segment.description = new_description
            session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def delete_segment(segment_id):
    session = Session()
    try:
        segment = session.query(Segment).filter_by(id=segment_id).first()
        if segment:
            session.delete(segment)
            session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_segment_users(segment_id):
    session = Session()
    try:
        return session.query(SegmentUser).filter_by(segment_id=segment_id).all()
    finally:
        session.close()


def remove_user_from_segment(segment_id, user_id):
    session = Session()
    try:
        user = (
            session.query(SegmentUser)
            .filter_by(segment_id=segment_id, user_id=user_id)
            .first()
        )
        if user:
            session.delete(user)
            session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


# Add these new functions
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
            .filter_by(telegram_config_id=telegram_config_id)
            .all()
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


# Add this new function to the existing file


def add_user_to_segment(segment_id, user_id, username, first_name, last_name, phone):
    session = Session()
    try:
        segment_user = SegmentUser(
            segment_id=segment_id,
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
        )
        session.add(segment_user)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
