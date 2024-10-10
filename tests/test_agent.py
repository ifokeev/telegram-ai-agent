import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from telegram_ai_agent.agent import TelegramAIAgent
from telegram_ai_agent.config import TelegramConfig
from phi.llm.openai.chat import OpenAIChat


@pytest.fixture
def mock_assistant():
    assistant = MagicMock()
    # Create a mock OpenAIChat object
    mock_openai_chat = MagicMock(spec=OpenAIChat)
    mock_openai_chat.__class__ = OpenAIChat
    mock_openai_chat.api_key = "mock_api_key"  # Add this line
    assistant.llm = mock_openai_chat
    return assistant


@pytest.fixture
def mock_config():
    return TelegramConfig(
        session_name="test_session",
        api_id=12345,
        api_hash="test_hash",
        phone_number="+1234567890",
    )


@pytest.fixture
def mock_logger():
    return MagicMock()


@pytest.mark.asyncio
async def test_agent_initialization(mock_assistant, mock_config, mock_logger):
    with patch("telegram_ai_agent.agent.TelegramSession") as mock_session:
        agent = TelegramAIAgent(mock_assistant, mock_config, logger=mock_logger)
        assert agent.assistant == mock_assistant
        assert agent.config == mock_config
        assert agent.logger == mock_logger


@pytest.mark.asyncio
async def test_agent_start(mock_assistant, mock_config, mock_logger):
    with patch("telegram_ai_agent.agent.TelegramSession") as mock_session:
        agent = TelegramAIAgent(mock_assistant, mock_config, logger=mock_logger)
        agent.session.start = AsyncMock()
        agent.session.start.return_value = None

        await agent.start()

        assert hasattr(agent, "inbound")
        assert hasattr(agent, "outbound")
        agent.session.start.assert_called_once()


@pytest.mark.asyncio
async def test_agent_stop(mock_assistant, mock_config, mock_logger):
    with patch("telegram_ai_agent.agent.TelegramSession") as mock_session:
        agent = TelegramAIAgent(mock_assistant, mock_config, logger=mock_logger)
        agent.session.stop = AsyncMock()

        await agent.stop()

        agent.session.stop.assert_called_once()


@pytest.mark.asyncio
async def test_agent_send_messages(mock_assistant, mock_config, mock_logger):
    with patch("telegram_ai_agent.agent.TelegramSession") as mock_session:
        agent = TelegramAIAgent(mock_assistant, mock_config, logger=mock_logger)
        agent.outbound = AsyncMock()

        recipients = ["@user1", "@user2"]
        message = "Test message"
        await agent.send_messages(recipients, message)

        agent.outbound.send_messages.assert_called_once_with(recipients, message, 0)


@pytest.mark.asyncio
async def test_agent_process_incoming_messages(
    mock_assistant, mock_config, mock_logger
):
    with patch("telegram_ai_agent.agent.TelegramSession") as mock_session:
        agent = TelegramAIAgent(mock_assistant, mock_config, logger=mock_logger)
        agent.inbound = AsyncMock()

        await agent.process_incoming_messages()

        agent.inbound.process_messages.assert_called_once_with(mock_assistant)
