"""
Tests for LangSmith tracing configuration and metadata passing.
"""

import os
from unittest.mock import patch

import pytest

from src.agents.base import AgentContext, AgentRole
from src.utils.llm import LLMResponse, ModelTier


class TestTracingConfiguration:
    """Tests for tracing environment variable handling."""

    def test_tracing_disabled_by_default(self):
        """Verify tracing is off when env vars not set."""
        with patch.dict(os.environ, {}, clear=True):
            # Remove any existing tracing vars
            os.environ.pop("LANGCHAIN_TRACING_V2", None)
            os.environ.pop("LANGCHAIN_API_KEY", None)
            assert os.getenv("LANGCHAIN_TRACING_V2") is None

    def test_tracing_env_vars_recognized(self):
        """Verify tracing env vars are read correctly."""
        env = {
            "LANGCHAIN_TRACING_V2": "true",
            "LANGCHAIN_API_KEY": "test-key-12345",
            "LANGCHAIN_PROJECT": "test-project",
        }
        with patch.dict(os.environ, env):
            assert os.getenv("LANGCHAIN_TRACING_V2") == "true"
            assert os.getenv("LANGCHAIN_API_KEY") == "test-key-12345"
            assert os.getenv("LANGCHAIN_PROJECT") == "test-project"


class TestAgentContextSessionId:
    """Tests for session_id field in AgentContext."""

    def test_context_accepts_session_id(self):
        """Verify AgentContext has session_id field."""
        context = AgentContext(
            show_bible="Test bible",
            creative_prompt="Test prompt",
            task_type="test_task",
            session_id="test_session_123",
        )
        assert context.session_id == "test_session_123"

    def test_context_session_id_defaults_to_none(self):
        """Verify session_id defaults to None."""
        context = AgentContext(
            show_bible="Test bible",
            creative_prompt="Test prompt",
            task_type="test_task",
        )
        assert context.session_id is None


class TestLLMMetadataParameters:
    """Tests for metadata parameters in LLM calls."""

    @pytest.mark.asyncio
    async def test_mock_llm_records_metadata(self, mock_llm):
        """Verify mock LLM records tracing metadata."""
        from langchain_core.messages import HumanMessage

        messages = [HumanMessage(content="Test message")]

        await mock_llm.acall(
            messages,
            tier=ModelTier.CREATIVE,
            run_name="test:task",
            tags=["agent:test", "task:test_task"],
            metadata={"agent_name": "Test Agent", "session_id": "session_123"},
        )

        # Verify call was recorded with metadata
        assert len(mock_llm.call_history) == 1
        call = mock_llm.call_history[0]
        assert call["run_name"] == "test:task"
        assert call["tags"] == ["agent:test", "task:test_task"]
        assert call["metadata"]["agent_name"] == "Test Agent"
        assert call["metadata"]["session_id"] == "session_123"

    @pytest.mark.asyncio
    async def test_mock_llm_works_without_metadata(self, mock_llm):
        """Verify mock LLM works when metadata is not provided."""
        from langchain_core.messages import HumanMessage

        messages = [HumanMessage(content="Test message")]

        response = await mock_llm.acall(messages, tier=ModelTier.CREATIVE)

        # Should still work
        assert response.content is not None
        assert len(mock_llm.call_history) == 1
        call = mock_llm.call_history[0]
        assert call["run_name"] is None
        assert call["tags"] is None
        assert call["metadata"] is None


class TestAgentTracingMetadata:
    """Tests for agent execution with tracing metadata."""

    @pytest.mark.asyncio
    async def test_agent_passes_metadata_to_llm(self, mock_config, mock_llm):
        """Verify agents pass tracing metadata when executing."""
        from src.agents import StaffWriterA

        agent = StaffWriterA(mock_config, mock_llm)
        context = AgentContext(
            show_bible="Test bible",
            creative_prompt="Test prompt",
            task_type="generate_pitches",
            session_id="session_456",
        )

        await agent.execute(context)

        # Verify LLM was called with metadata
        assert len(mock_llm.call_history) == 1
        call = mock_llm.call_history[0]

        # Check run_name format
        assert call["run_name"] == "staff_writer_a:generate_pitches"

        # Check tags
        assert "agent:staff_writer_a" in call["tags"]
        assert "task:generate_pitches" in call["tags"]
        assert "tier:creative" in call["tags"]

        # Check metadata
        assert call["metadata"]["agent_name"] == "Staff Writer A"
        assert call["metadata"]["agent_role"] == "staff_writer_a"
        assert call["metadata"]["task_type"] == "generate_pitches"
        assert call["metadata"]["session_id"] == "session_456"

    @pytest.mark.asyncio
    async def test_agent_handles_missing_session_id(self, mock_config, mock_llm):
        """Verify agents handle missing session_id gracefully."""
        from src.agents import ShowrunnerAgent

        agent = ShowrunnerAgent(mock_config, mock_llm)
        context = AgentContext(
            show_bible="Test bible",
            creative_prompt="Test prompt",
            task_type="select_pitch",
            # No session_id provided
        )

        await agent.execute(context)

        # Verify LLM was called and metadata has "unknown" for session_id
        assert len(mock_llm.call_history) == 1
        call = mock_llm.call_history[0]
        assert call["metadata"]["session_id"] == "unknown"
