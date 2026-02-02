"""
Unit tests for agent implementations.

Tests the src/agents module including:
- BaseAgent abstract class functionality
- AgentRole enum and model tier mapping
- AgentContext and AgentOutput dataclasses
- All 10 concrete agent implementations
- Task instruction retrieval
- Agent execution with mocked LLM
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.agents.base import (
    AgentContext,
    AgentOutput,
    AgentRole,
    BaseAgent,
    AGENT_MODEL_TIERS,
    get_agent_description,
)
from src.agents import (
    HeadWriterAgent,
    QAAgent,
    ResearchAgent,
    ScriptCoordinatorAgent,
    SeniorWriterA,
    SeniorWriterB,
    ShowrunnerAgent,
    StaffWriterA,
    StaffWriterB,
    StoryEditorAgent,
)
from src.utils.config import Config
from src.utils.llm import LLMResponse, ModelTier


# =============================================================================
# AGENT ROLE TESTS
# =============================================================================


class TestAgentRole:
    """Tests for AgentRole enum."""

    def test_all_roles_defined(self):
        """Test that all 10 agent roles are defined."""
        expected_roles = [
            "showrunner",
            "head_writer",
            "senior_writer_a",
            "senior_writer_b",
            "staff_writer_a",
            "staff_writer_b",
            "story_editor",
            "research",
            "script_coordinator",
            "qa",
        ]
        actual_roles = [role.value for role in AgentRole]
        assert len(actual_roles) == 10
        for role in expected_roles:
            assert role in actual_roles

    def test_leadership_roles(self):
        """Test leadership tier roles."""
        assert AgentRole.SHOWRUNNER.value == "showrunner"
        assert AgentRole.HEAD_WRITER.value == "head_writer"

    def test_creative_roles(self):
        """Test creative tier roles."""
        assert AgentRole.SENIOR_WRITER_A.value == "senior_writer_a"
        assert AgentRole.SENIOR_WRITER_B.value == "senior_writer_b"
        assert AgentRole.STAFF_WRITER_A.value == "staff_writer_a"
        assert AgentRole.STAFF_WRITER_B.value == "staff_writer_b"

    def test_support_roles(self):
        """Test support tier roles."""
        assert AgentRole.STORY_EDITOR.value == "story_editor"
        assert AgentRole.RESEARCH.value == "research"

    def test_qa_roles(self):
        """Test QA tier roles."""
        assert AgentRole.SCRIPT_COORDINATOR.value == "script_coordinator"
        assert AgentRole.QA.value == "qa"


class TestAgentModelTiers:
    """Tests for agent model tier mapping."""

    def test_all_roles_have_tier(self):
        """Test that all roles have a model tier assigned."""
        for role in AgentRole:
            assert role in AGENT_MODEL_TIERS

    def test_leadership_uses_creative_tier(self):
        """Test that leadership roles use creative model tier."""
        assert AGENT_MODEL_TIERS[AgentRole.SHOWRUNNER] == ModelTier.CREATIVE
        assert AGENT_MODEL_TIERS[AgentRole.HEAD_WRITER] == ModelTier.CREATIVE

    def test_creative_roles_use_creative_tier(self):
        """Test that creative roles use creative model tier."""
        creative_roles = [
            AgentRole.SENIOR_WRITER_A,
            AgentRole.SENIOR_WRITER_B,
            AgentRole.STAFF_WRITER_A,
            AgentRole.STAFF_WRITER_B,
        ]
        for role in creative_roles:
            assert AGENT_MODEL_TIERS[role] == ModelTier.CREATIVE

    def test_support_roles_use_support_tier(self):
        """Test that support roles use support model tier."""
        support_roles = [
            AgentRole.STORY_EDITOR,
            AgentRole.RESEARCH,
        ]
        for role in support_roles:
            assert AGENT_MODEL_TIERS[role] == ModelTier.SUPPORT

    def test_qa_roles_use_support_tier(self):
        """Test that QA roles use support model tier."""
        qa_roles = [
            AgentRole.SCRIPT_COORDINATOR,
            AgentRole.QA,
        ]
        for role in qa_roles:
            assert AGENT_MODEL_TIERS[role] == ModelTier.SUPPORT


# =============================================================================
# AGENT CONTEXT TESTS
# =============================================================================


class TestAgentContext:
    """Tests for AgentContext dataclass."""

    def test_minimal_context(self):
        """Test creating context with minimal required fields."""
        context = AgentContext(
            show_bible="# Show Bible",
            creative_prompt="# Creative Prompt",
            task_type="test_task",
        )
        assert context.show_bible == "# Show Bible"
        assert context.creative_prompt == "# Creative Prompt"
        assert context.task_type == "test_task"
        assert context.previous_output is None
        assert context.direction_notes is None
        assert context.additional_context == {}

    def test_full_context(self):
        """Test creating context with all fields."""
        context = AgentContext(
            show_bible="# Show Bible",
            creative_prompt="# Creative Prompt",
            task_type="test_task",
            previous_output="Previous stage output...",
            direction_notes="Focus on character development",
            additional_context={"key": "value"},
        )
        assert context.previous_output == "Previous stage output..."
        assert context.direction_notes == "Focus on character development"
        assert context.additional_context == {"key": "value"}

    def test_additional_context_defaults_to_empty_dict(self):
        """Test that additional_context defaults to empty dict."""
        context = AgentContext(
            show_bible="bible",
            creative_prompt="prompt",
            task_type="task",
        )
        # Should be empty dict, not None
        assert isinstance(context.additional_context, dict)
        assert len(context.additional_context) == 0


# =============================================================================
# AGENT OUTPUT TESTS
# =============================================================================


class TestAgentOutput:
    """Tests for AgentOutput dataclass."""

    def test_successful_output(self):
        """Test creating successful agent output."""
        output = AgentOutput(
            agent_role=AgentRole.SHOWRUNNER,
            task_type="select_pitch",
            content="Selected pitch #1...",
            success=True,
            token_usage={"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150},
            metadata={"model": "claude-sonnet"},
        )
        assert output.agent_role == AgentRole.SHOWRUNNER
        assert output.task_type == "select_pitch"
        assert output.content == "Selected pitch #1..."
        assert output.success is True
        assert output.error_message is None
        assert output.token_usage["total_tokens"] == 150

    def test_failed_output(self):
        """Test creating failed agent output."""
        output = AgentOutput(
            agent_role=AgentRole.RESEARCH,
            task_type="gather_references",
            content="",
            success=False,
            error_message="API rate limit exceeded",
        )
        assert output.success is False
        assert output.error_message == "API rate limit exceeded"
        assert output.content == ""

    def test_output_string_representation(self):
        """Test AgentOutput string representation."""
        output = AgentOutput(
            agent_role=AgentRole.HEAD_WRITER,
            task_type="compile_pitches",
            content="content",
            success=True,
        )
        assert "head_writer" in str(output)
        assert "compile_pitches" in str(output)
        assert "SUCCESS" in str(output)

    def test_failed_output_string_representation(self):
        """Test failed AgentOutput string representation."""
        output = AgentOutput(
            agent_role=AgentRole.QA,
            task_type="validate",
            content="",
            success=False,
        )
        assert "FAILED" in str(output)

    def test_metadata_defaults_to_empty_dict(self):
        """Test that metadata defaults to empty dict."""
        output = AgentOutput(
            agent_role=AgentRole.SHOWRUNNER,
            task_type="test",
            content="content",
            success=True,
        )
        assert isinstance(output.metadata, dict)


# =============================================================================
# GET AGENT DESCRIPTION TESTS
# =============================================================================


class TestGetAgentDescription:
    """Tests for get_agent_description function."""

    def test_all_roles_have_descriptions(self):
        """Test that all roles have descriptions."""
        for role in AgentRole:
            desc = get_agent_description(role)
            assert isinstance(desc, str)
            assert len(desc) > 10

    def test_showrunner_description(self):
        """Test Showrunner description."""
        desc = get_agent_description(AgentRole.SHOWRUNNER)
        assert "authority" in desc.lower() or "decision" in desc.lower()

    def test_head_writer_description(self):
        """Test Head Writer description."""
        desc = get_agent_description(AgentRole.HEAD_WRITER)
        assert "manager" in desc.lower() or "synthesizer" in desc.lower()


# =============================================================================
# CONCRETE AGENT TESTS
# =============================================================================


class TestShowrunnerAgent:
    """Tests for ShowrunnerAgent."""

    def test_initialization(self, mock_config: Config, mock_llm):
        """Test Showrunner agent initialization."""
        agent = ShowrunnerAgent(mock_config, mock_llm)
        assert agent.role == AgentRole.SHOWRUNNER
        assert agent.model_tier == ModelTier.CREATIVE
        assert "Showrunner" in agent.name

    def test_system_prompt(self, mock_config: Config, mock_llm):
        """Test Showrunner system prompt."""
        agent = ShowrunnerAgent(mock_config, mock_llm)
        prompt = agent.get_system_prompt()
        assert "SHOWRUNNER" in prompt
        assert "creative authority" in prompt.lower()
        assert "final" in prompt.lower()

    def test_task_instructions_select_pitch(self, mock_config: Config, mock_llm):
        """Test Showrunner select_pitch task instructions."""
        agent = ShowrunnerAgent(mock_config, mock_llm)
        context = AgentContext(
            show_bible="bible",
            creative_prompt="prompt",
            task_type="select_pitch",
        )
        instructions = agent.get_task_instructions("select_pitch", context)
        assert "SELECT" in instructions or "PITCH" in instructions
        assert "OUTPUT FORMAT" in instructions

    def test_task_instructions_review_draft(self, mock_config: Config, mock_llm):
        """Test Showrunner review_draft task instructions."""
        agent = ShowrunnerAgent(mock_config, mock_llm)
        context = AgentContext(
            show_bible="bible",
            creative_prompt="prompt",
            task_type="review_draft",
        )
        instructions = agent.get_task_instructions("review_draft", context)
        assert "REVIEW" in instructions or "DRAFT" in instructions

    def test_task_instructions_final_approval(self, mock_config: Config, mock_llm):
        """Test Showrunner final_approval task instructions."""
        agent = ShowrunnerAgent(mock_config, mock_llm)
        context = AgentContext(
            show_bible="bible",
            creative_prompt="prompt",
            task_type="final_approval",
        )
        instructions = agent.get_task_instructions("final_approval", context)
        assert "APPROVAL" in instructions or "APPROVED" in instructions

    def test_unknown_task_type(self, mock_config: Config, mock_llm):
        """Test Showrunner with unknown task type."""
        agent = ShowrunnerAgent(mock_config, mock_llm)
        context = AgentContext(
            show_bible="bible",
            creative_prompt="prompt",
            task_type="unknown_task",
        )
        instructions = agent.get_task_instructions("unknown_task", context)
        assert "unknown_task" in instructions


class TestHeadWriterAgent:
    """Tests for HeadWriterAgent."""

    def test_initialization(self, mock_config: Config, mock_llm):
        """Test Head Writer agent initialization."""
        agent = HeadWriterAgent(mock_config, mock_llm)
        assert agent.role == AgentRole.HEAD_WRITER
        assert agent.model_tier == ModelTier.CREATIVE

    def test_system_prompt(self, mock_config: Config, mock_llm):
        """Test Head Writer system prompt."""
        agent = HeadWriterAgent(mock_config, mock_llm)
        prompt = agent.get_system_prompt()
        assert "HEAD WRITER" in prompt
        assert "manage" in prompt.lower() or "orchestrate" in prompt.lower()


class TestSeniorWriterA:
    """Tests for SeniorWriterA (premise/character specialist)."""

    def test_initialization(self, mock_config: Config, mock_llm):
        """Test Senior Writer A initialization."""
        agent = SeniorWriterA(mock_config, mock_llm)
        assert agent.role == AgentRole.SENIOR_WRITER_A
        assert agent.model_tier == ModelTier.CREATIVE

    def test_system_prompt(self, mock_config: Config, mock_llm):
        """Test Senior Writer A system prompt."""
        agent = SeniorWriterA(mock_config, mock_llm)
        prompt = agent.get_system_prompt()
        assert "SENIOR WRITER A" in prompt
        assert "premise" in prompt.lower() or "character" in prompt.lower()


class TestSeniorWriterB:
    """Tests for SeniorWriterB (dialogue specialist)."""

    def test_initialization(self, mock_config: Config, mock_llm):
        """Test Senior Writer B initialization."""
        agent = SeniorWriterB(mock_config, mock_llm)
        assert agent.role == AgentRole.SENIOR_WRITER_B
        assert agent.model_tier == ModelTier.CREATIVE

    def test_system_prompt(self, mock_config: Config, mock_llm):
        """Test Senior Writer B system prompt."""
        agent = SeniorWriterB(mock_config, mock_llm)
        prompt = agent.get_system_prompt()
        assert "SENIOR WRITER" in prompt and "B" in prompt
        assert "dialogue" in prompt.lower()


class TestStaffWriterA:
    """Tests for StaffWriterA (pitch generator)."""

    def test_initialization(self, mock_config: Config, mock_llm):
        """Test Staff Writer A initialization."""
        agent = StaffWriterA(mock_config, mock_llm)
        assert agent.role == AgentRole.STAFF_WRITER_A
        assert agent.model_tier == ModelTier.CREATIVE

    def test_system_prompt(self, mock_config: Config, mock_llm):
        """Test Staff Writer A system prompt."""
        agent = StaffWriterA(mock_config, mock_llm)
        prompt = agent.get_system_prompt()
        assert "STAFF WRITER A" in prompt
        assert "pitch" in prompt.lower()


class TestStaffWriterB:
    """Tests for StaffWriterB (structure specialist)."""

    def test_initialization(self, mock_config: Config, mock_llm):
        """Test Staff Writer B initialization."""
        agent = StaffWriterB(mock_config, mock_llm)
        assert agent.role == AgentRole.STAFF_WRITER_B
        assert agent.model_tier == ModelTier.CREATIVE

    def test_system_prompt(self, mock_config: Config, mock_llm):
        """Test Staff Writer B system prompt."""
        agent = StaffWriterB(mock_config, mock_llm)
        prompt = agent.get_system_prompt()
        assert "STAFF WRITER" in prompt and "B" in prompt
        assert "structure" in prompt.lower()


class TestStoryEditorAgent:
    """Tests for StoryEditorAgent."""

    def test_initialization(self, mock_config: Config, mock_llm):
        """Test Story Editor initialization."""
        agent = StoryEditorAgent(mock_config, mock_llm)
        assert agent.role == AgentRole.STORY_EDITOR
        assert agent.model_tier == ModelTier.SUPPORT

    def test_system_prompt(self, mock_config: Config, mock_llm):
        """Test Story Editor system prompt."""
        agent = StoryEditorAgent(mock_config, mock_llm)
        prompt = agent.get_system_prompt()
        assert "STORY EDITOR" in prompt
        assert "continuity" in prompt.lower() or "consistency" in prompt.lower()


class TestResearchAgent:
    """Tests for ResearchAgent."""

    def test_initialization(self, mock_config: Config, mock_llm):
        """Test Research Agent initialization."""
        agent = ResearchAgent(mock_config, mock_llm)
        assert agent.role == AgentRole.RESEARCH
        assert agent.model_tier == ModelTier.SUPPORT

    def test_system_prompt(self, mock_config: Config, mock_llm):
        """Test Research Agent system prompt."""
        agent = ResearchAgent(mock_config, mock_llm)
        prompt = agent.get_system_prompt()
        assert "RESEARCH" in prompt
        assert "fact" in prompt.lower() or "reference" in prompt.lower()


class TestScriptCoordinatorAgent:
    """Tests for ScriptCoordinatorAgent."""

    def test_initialization(self, mock_config: Config, mock_llm):
        """Test Script Coordinator initialization."""
        agent = ScriptCoordinatorAgent(mock_config, mock_llm)
        assert agent.role == AgentRole.SCRIPT_COORDINATOR
        assert agent.model_tier == ModelTier.SUPPORT

    def test_system_prompt(self, mock_config: Config, mock_llm):
        """Test Script Coordinator system prompt."""
        agent = ScriptCoordinatorAgent(mock_config, mock_llm)
        prompt = agent.get_system_prompt()
        assert "SCRIPT COORDINATOR" in prompt
        assert "format" in prompt.lower()


class TestQAAgent:
    """Tests for QAAgent."""

    def test_initialization(self, mock_config: Config, mock_llm):
        """Test QA Agent initialization."""
        agent = QAAgent(mock_config, mock_llm)
        assert agent.role == AgentRole.QA
        assert agent.model_tier == ModelTier.SUPPORT

    def test_system_prompt(self, mock_config: Config, mock_llm):
        """Test QA Agent system prompt."""
        agent = QAAgent(mock_config, mock_llm)
        prompt = agent.get_system_prompt()
        assert "QUALITY" in prompt or "QA" in prompt
        assert "validation" in prompt.lower() or "quality" in prompt.lower()


# =============================================================================
# AGENT EXECUTION TESTS
# =============================================================================


class TestAgentExecution:
    """Tests for agent execution with mocked LLM."""

    @pytest.mark.asyncio
    async def test_execute_success(self, mock_config: Config, mock_llm):
        """Test successful agent execution."""
        mock_llm.set_response("This is the selected pitch response.")

        agent = ShowrunnerAgent(mock_config, mock_llm)
        context = AgentContext(
            show_bible="# Show Bible\nContent here",
            creative_prompt="# Creative Prompt\nContent here",
            task_type="select_pitch",
        )

        output = await agent.execute(context)

        assert output.success is True
        assert output.agent_role == AgentRole.SHOWRUNNER
        assert output.task_type == "select_pitch"
        assert output.content == "This is the selected pitch response."
        assert output.token_usage is not None
        assert output.error_message is None

    @pytest.mark.asyncio
    async def test_execute_with_previous_output(self, mock_config: Config, mock_llm):
        """Test agent execution with previous output context."""
        mock_llm.set_response("Reviewed draft response.")

        agent = ShowrunnerAgent(mock_config, mock_llm)
        context = AgentContext(
            show_bible="# Show Bible",
            creative_prompt="# Prompt",
            task_type="review_draft",
            previous_output="First draft content...",
        )

        output = await agent.execute(context)

        assert output.success is True
        # Check that the call included previous output
        assert len(mock_llm.call_history) == 1
        messages = mock_llm.call_history[0]["messages"]
        # Messages are LangChain objects with .content attribute
        user_message = messages[1].content
        assert "Previous Stage Output" in user_message

    @pytest.mark.asyncio
    async def test_execute_with_direction_notes(self, mock_config: Config, mock_llm):
        """Test agent execution with direction notes."""
        mock_llm.set_response("Response with direction notes.")

        agent = HeadWriterAgent(mock_config, mock_llm)
        context = AgentContext(
            show_bible="# Bible",
            creative_prompt="# Prompt",
            task_type="compile_pitches",
            direction_notes="Focus on absurdist humor.",
        )

        output = await agent.execute(context)

        assert output.success is True
        messages = mock_llm.call_history[0]["messages"]
        # Messages are LangChain objects with .content attribute
        user_message = messages[1].content
        assert "Direction Notes" in user_message
        assert "absurdist" in user_message

    @pytest.mark.asyncio
    async def test_execute_tracks_token_usage(self, mock_config: Config, mock_llm):
        """Test that execution tracks token usage."""
        mock_llm.set_response("A response for token tracking.")

        agent = StaffWriterA(mock_config, mock_llm)
        context = AgentContext(
            show_bible="# Bible",
            creative_prompt="# Prompt",
            task_type="generate_pitch",
        )

        output = await agent.execute(context)

        assert output.success is True
        assert output.token_usage is not None
        assert "prompt_tokens" in output.token_usage
        assert "completion_tokens" in output.token_usage
        assert "total_tokens" in output.token_usage
        assert output.token_usage["total_tokens"] > 0

    @pytest.mark.asyncio
    async def test_execute_failure_returns_error(self, mock_config: Config, mock_llm):
        """Test that execution failures return error output."""
        # Make LLM raise an exception
        async def raise_error(*args, **kwargs):
            raise Exception("API Error: Rate limited")

        mock_llm.acall = raise_error

        agent = ResearchAgent(mock_config, mock_llm)
        context = AgentContext(
            show_bible="# Bible",
            creative_prompt="# Prompt",
            task_type="gather_references",
        )

        output = await agent.execute(context)

        assert output.success is False
        assert "Rate limited" in output.error_message
        assert output.content == ""

    @pytest.mark.asyncio
    async def test_multiple_agent_executions(self, mock_config: Config, mock_llm):
        """Test executing multiple agents in sequence."""
        mock_llm.set_responses([
            "Pitch from Staff Writer A",
            "Structure from Staff Writer B",
        ])

        agent_a = StaffWriterA(mock_config, mock_llm)
        agent_b = StaffWriterB(mock_config, mock_llm)

        context = AgentContext(
            show_bible="# Bible",
            creative_prompt="# Prompt",
            task_type="generate_pitch",
        )

        output_a = await agent_a.execute(context)
        output_b = await agent_b.execute(context)

        assert output_a.success is True
        assert output_b.success is True
        assert output_a.content == "Pitch from Staff Writer A"
        assert output_b.content == "Structure from Staff Writer B"


# =============================================================================
# BUILD PROMPT TESTS
# =============================================================================


class TestBuildPrompt:
    """Tests for the build_prompt method."""

    def test_build_prompt_includes_show_bible(self, mock_config: Config, mock_llm):
        """Test that built prompt includes show bible."""
        agent = ShowrunnerAgent(mock_config, mock_llm)
        context = AgentContext(
            show_bible="# MY SHOW BIBLE CONTENT",
            creative_prompt="# Prompt",
            task_type="select_pitch",
        )

        system_prompt, user_prompt = agent.build_prompt(context)

        assert "MY SHOW BIBLE CONTENT" in user_prompt
        assert "Show Bible" in user_prompt

    def test_build_prompt_includes_creative_prompt(self, mock_config: Config, mock_llm):
        """Test that built prompt includes creative prompt."""
        agent = ShowrunnerAgent(mock_config, mock_llm)
        context = AgentContext(
            show_bible="# Bible",
            creative_prompt="# MY CREATIVE PROMPT CONTENT",
            task_type="select_pitch",
        )

        system_prompt, user_prompt = agent.build_prompt(context)

        assert "MY CREATIVE PROMPT CONTENT" in user_prompt
        assert "Creative Prompt" in user_prompt

    def test_build_prompt_includes_task_type(self, mock_config: Config, mock_llm):
        """Test that built prompt includes task type."""
        agent = ShowrunnerAgent(mock_config, mock_llm)
        context = AgentContext(
            show_bible="# Bible",
            creative_prompt="# Prompt",
            task_type="final_approval",
        )

        system_prompt, user_prompt = agent.build_prompt(context)

        assert "CURRENT TASK: final_approval" in user_prompt

    def test_build_prompt_excludes_none_fields(self, mock_config: Config, mock_llm):
        """Test that None optional fields are excluded from prompt."""
        agent = ShowrunnerAgent(mock_config, mock_llm)
        context = AgentContext(
            show_bible="# Bible",
            creative_prompt="# Prompt",
            task_type="select_pitch",
            previous_output=None,
            direction_notes=None,
        )

        system_prompt, user_prompt = agent.build_prompt(context)

        # These sections should not appear when None
        assert "Previous Stage Output" not in user_prompt
        assert "Direction Notes" not in user_prompt


# =============================================================================
# AGENT NAME TESTS
# =============================================================================


class TestAgentNames:
    """Tests for agent name property."""

    def test_showrunner_name(self, mock_config: Config, mock_llm):
        """Test Showrunner name formatting."""
        agent = ShowrunnerAgent(mock_config, mock_llm)
        assert agent.name == "Showrunner"

    def test_head_writer_name(self, mock_config: Config, mock_llm):
        """Test Head Writer name formatting."""
        agent = HeadWriterAgent(mock_config, mock_llm)
        assert agent.name == "Head Writer"

    def test_senior_writer_a_name(self, mock_config: Config, mock_llm):
        """Test Senior Writer A name formatting."""
        agent = SeniorWriterA(mock_config, mock_llm)
        assert agent.name == "Senior Writer A"

    def test_staff_writer_b_name(self, mock_config: Config, mock_llm):
        """Test Staff Writer B name formatting."""
        agent = StaffWriterB(mock_config, mock_llm)
        assert agent.name == "Staff Writer B"

    def test_qa_name(self, mock_config: Config, mock_llm):
        """Test QA agent name formatting."""
        agent = QAAgent(mock_config, mock_llm)
        assert agent.name == "Qa"  # Title case of "qa"
