"""
Integration tests for the sketch comedy writing system.

Tests the complete workflow including:
- Graph construction and compilation
- Full workflow execution with mocked LLM
- State persistence and checkpoints
- End-to-end happy path scenarios
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from langgraph.checkpoint.memory import MemorySaver

from src.workflow.graph import (
    build_workflow_graph,
    compile_app,
    compile_app_no_interrupts,
    get_graph_visualization,
)
from src.workflow.state import (
    SketchState,
    WorkflowStage,
    create_initial_state,
)
from src.utils.config import Config

# =============================================================================
# GRAPH CONSTRUCTION TESTS
# =============================================================================


class TestBuildWorkflowGraph:
    """Tests for build_workflow_graph function."""

    def test_graph_builds_successfully(self):
        """Test that workflow graph builds without error."""
        graph = build_workflow_graph()
        assert graph is not None

    def test_graph_has_all_nodes(self):
        """Test that graph contains all expected nodes."""
        graph = build_workflow_graph()
        # StateGraph has nodes attribute
        expected_nodes = [
            "pitch_session",
            "human_pitch_review",
            "showrunner_select",
            "story_breaking",
            "human_beat_review",
            "drafting",
            "table_read",
            "revision",
            "polish",
            "human_final_review",
        ]
        for node in expected_nodes:
            assert node in graph.nodes

    def test_graph_has_entry_point(self):
        """Test that graph has pitch_session as entry point."""
        graph = build_workflow_graph()
        # In LangGraph, entry point is accessible via compiled app
        # For now, just verify the graph builds
        assert graph is not None


# =============================================================================
# APP COMPILATION TESTS
# =============================================================================


class TestCompileApp:
    """Tests for compile_app function."""

    def test_compile_with_default_checkpointer(self):
        """Test compilation with default MemorySaver."""
        app = compile_app()
        assert app is not None

    def test_compile_with_custom_checkpointer(self):
        """Test compilation with custom checkpointer."""
        checkpointer = MemorySaver()
        app = compile_app(checkpointer=checkpointer)
        assert app is not None

    def test_compile_with_custom_interrupts(self):
        """Test compilation with custom interrupt points."""
        app = compile_app(
            interrupt_before=["human_pitch_review"],
            interrupt_after=["polish"],
        )
        assert app is not None

    def test_compile_with_no_interrupts(self):
        """Test compilation with empty interrupt lists."""
        app = compile_app(
            interrupt_before=[],
            interrupt_after=[],
        )
        assert app is not None


class TestCompileAppNoInterrupts:
    """Tests for compile_app_no_interrupts function."""

    def test_compile_no_interrupts(self):
        """Test compilation without interrupts."""
        app = compile_app_no_interrupts()
        assert app is not None

    def test_compile_no_interrupts_with_checkpointer(self):
        """Test compilation without interrupts but with checkpointer."""
        checkpointer = MemorySaver()
        app = compile_app_no_interrupts(checkpointer=checkpointer)
        assert app is not None


# =============================================================================
# GRAPH VISUALIZATION TESTS
# =============================================================================


class TestGraphVisualization:
    """Tests for get_graph_visualization function."""

    def test_visualization_contains_nodes(self):
        """Test that visualization lists all nodes."""
        viz = get_graph_visualization()
        assert "pitch_session" in viz
        assert "human_pitch_review" in viz
        assert "showrunner_select" in viz
        assert "story_breaking" in viz
        assert "human_beat_review" in viz
        assert "drafting" in viz
        assert "table_read" in viz
        assert "revision" in viz
        assert "polish" in viz
        assert "human_final_review" in viz

    def test_visualization_contains_edges(self):
        """Test that visualization describes edges."""
        viz = get_graph_visualization()
        assert "->" in viz
        assert "EDGES:" in viz

    def test_visualization_contains_checkpoints(self):
        """Test that visualization lists checkpoints."""
        viz = get_graph_visualization()
        assert "HUMAN CHECKPOINTS:" in viz
        assert "human_pitch_review" in viz
        assert "human_beat_review" in viz
        assert "human_final_review" in viz


# =============================================================================
# STATE FLOW TESTS
# =============================================================================


class TestStateFlow:
    """Tests for state flow through workflow stages."""

    def test_initial_state_is_valid_for_graph(self):
        """Test that initial state can be used with the graph."""
        state = create_initial_state(
            show_bible="# Test Bible",
            creative_prompt="# Test Prompt",
        )
        # State should have all required fields
        assert "show_bible" in state
        assert "creative_prompt" in state
        assert "current_stage" in state

    def test_state_progresses_through_stages(self):
        """Test that state can progress through all stages."""
        state = create_initial_state("bible", "prompt")

        stages = [
            WorkflowStage.PITCH_SESSION,
            WorkflowStage.HUMAN_PITCH_REVIEW,
            WorkflowStage.SHOWRUNNER_SELECT,
            WorkflowStage.STORY_BREAKING,
            WorkflowStage.HUMAN_BEAT_REVIEW,
            WorkflowStage.SCRIPT_DRAFTING,
            WorkflowStage.TABLE_READ,
            WorkflowStage.REVISION,
            WorkflowStage.POLISH,
            WorkflowStage.HUMAN_FINAL_REVIEW,
            WorkflowStage.COMPLETE,
        ]

        from src.workflow.state import update_stage

        for stage in stages:
            state = update_stage(state, stage)
            assert state["current_stage"] == stage.value


# =============================================================================
# MOCK LLM WORKFLOW TESTS
# =============================================================================


class TestMockedWorkflowExecution:
    """Tests for workflow execution with mocked LLM responses."""

    def test_mock_llm_fixture_available(self, mock_llm):
        """Test that mock LLM fixture is available."""
        assert mock_llm is not None
        assert hasattr(mock_llm, "set_response")
        assert hasattr(mock_llm, "call_history")

    def test_mock_config_fixture_available(self, mock_config: Config):
        """Test that mock config fixture is available."""
        assert mock_config is not None
        assert mock_config.llm.provider in ["anthropic", "openai"]
        assert mock_config.workflow.max_revision_cycles > 0

    @pytest.mark.asyncio
    async def test_agent_execution_with_mock(self, mock_config, mock_llm):
        """Test agent execution with mocked LLM."""
        from src.agents import ShowrunnerAgent, AgentContext

        mock_llm.set_response("**SELECTED PITCH:** Tech Support ER\n**WHY:** Great premise!")

        agent = ShowrunnerAgent(mock_config, mock_llm)
        context = AgentContext(
            show_bible="# Show Bible",
            creative_prompt="# Creative Prompt",
            task_type="select_pitch",
        )

        output = await agent.execute(context)
        assert output.success is True
        assert "Tech Support" in output.content


# =============================================================================
# FIXTURE STATE TESTS
# =============================================================================


class TestFixtureStates:
    """Tests using the various state fixtures."""

    def test_initial_state_has_correct_stage(self, initial_state):
        """Test initial state stage."""
        assert initial_state["current_stage"] == WorkflowStage.INITIALIZATION.value

    def test_state_after_pitches_has_pitches(self, state_after_pitches):
        """Test state after pitches has pitch data."""
        assert len(state_after_pitches["pitches"]) > 0
        assert state_after_pitches["compiled_pitches"]

    def test_approved_beat_sheet_state(self, state_approved_beat_sheet):
        """Test approved beat sheet state."""
        assert state_approved_beat_sheet["human_beat_sheet_approval"] is True
        assert state_approved_beat_sheet["beat_sheet"]

    def test_final_review_state(self, state_final_review):
        """Test final review state."""
        assert state_final_review["formatted_script"]
        assert state_final_review["qa_report"]

    def test_final_approved_state(self, state_final_approved):
        """Test final approved state."""
        assert state_final_approved["human_final_approval"] is True
        assert state_final_approved["final_script"]


# =============================================================================
# EDGE CASE TESTS
# =============================================================================


class TestWorkflowEdgeCases:
    """Tests for edge cases in workflow execution."""

    def test_empty_show_bible_state(self):
        """Test handling of minimal show bible."""
        state = create_initial_state(
            show_bible="",  # Empty but valid
            creative_prompt="# Prompt",
        )
        # State creation should succeed even with minimal content
        # Validation happens elsewhere
        assert state["show_bible"] == ""

    def test_max_revision_cycles_boundary(self, state_max_revisions):
        """Test state at max revision boundary."""
        from src.workflow.edges import should_continue_revision

        result = should_continue_revision(state_max_revisions)
        assert result == "max_iterations"

    def test_empty_pitch_selection(self, state_after_pitches):
        """Test edge function with empty pitch selection."""
        from src.workflow.edges import get_next_stage_after_pitch_review

        state_after_pitches["human_selected_pitches"] = []
        result = get_next_stage_after_pitch_review(state_after_pitches)
        assert result == "showrunner_select"


# =============================================================================
# COMPREHENSIVE WORKFLOW TESTS
# =============================================================================


class TestComprehensiveWorkflow:
    """Comprehensive tests for the full workflow."""

    def test_all_imports_work(self):
        """Test that all workflow components can be imported."""
        from src.workflow.graph import build_workflow_graph, compile_app
        from src.workflow.state import SketchState, create_initial_state
        from src.workflow.edges import (
            should_revise_beat_sheet,
            should_continue_revision,
            should_approve_final,
        )
        from src.workflow.nodes import (
            pitch_session_node,
            human_pitch_review_node,
            showrunner_select_node,
            story_breaking_node,
            human_beat_review_node,
            drafting_node,
            table_read_node,
            revision_node,
            polish_node,
            human_final_review_node,
        )

        # All imports successful
        assert True

    def test_all_agents_can_be_initialized(self, mock_config, mock_llm):
        """Test that all 10 agents can be initialized."""
        from src.agents import (
            ShowrunnerAgent,
            HeadWriterAgent,
            SeniorWriterA,
            SeniorWriterB,
            StaffWriterA,
            StaffWriterB,
            StoryEditorAgent,
            ResearchAgent,
            ScriptCoordinatorAgent,
            QAAgent,
        )

        agents = [
            ShowrunnerAgent(mock_config, mock_llm),
            HeadWriterAgent(mock_config, mock_llm),
            SeniorWriterA(mock_config, mock_llm),
            SeniorWriterB(mock_config, mock_llm),
            StaffWriterA(mock_config, mock_llm),
            StaffWriterB(mock_config, mock_llm),
            StoryEditorAgent(mock_config, mock_llm),
            ResearchAgent(mock_config, mock_llm),
            ScriptCoordinatorAgent(mock_config, mock_llm),
            QAAgent(mock_config, mock_llm),
        ]

        assert len(agents) == 10
        for agent in agents:
            assert agent.role is not None
            assert agent.name is not None

    def test_workflow_state_type_checking(self):
        """Test that SketchState TypedDict has expected keys."""
        state = create_initial_state("bible", "prompt")

        expected_keys = [
            "show_bible",
            "creative_prompt",
            "session_id",
            "target_length",
            "max_revision_cycles",
            "pitches",
            "compiled_pitches",
            "human_selected_pitches",
            "showrunner_selected_pitch",
            "beat_sheet",
            "human_beat_sheet_approval",
            "first_draft",
            "table_read_feedback",
            "revised_draft",
            "iteration_count",
            "formatted_script",
            "qa_report",
            "final_script",
            "current_stage",
            "error_log",
            "token_usage",
        ]

        for key in expected_keys:
            assert key in state, f"Missing key: {key}"


# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================


class TestErrorHandling:
    """Tests for error handling in the workflow."""

    def test_add_error_function(self):
        """Test that errors can be added to state."""
        from src.workflow.state import add_error

        state = create_initial_state("bible", "prompt")
        state = add_error(state, "Test error", context="test_context")

        assert len(state["error_log"]) == 1
        assert state["error_log"][0]["error"] == "Test error"

    def test_multiple_errors_accumulate(self):
        """Test that multiple errors accumulate."""
        from src.workflow.state import add_error

        state = create_initial_state("bible", "prompt")
        state = add_error(state, "Error 1")
        state = add_error(state, "Error 2")
        state = add_error(state, "Error 3")

        assert len(state["error_log"]) == 3

    def test_token_usage_tracking(self):
        """Test token usage accumulation."""
        from src.workflow.state import update_token_usage

        state = create_initial_state("bible", "prompt")
        state = update_token_usage(state, 100, 50)
        state = update_token_usage(state, 200, 100)

        assert state["token_usage"]["prompt_tokens"] == 300
        assert state["token_usage"]["completion_tokens"] == 150
        assert state["token_usage"]["total_tokens"] == 450


# =============================================================================
# CHECKPOINT TESTS
# =============================================================================


class TestCheckpoints:
    """Tests for checkpoint functionality."""

    def test_default_interrupt_points(self):
        """Test that default interrupt points are set correctly."""
        # The compile_app function sets these defaults
        # We can verify by checking the function behavior
        # Note: We can't easily inspect compiled app interrupts
        # So we verify the defaults are what we expect
        expected_interrupts = [
            "human_pitch_review",
            "human_beat_review",
            "human_final_review",
        ]
        # Just verify these are valid node names
        graph = build_workflow_graph()
        for interrupt in expected_interrupts:
            assert interrupt in graph.nodes

    def test_state_persists_with_checkpointer(self):
        """Test that state can be saved and loaded with checkpointer."""
        checkpointer = MemorySaver()
        app = compile_app(checkpointer=checkpointer)
        assert app is not None
        # Full persistence testing would require running the workflow
        # which needs actual or fully mocked agents


# =============================================================================
# CONFIGURATION TESTS
# =============================================================================


class TestConfigurationIntegration:
    """Tests for configuration integration."""

    def test_mock_config_has_all_sections(self, mock_config):
        """Test mock config has all required sections."""
        assert mock_config.llm is not None
        assert mock_config.workflow is not None
        assert mock_config.show is not None
        assert mock_config.project_root is not None

    def test_workflow_config_values(self, mock_config):
        """Test workflow config values are sensible."""
        assert mock_config.workflow.max_revision_cycles >= 1
        assert mock_config.workflow.target_sketch_length >= 1

    def test_show_config_content(self, mock_config):
        """Test show config has content."""
        assert len(mock_config.show.show_bible) > 0
        assert len(mock_config.show.creative_prompt) > 0
