from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class TelegramConfig(Base):
    __tablename__ = "telegram_configs"

    id = Column(Integer, primary_key=True)
    phone_number = Column(String, unique=True)
    api_id = Column(Integer)
    api_hash = Column(String)
    session_file = Column(String)

    assistants = relationship(
        "Assistant", back_populates="telegram_config", cascade="all, delete-orphan"
    )
    campaigns = relationship(
        "Campaign", back_populates="telegram_config", cascade="all, delete-orphan"
    )


class Assistant(Base):
    __tablename__ = "assistants"

    id = Column(Integer, primary_key=True)
    telegram_config_id = Column(
        Integer, ForeignKey("telegram_configs.id", ondelete="CASCADE")
    )
    name = Column(String, unique=True)
    api_key = Column(String)
    description = Column(String)
    instructions = Column(String)
    status = Column(String, default="Stopped")
    pid = Column(Integer, nullable=True)

    # Updated proxy settings
    proxy_type = Column(String, nullable=True)  # socks5, socks4, http
    proxy_addr = Column(String, nullable=True)
    proxy_port = Column(Integer, nullable=True)
    proxy_username = Column(String, nullable=True)
    proxy_password = Column(String, nullable=True)
    proxy_rdns = Column(Boolean, default=True)

    # Advanced settings
    timeout = Column(Integer, default=30)
    set_typing = Column(Boolean, default=True)
    typing_delay_factor = Column(Float, default=0.05)
    typing_delay_max = Column(Float, default=30.0)
    inter_chunk_delay_min = Column(Float, default=1.5)
    inter_chunk_delay_max = Column(Float, default=4.0)
    min_messages = Column(Integer, default=1)
    max_messages = Column(Integer, default=3)
    min_typing_speed = Column(Float, default=100.0)
    max_typing_speed = Column(Float, default=200.0)
    min_burst_length = Column(Integer, default=5)
    max_burst_length = Column(Integer, default=15)
    min_pause_duration = Column(Float, default=0.5)
    max_pause_duration = Column(Float, default=2.0)
    read_delay_factor = Column(Float, default=0.05)
    min_read_delay = Column(Float, default=0.5)
    max_read_delay = Column(Float, default=2.0)
    chat_history_limit = Column(Integer, default=100)

    telegram_config = relationship("TelegramConfig", back_populates="assistants")
    campaigns = relationship(
        "Campaign", back_populates="assistant", cascade="all, delete-orphan"
    )


class Segment(Base):
    __tablename__ = "segments"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(String)
    users = relationship(
        "SegmentUser", back_populates="segment", cascade="all, delete-orphan"
    )
    campaigns = relationship(
        "Campaign", back_populates="segment", cascade="all, delete-orphan"
    )


class SegmentUser(Base):
    __tablename__ = "segment_users"

    id = Column(Integer, primary_key=True)
    segment_id = Column(Integer, ForeignKey("segments.id", ondelete="CASCADE"))
    user_id = Column(String)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    phone = Column(String)

    segment = relationship("Segment", back_populates="users")


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True)
    telegram_config_id = Column(
        Integer, ForeignKey("telegram_configs.id", ondelete="CASCADE")
    )
    segment_id = Column(Integer, ForeignKey("segments.id", ondelete="CASCADE"))
    assistant_id = Column(Integer, ForeignKey("assistants.id", ondelete="CASCADE"))
    message_template = Column(String)
    make_unique = Column(Boolean)
    throttle = Column(Float)

    telegram_config = relationship("TelegramConfig", back_populates="campaigns")
    segment = relationship("Segment", back_populates="campaigns")
    assistant = relationship("Assistant", back_populates="campaigns")
    recipients = relationship(
        "CampaignRecipient", back_populates="campaign", cascade="all, delete-orphan"
    )


class CampaignRecipient(Base):
    __tablename__ = "campaign_recipients"

    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id", ondelete="CASCADE"))
    user_id = Column(String)
    username = Column(String)
    status = Column(String, default="Pending")
    sent_at = Column(DateTime, nullable=True)

    campaign = relationship("Campaign", back_populates="recipients")
