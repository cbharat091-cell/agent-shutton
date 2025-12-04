import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import asyncio


@pytest.fixture
def mock_google_auth():
    """Mock google.auth.default to avoid credential errors."""
    with patch("google.auth.default") as mock_default:
        mock_default.return_value = (Mock(), "test-project")
        yield mock_default


@pytest.fixture
def mock_llm_response():
    """Create a mock LLM response."""
    return Mock(
        text="This is a test response from the mock LLM",
        candidates=[Mock(content=Mock(parts=[Mock(text="This is a test response from the mock LLM")]))],
    )


@pytest.fixture
def mock_genai_client():
    """Mock the Google GenAI client."""
    with patch("google.genai.Client") as mock_client:
        mock_instance = AsyncMock()
        mock_client.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_adk_runner():
    """Mock the ADK Runner for testing."""
    with patch("google.adk.runners.Runner") as mock_runner_class:
        mock_runner = AsyncMock()
        mock_runner_class.return_value = mock_runner
        
        # Create mock events for the runner
        async def mock_run_async(*args, **kwargs):
            # Yield some mock events
            event1 = Mock()
            event1.is_final_response.return_value = False
            yield event1
            
            event2 = Mock()
            event2.is_final_response.return_value = True
            event2.content = Mock(parts=[Mock(text="Mock response")])
            yield event2
        
        mock_runner.run_async = mock_run_async
        yield mock_runner_class


@pytest.fixture
def mock_session_service():
    """Mock the ADK session service."""
    with patch("google.adk.sessions.InMemorySessionService") as mock_service_class:
        mock_service = AsyncMock()
        mock_service_class.return_value = mock_service
        yield mock_service_class


@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def setup_mocks(mock_google_auth, mock_genai_client, mock_adk_runner, mock_session_service):
    """Automatically set up all mocks for tests."""
    yield
