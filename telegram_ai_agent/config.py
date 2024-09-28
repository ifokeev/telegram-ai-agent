from dataclasses import dataclass
from typing import Optional


@dataclass
class TelegramConfig:
    session_name: str
    api_id: int
    api_hash: str
    phone_number: str
    proxy: Optional[dict] = None
    timeout: int = 30
    set_typing: bool = True
    typing_delay_factor: float = 0.05
    typing_delay_max: float = 30.0
    inter_chunk_delay_min: float = 1.5
    inter_chunk_delay_max: float = 4.0
    min_messages: int = 1
    max_messages: int = 3
    min_typing_speed: float = 100.0  # words per minute
    max_typing_speed: float = 200.0  # words per minute
    min_burst_length: int = 5
    max_burst_length: int = 15
    min_pause_duration: float = 0.5
    max_pause_duration: float = 2.0
    read_delay_factor: float = 0.05
    min_read_delay: float = 0.5
    max_read_delay: float = 2.0
    chat_history_limit: int = 100
