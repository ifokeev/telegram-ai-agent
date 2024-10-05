from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()


class TelegramConfigDB(Base):
    __tablename__ = "telegram_configs"

    id = Column(Integer, primary_key=True)
    phone_number = Column(String, unique=True)
    api_id = Column(Integer)
    api_hash = Column(String)
    session_file = Column(String)

    assistants = relationship("Assistant", back_populates="telegram_config")


class Assistant(Base):
    __tablename__ = "assistants"

    id = Column(Integer, primary_key=True)
    telegram_config_id = Column(Integer, ForeignKey("telegram_configs.id"))
    name = Column(String, unique=True)
    api_key = Column(String)
    description = Column(String)
    instructions = Column(String)
    status = Column(String, default="Stopped")
    pid = Column(Integer, nullable=True)

    telegram_config = relationship("TelegramConfigDB", back_populates="assistants")
    # Removed the relationship to Job model:
    # job = relationship("Job", back_populates="assistant", uselist=False)


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
