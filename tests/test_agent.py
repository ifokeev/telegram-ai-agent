import pytest
from unittest.mock import AsyncMock, MagicMock
from telegram_ai_agent.agent import TelegramAIAgent
from telegram_ai_agent.config import TelegramConfig


@pytest.fixture
def mock_assistant():
    return MagicMock()


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
    agent = TelegramAIAgent(mock_assistant, mock_config, logger=mock_logger)
    assert agent.assistant == mock_assistant
    assert agent.config == mock_config
    assert agent.logger == mock_logger


@pytest.mark.asyncio
async def test_agent_start(mock_assistant, mock_config, mock_logger):
    agent = TelegramAIAgent(mock_assistant, mock_config, logger=mock_logger)
    agent.auth.authenticate = AsyncMock()
    agent.auth.authenticate.return_value = MagicMock()

    await agent.start()

    assert agent.client is not None
    assert agent.inbound is not None
    assert agent.outbound is not None
    agent.auth.authenticate.assert_called_once()


@pytest.mark.asyncio
async def test_agent_stop(mock_assistant, mock_config, mock_logger):
    agent = TelegramAIAgent(mock_assistant, mock_config, logger=mock_logger)
    agent.client = AsyncMock()
    agent.client.is_connected.return_value = True

    await agent.stop()

    agent.client.disconnect.assert_called_once()


@pytest.mark.asyncio
async def test_agent_send_messages(mock_assistant, mock_config, mock_logger):
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
    agent = TelegramAIAgent(mock_assistant, mock_config, logger=mock_logger)
    agent.inbound = AsyncMock()

    await agent.process_incoming_messages()

    agent.inbound.process_messages.assert_called_once_with(mock_assistant)
