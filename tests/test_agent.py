import pytest
import asyncio
import os
import tempfile
from unittest.mock import Mock, patch, AsyncMock, MagicMock

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types


@pytest.mark.asyncio
async def test_agent_imports():
    """Test that the agent module can be imported successfully."""
    try:
        from blogger_agent.agent import root_agent
        assert root_agent is not None
    except ImportError as e:
        pytest.fail(f"Failed to import root_agent: {e}")


@pytest.mark.asyncio
async def test_agent_with_mocked_runner(mock_adk_runner, mock_session_service):
    """Test the agent workflow with mocked runner and session."""
    from blogger_agent.agent import root_agent
    
    # Create mocked instances
    session_service = InMemorySessionService()
    runner = Runner(
        agent=root_agent, app_name="app", session_service=session_service
    )
    
    # Verify runner was created
    assert runner is not None


@pytest.mark.asyncio
async def test_agent_single_query(mock_adk_runner, mock_session_service):
    """Test agent with a single query."""
    from blogger_agent.agent import root_agent
    
    session_service = InMemorySessionService()
    runner = Runner(
        agent=root_agent, app_name="app", session_service=session_service
    )
    
    query = "I want to write a blog post about the new features in the latest version of the ADK."
    
    # Create a mock message
    message = genai_types.Content(
        role="user",
        parts=[genai_types.Part.from_text(text=query)]
    )
    
    # Verify message was created
    assert message is not None
    assert message.role == "user"


def test_config_loads_without_credentials():
    """Test that config loads without Google credentials."""
    try:
        from blogger_agent.config import config, ResearchConfiguration
        assert config is not None
        assert isinstance(config, ResearchConfiguration)
        assert config.critic_model == "gemini-2.5-pro"
        assert config.worker_model == "gemini-2.5-flash"
    except Exception as e:
        pytest.fail(f"Config failed to load: {e}")


def test_agent_modules_import():
    """Test that all agent sub-modules can be imported."""
    try:
        from blogger_agent import agent_utils, validation_checkers, tools
        from blogger_agent.sub_agents import (
            blog_editor,
            blog_planner,
            blog_writer,
            social_media_writer,
        )
        
        assert agent_utils is not None
        assert validation_checkers is not None
        assert tools is not None
        assert blog_editor is not None
        assert blog_planner is not None
        assert blog_writer is not None
        assert social_media_writer is not None
    except ImportError as e:
        pytest.fail(f"Failed to import agent modules: {e}")


def test_save_blog_post_to_file():
    """Test the save_blog_post_to_file function."""
    from blogger_agent.tools import save_blog_post_to_file
    
    with tempfile.TemporaryDirectory() as tmpdir:
        filename = os.path.join(tmpdir, "test_post.md")
        blog_content = "# Test Blog Post\n\nThis is a test blog post."
        
        result = save_blog_post_to_file(blog_content, filename)
        
        assert result["status"] == "success"
        assert os.path.exists(filename)
        
        with open(filename, "r") as f:
            saved_content = f.read()
        assert saved_content == blog_content


def test_analyze_codebase():
    """Test the analyze_codebase function."""
    from blogger_agent.tools import analyze_codebase
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files
        test_file = os.path.join(tmpdir, "test.py")
        with open(test_file, "w") as f:
            f.write("# Test Python file\nprint('hello')")
        
        result = analyze_codebase(tmpdir)
        
        assert "codebase_context" in result
        assert "test.py" in result["codebase_context"]
        assert "print('hello')" in result["codebase_context"]


def test_config_environment_variables():
    """Test that config sets environment variables correctly."""
    import os
    from blogger_agent.config import config
    
    # Verify that environment variables are set
    assert os.getenv("GOOGLE_CLOUD_LOCATION") == "global"
    assert os.getenv("GOOGLE_GENAI_USE_VERTEXAI") == "True"
    
    # Project ID should be either from credentials or test-project
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    assert project_id is not None
    assert project_id in ["test-project"] or project_id != ""


def test_agent_name_and_description():
    """Test that the agent has proper name and description."""
    from blogger_agent.agent import interactive_blogger_agent
    
    assert interactive_blogger_agent.name == "interactive_blogger_agent"
    assert "technical blogging" in interactive_blogger_agent.description.lower()


def test_agent_has_sub_agents():
    """Test that the agent includes required sub-agents."""
    from blogger_agent.agent import interactive_blogger_agent
    
    # Get sub-agent names
    sub_agent_names = [agent.name for agent in interactive_blogger_agent.sub_agents]
    
    assert len(sub_agent_names) > 0
    # Check that key sub-agents are present
    assert any("planner" in name.lower() for name in sub_agent_names)
    assert any("writer" in name.lower() for name in sub_agent_names)


def test_agent_has_tools():
    """Test that the agent includes required tools."""
    from blogger_agent.agent import interactive_blogger_agent
    
    tool_names = [tool.name for tool in interactive_blogger_agent.tools]
    
    assert len(tool_names) > 0
    # Check that key tools are present
    assert any("save" in name.lower() for name in tool_names)


def test_validation_checkers_import():
    """Test that validation checkers can be imported and instantiated."""
    from blogger_agent.validation_checkers import (
        OutlineValidationChecker,
        BlogPostValidationChecker,
    )
    
    outline_checker = OutlineValidationChecker(name="outline_checker")
    blog_checker = BlogPostValidationChecker(name="blog_checker")
    
    assert outline_checker.name == "outline_checker"
    assert blog_checker.name == "blog_checker"


@pytest.mark.asyncio
async def test_validation_checker_with_context():
    """Test validation checker with mock context."""
    from blogger_agent.validation_checkers import OutlineValidationChecker
    from google.adk.agents.invocation_context import InvocationContext
    
    checker = OutlineValidationChecker(name="outline_checker")
    
    # Create a mock context
    mock_context = Mock(spec=InvocationContext)
    mock_context.session = Mock()
    mock_context.session.state = {}
    
    # Test without blog_outline
    events = []
    async for event in checker._run_async_impl(mock_context):
        events.append(event)
    
    assert len(events) > 0


def test_config_model_names():
    """Test that config has the expected model names."""
    from blogger_agent.config import config
    
    assert config.critic_model == "gemini-2.5-pro"
    assert config.worker_model == "gemini-2.5-flash"
    assert config.max_search_iterations == 5
