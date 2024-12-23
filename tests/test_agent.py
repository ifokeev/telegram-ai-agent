from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from phi.llm.openai.chat import OpenAIChat

from telegram_ai_agent.agent import TelegramAIAgent
from telegram_ai_agent.config import TelegramConfig


@pytest.fixture
def mock_assistant():
    assistant = MagicMock()
    # Create a mock OpenAIChat object
    mock_openai_chat = MagicMock(spec=OpenAIChat)
    mock_openai_chat.__class__ = OpenAIChat
    mock_openai_chat.api_key = "mock_api_key"
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


@pytest.fixture
def mock_session():
    with patch("telegram_ai_agent.agent.TelegramSession") as mock:
        session = mock.return_value
        session.start = AsyncMock()
        session.stop = AsyncMock()
        session.is_connected = MagicMock(return_value=False)
        yield session


@pytest.mark.asyncio
async def test_agent_initialization(
    mock_assistant, mock_config, mock_logger, mock_session
):
    agent = TelegramAIAgent(mock_assistant, mock_config, logger=mock_logger)
    assert agent.assistant == mock_assistant
    assert agent.config == mock_config
    assert agent.logger == mock_logger


@pytest.mark.asyncio
async def test_agent_start(mock_assistant, mock_config, mock_logger, mock_session):
    # Create the agent with the mocked session
    agent = TelegramAIAgent(
        mock_assistant, mock_config, logger=mock_logger, session=mock_session
    )

    # Test the start method
    await agent.start()

    # Verify that session.start was called
    mock_session.start.assert_called_once()
    assert hasattr(agent, "inbound")
    assert hasattr(agent, "outbound")


@pytest.mark.asyncio
async def test_agent_stop(mock_assistant, mock_config, mock_logger, mock_session):
    # Create the agent with the mocked session
    agent = TelegramAIAgent(
        mock_assistant, mock_config, logger=mock_logger, session=mock_session
    )

    # Test the stop method
    await agent.stop()

    # Verify that session.stop was called
    mock_session.stop.assert_called_once()


@pytest.mark.asyncio
async def test_agent_send_messages(
    mock_assistant, mock_config, mock_logger, mock_session
):
    # Create the agent with the mocked session
    agent = TelegramAIAgent(
        mock_assistant, mock_config, logger=mock_logger, session=mock_session
    )
    agent.outbound = AsyncMock()

    # Test sending messages
    recipients = ["@user1", "@user2"]
    message = "Test message"
    await agent.send_messages(recipients, message)

    # Verify that outbound.send_messages was called with correct arguments
    agent.outbound.send_messages.assert_called_once_with(recipients, message, 0)


@pytest.mark.asyncio
async def test_agent_process_incoming_messages(
    mock_assistant, mock_config, mock_logger, mock_session
):
    # Create the agent with the mocked session
    agent = TelegramAIAgent(
        mock_assistant, mock_config, logger=mock_logger, session=mock_session
    )
    agent.inbound = AsyncMock()

    # Test processing incoming messages
    await agent.process_incoming_messages()

    # Verify that inbound.process_messages was called with correct arguments
    agent.inbound.process_messages.assert_called_once_with(mock_assistant)


@pytest.mark.asyncio
async def test_agent_run(mock_assistant, mock_config, mock_logger, mock_session):
    # Create the agent with the mocked session
    agent = TelegramAIAgent(
        mock_assistant, mock_config, logger=mock_logger, session=mock_session
    )
    agent.start = AsyncMock()
    agent.process_incoming_messages = AsyncMock()
    mock_session.run_until_disconnected = AsyncMock()

    # Test the run method
    await agent.run()

    # Verify that all required methods were called
    agent.start.assert_called_once()
    agent.process_incoming_messages.assert_called_once()
    mock_session.run_until_disconnected.assert_called_once()
