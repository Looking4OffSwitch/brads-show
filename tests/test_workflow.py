"""
Unit tests for workflow state and node implementations.

Tests the src/workflow module including:
- WorkflowStage enum
- Pitch, TableReadFeedback, and QAReport dataclasses
- SketchState TypedDict and helper functions
- Individual workflow node functions
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from src.workflow.state import (
    Pitch,
    QAReport,
    SketchState,
    TableReadFeedback,
    WorkflowStage,
    add_error,
    create_initial_state,
    update_stage,
    update_token_usage,
)

# =============================================================================
# WORKFLOW STAGE TESTS
# =============================================================================


class TestWorkflowStage:
    """Tests for WorkflowStage enum."""

    def test_all_stages_defined(self):
        """Test that all expected workflow stages are defined."""
        expected_stages = [
            "initialization",
            "pitch_session",
            "human_pitch_review",
            "showrunner_select",
            "story_breaking",
            "human_beat_review",
            "script_drafting",
            "table_read",
            "revision",
            "polish",
            "human_final_review",
            "complete",
        ]
        actual_stages = [stage.value for stage in WorkflowStage]
        assert len(actual_stages) == 12
        for stage in expected_stages:
            assert stage in actual_stages

    def test_initialization_stage(self):
        """Test initialization stage value."""
        assert WorkflowStage.INITIALIZATION.value == "initialization"

    def test_human_checkpoint_stages(self):
        """Test human checkpoint stages."""
        assert WorkflowStage.HUMAN_PITCH_REVIEW.value == "human_pitch_review"
        assert WorkflowStage.HUMAN_BEAT_REVIEW.value == "human_beat_review"
        assert WorkflowStage.HUMAN_FINAL_REVIEW.value == "human_final_review"

    def test_complete_stage(self):
        """Test complete stage value."""
        assert WorkflowStage.COMPLETE.value == "complete"


# =============================================================================
# PITCH DATACLASS TESTS
# =============================================================================


class TestPitch:
    """Tests for Pitch dataclass."""

    def test_minimal_pitch(self):
        """Test creating pitch with minimal fields."""
        pitch = Pitch(
            id="pitch_001",
            title="Tech Support ER",
            logline="Tech support agent treats problems like surgery",
            game="Medical drama escalation",
            agent="Staff Writer A",
        )
        assert pitch.id == "pitch_001"
        assert pitch.title == "Tech Support ER"
        assert pitch.character_types == []
        assert pitch.escalation_path == ""
        assert pitch.score is None

    def test_full_pitch(self):
        """Test creating pitch with all fields."""
        pitch = Pitch(
            id="pitch_002",
            title="DMV Odyssey",
            logline="Every DMV visit becomes an epic quest",
            game="Epic adventure framing for mundane tasks",
            agent="Senior Writer A",
            character_types=["Hero customer", "Bored clerks"],
            escalation_path="Forms → Multiple departments → Boss battle",
            research_notes="DMV wait times average 37 minutes",
            score=8.5,
        )
        assert pitch.character_types == ["Hero customer", "Bored clerks"]
        assert pitch.score == 8.5

    def test_pitch_to_dict(self):
        """Test Pitch serialization to dictionary."""
        pitch = Pitch(
            id="pitch_003",
            title="Test Pitch",
            logline="A test logline",
            game="Test game",
            agent="Test Agent",
        )
        data = pitch.to_dict()
        assert data["id"] == "pitch_003"
        assert data["title"] == "Test Pitch"
        assert "logline" in data
        assert "game" in data

    def test_pitch_from_dict(self):
        """Test Pitch deserialization from dictionary."""
        data = {
            "id": "pitch_004",
            "title": "From Dict",
            "logline": "Created from dict",
            "game": "Dict game",
            "agent": "Dict Agent",
            "score": 7.0,
        }
        pitch = Pitch.from_dict(data)
        assert pitch.id == "pitch_004"
        assert pitch.score == 7.0

    def test_pitch_from_dict_missing_optional(self):
        """Test Pitch from dict with missing optional fields."""
        data = {
            "id": "pitch_005",
            "title": "Minimal",
            "logline": "Minimal logline",
            "game": "Minimal game",
            "agent": "Minimal Agent",
        }
        pitch = Pitch.from_dict(data)
        assert pitch.character_types == []
        assert pitch.score is None


# =============================================================================
# TABLE READ FEEDBACK TESTS
# =============================================================================


class TestTableReadFeedback:
    """Tests for TableReadFeedback dataclass."""

    def test_minimal_feedback(self):
        """Test creating feedback with minimal fields."""
        feedback = TableReadFeedback(
            agent="Senior Writer A",
            focus_area="Character",
        )
        assert feedback.agent == "Senior Writer A"
        assert feedback.focus_area == "Character"
        assert feedback.issues == []
        assert feedback.strengths == []

    def test_full_feedback(self):
        """Test creating feedback with all fields."""
        feedback = TableReadFeedback(
            agent="Senior Writer B",
            focus_area="Jokes",
            issues=[{"type": "weak_punchline", "location": "page 3"}],
            strengths=["Great opening", "Strong callback"],
            suggestions=["Punch up the ending"],
            raw_content="Full feedback content...",
        )
        assert len(feedback.issues) == 1
        assert len(feedback.strengths) == 2

    def test_feedback_to_dict(self):
        """Test TableReadFeedback serialization."""
        feedback = TableReadFeedback(
            agent="Story Editor",
            focus_area="Continuity",
            issues=[{"type": "timeline_error"}],
        )
        data = feedback.to_dict()
        assert data["agent"] == "Story Editor"
        assert data["focus_area"] == "Continuity"
        assert len(data["issues"]) == 1


# =============================================================================
# QA REPORT TESTS
# =============================================================================


class TestQAReport:
    """Tests for QAReport dataclass."""

    def test_approved_report(self):
        """Test creating approved QA report."""
        report = QAReport(
            approved=True,
            confidence_score=9,
            strengths=["Strong structure", "Great jokes"],
        )
        assert report.approved is True
        assert report.confidence_score == 9
        assert report.critical_issues == []

    def test_rejected_report(self):
        """Test creating rejected QA report."""
        report = QAReport(
            approved=False,
            confidence_score=4,
            critical_issues=["Game unclear", "Weak ending"],
            minor_issues=["Typo on page 2"],
        )
        assert report.approved is False
        assert len(report.critical_issues) == 2

    def test_report_with_checklist(self):
        """Test QA report with checklist results."""
        report = QAReport(
            approved=True,
            confidence_score=8,
            checklist_results={
                "formatting": {"character_names": True, "scene_headers": True},
                "content": {"game_clear": True, "escalation": True},
            },
        )
        assert report.checklist_results["formatting"]["character_names"] is True

    def test_report_to_dict(self):
        """Test QAReport serialization."""
        report = QAReport(approved=True, confidence_score=7)
        data = report.to_dict()
        assert data["approved"] is True
        assert data["confidence_score"] == 7


# =============================================================================
# CREATE INITIAL STATE TESTS
# =============================================================================


class TestCreateInitialState:
    """Tests for create_initial_state function."""

    def test_minimal_initial_state(self):
        """Test creating state with minimal parameters."""
        state = create_initial_state(
            show_bible="# Show Bible",
            creative_prompt="# Creative Prompt",
        )
        assert state["show_bible"] == "# Show Bible"
        assert state["creative_prompt"] == "# Creative Prompt"
        assert state["target_length"] == 5
        assert state["max_revision_cycles"] == 3

    def test_initial_state_with_session_id(self):
        """Test creating state with custom session ID."""
        state = create_initial_state(
            show_bible="bible",
            creative_prompt="prompt",
            session_id="custom_session_123",
        )
        assert state["session_id"] == "custom_session_123"

    def test_initial_state_generates_session_id(self):
        """Test that session ID is generated if not provided."""
        state = create_initial_state(
            show_bible="bible",
            creative_prompt="prompt",
        )
        assert state["session_id"].startswith("sketch_")
        assert len(state["session_id"]) > 10

    def test_initial_state_custom_parameters(self):
        """Test creating state with custom workflow parameters."""
        state = create_initial_state(
            show_bible="bible",
            creative_prompt="prompt",
            target_length=7,
            max_revision_cycles=5,
        )
        assert state["target_length"] == 7
        assert state["max_revision_cycles"] == 5

    def test_initial_state_empty_collections(self):
        """Test that initial state has empty collections."""
        state = create_initial_state(
            show_bible="bible",
            creative_prompt="prompt",
        )
        assert state["pitches"] == []
        assert state["human_selected_pitches"] == []
        assert state["drafted_sections"] == []
        assert state["table_read_feedback"] == []
        assert state["error_log"] == []

    def test_initial_state_empty_strings(self):
        """Test that initial state has empty string fields."""
        state = create_initial_state(
            show_bible="bible",
            creative_prompt="prompt",
        )
        assert state["compiled_pitches"] == ""
        assert state["beat_sheet"] == ""
        assert state["first_draft"] == ""
        assert state["final_script"] == ""

    def test_initial_state_current_stage(self):
        """Test that initial state starts at initialization stage."""
        state = create_initial_state(
            show_bible="bible",
            creative_prompt="prompt",
        )
        assert state["current_stage"] == WorkflowStage.INITIALIZATION.value

    def test_initial_state_stage_history(self):
        """Test that initial state has stage history."""
        state = create_initial_state(
            show_bible="bible",
            creative_prompt="prompt",
        )
        assert len(state["stage_history"]) == 1
        assert state["stage_history"][0]["stage"] == "initialization"
        assert state["stage_history"][0]["status"] == "started"

    def test_initial_state_token_usage(self):
        """Test that initial state has zero token usage."""
        state = create_initial_state(
            show_bible="bible",
            creative_prompt="prompt",
        )
        assert state["token_usage"]["prompt_tokens"] == 0
        assert state["token_usage"]["completion_tokens"] == 0
        assert state["token_usage"]["total_tokens"] == 0

    def test_initial_state_boolean_defaults(self):
        """Test that initial state boolean fields default to False."""
        state = create_initial_state(
            show_bible="bible",
            creative_prompt="prompt",
        )
        assert state["human_beat_sheet_approval"] is False
        assert state["showrunner_revision_approved"] is False
        assert state["human_final_approval"] is False


# =============================================================================
# UPDATE STAGE TESTS
# =============================================================================


class TestUpdateStage:
    """Tests for update_stage function."""

    def test_update_stage_changes_current(self):
        """Test that update_stage changes current stage."""
        state = create_initial_state("bible", "prompt")
        new_state = update_stage(state, WorkflowStage.PITCH_SESSION)
        assert new_state["current_stage"] == "pitch_session"

    def test_update_stage_adds_history(self):
        """Test that update_stage adds to history."""
        state = create_initial_state("bible", "prompt")
        original_history_len = len(state["stage_history"])
        new_state = update_stage(state, WorkflowStage.PITCH_SESSION)
        assert len(new_state["stage_history"]) == original_history_len + 1

    def test_update_stage_history_format(self):
        """Test history entry format."""
        state = create_initial_state("bible", "prompt")
        new_state = update_stage(state, WorkflowStage.STORY_BREAKING)
        latest = new_state["stage_history"][-1]
        assert latest["stage"] == "story_breaking"
        assert latest["status"] == "started"
        assert "timestamp" in latest

    def test_update_stage_preserves_other_fields(self):
        """Test that update_stage preserves other state fields."""
        state = create_initial_state("bible", "prompt", session_id="test123")
        state["pitches"] = [{"id": "pitch_001"}]
        new_state = update_stage(state, WorkflowStage.HUMAN_PITCH_REVIEW)
        assert new_state["session_id"] == "test123"
        assert new_state["pitches"] == [{"id": "pitch_001"}]

    def test_multiple_stage_updates(self):
        """Test multiple consecutive stage updates."""
        state = create_initial_state("bible", "prompt")
        state = update_stage(state, WorkflowStage.PITCH_SESSION)
        state = update_stage(state, WorkflowStage.HUMAN_PITCH_REVIEW)
        state = update_stage(state, WorkflowStage.SHOWRUNNER_SELECT)
        assert state["current_stage"] == "showrunner_select"
        assert len(state["stage_history"]) == 4  # init + 3 updates


# =============================================================================
# ADD ERROR TESTS
# =============================================================================


class TestAddError:
    """Tests for add_error function."""

    def test_add_error_creates_entry(self):
        """Test that add_error adds to error log."""
        state = create_initial_state("bible", "prompt")
        new_state = add_error(state, "Test error message")
        assert len(new_state["error_log"]) == 1

    def test_add_error_with_context(self):
        """Test add_error with context."""
        state = create_initial_state("bible", "prompt")
        new_state = add_error(state, "API failed", context="pitch_session:staff_a")
        error = new_state["error_log"][0]
        assert error["error"] == "API failed"
        assert error["context"] == "pitch_session:staff_a"

    def test_add_error_includes_stage(self):
        """Test that error log includes current stage."""
        state = create_initial_state("bible", "prompt")
        state = update_stage(state, WorkflowStage.TABLE_READ)
        new_state = add_error(state, "Review failed")
        error = new_state["error_log"][0]
        assert error["stage"] == "table_read"

    def test_add_error_includes_timestamp(self):
        """Test that error log includes timestamp."""
        state = create_initial_state("bible", "prompt")
        new_state = add_error(state, "Some error")
        assert "timestamp" in new_state["error_log"][0]

    def test_multiple_errors(self):
        """Test adding multiple errors."""
        state = create_initial_state("bible", "prompt")
        state = add_error(state, "Error 1")
        state = add_error(state, "Error 2")
        state = add_error(state, "Error 3")
        assert len(state["error_log"]) == 3

    def test_add_error_preserves_existing_errors(self):
        """Test that new errors don't overwrite existing ones."""
        state = create_initial_state("bible", "prompt")
        state = add_error(state, "First error")
        state = add_error(state, "Second error")
        assert state["error_log"][0]["error"] == "First error"
        assert state["error_log"][1]["error"] == "Second error"


# =============================================================================
# UPDATE TOKEN USAGE TESTS
# =============================================================================


class TestUpdateTokenUsage:
    """Tests for update_token_usage function."""

    def test_add_tokens_to_empty(self):
        """Test adding tokens to initial state."""
        state = create_initial_state("bible", "prompt")
        new_state = update_token_usage(state, prompt_tokens=100, completion_tokens=50)
        assert new_state["token_usage"]["prompt_tokens"] == 100
        assert new_state["token_usage"]["completion_tokens"] == 50
        assert new_state["token_usage"]["total_tokens"] == 150

    def test_accumulate_tokens(self):
        """Test that tokens accumulate."""
        state = create_initial_state("bible", "prompt")
        state = update_token_usage(state, 100, 50)
        state = update_token_usage(state, 200, 100)
        assert state["token_usage"]["prompt_tokens"] == 300
        assert state["token_usage"]["completion_tokens"] == 150
        assert state["token_usage"]["total_tokens"] == 450

    def test_zero_tokens(self):
        """Test adding zero tokens."""
        state = create_initial_state("bible", "prompt")
        state = update_token_usage(state, 100, 50)
        state = update_token_usage(state, 0, 0)
        assert state["token_usage"]["total_tokens"] == 150


# =============================================================================
# STATE FIXTURE TESTS
# =============================================================================


class TestStateFixtures:
    """Tests using state fixtures from conftest.py."""

    def test_initial_state_fixture(self, initial_state: SketchState):
        """Test initial state fixture."""
        assert initial_state["show_bible"]
        assert initial_state["creative_prompt"]
        assert initial_state["session_id"] == "test_session_001"

    def test_state_after_pitches(self, state_after_pitches: SketchState):
        """Test state after pitch session."""
        assert len(state_after_pitches["pitches"]) == 3
        assert state_after_pitches["compiled_pitches"]
        assert state_after_pitches["current_stage"] == "human_pitch_review"

    def test_state_after_pitch_selection(self, state_after_pitch_selection: SketchState):
        """Test state after human pitch selection."""
        assert len(state_after_pitch_selection["human_selected_pitches"]) > 0
        assert state_after_pitch_selection["showrunner_selected_pitch"]
        assert state_after_pitch_selection["current_stage"] == "story_breaking"

    def test_state_after_beat_sheet(self, state_after_beat_sheet: SketchState):
        """Test state after beat sheet creation."""
        assert state_after_beat_sheet["beat_sheet"]
        assert state_after_beat_sheet["character_details"]
        assert state_after_beat_sheet["current_stage"] == "human_beat_review"

    def test_state_approved_beat_sheet(self, state_approved_beat_sheet: SketchState):
        """Test state with approved beat sheet."""
        assert state_approved_beat_sheet["human_beat_sheet_approval"] is True
        assert state_approved_beat_sheet["current_stage"] == "drafting"

    def test_state_needs_revision(self, state_needs_revision: SketchState):
        """Test state that needs revision."""
        assert state_needs_revision["human_beat_sheet_approval"] is False
        assert state_needs_revision["human_beat_sheet_notes"]

    def test_state_in_revision(self, state_in_revision: SketchState):
        """Test state during revision cycle."""
        assert state_in_revision["first_draft"]
        assert state_in_revision["iteration_count"] >= 1
        assert state_in_revision["current_stage"] == "revision"

    def test_state_max_revisions(self, state_max_revisions: SketchState):
        """Test state at max revision iterations."""
        assert state_max_revisions["iteration_count"] == state_max_revisions["max_revision_cycles"]

    def test_state_final_review(self, state_final_review: SketchState):
        """Test state ready for final review."""
        assert state_final_review["formatted_script"]
        assert state_final_review["qa_report"]
        assert state_final_review["current_stage"] == "human_final_review"

    def test_state_final_approved(self, state_final_approved: SketchState):
        """Test state with final approval."""
        assert state_final_approved["human_final_approval"] is True
        assert state_final_approved["final_script"]


# =============================================================================
# WORKFLOW STAGE TRANSITIONS
# =============================================================================


class TestWorkflowStageTransitions:
    """Tests for valid workflow stage transitions."""

    def test_full_happy_path(self, initial_state: SketchState):
        """Test full happy path stage progression."""
        state = initial_state
        expected_stages = [
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

        for stage in expected_stages:
            state = update_stage(state, stage)
            assert state["current_stage"] == stage.value

        # Should have all stages in history
        assert len(state["stage_history"]) == 12  # init + 11 stages

    def test_revision_loop(self, initial_state: SketchState):
        """Test revision loop stage transitions."""
        state = initial_state
        # Progress to revision
        state = update_stage(state, WorkflowStage.SCRIPT_DRAFTING)
        state = update_stage(state, WorkflowStage.TABLE_READ)

        # Multiple revision cycles
        for i in range(3):
            state = update_stage(state, WorkflowStage.REVISION)
            state["iteration_count"] = i + 1

        assert state["iteration_count"] == 3
        # Multiple revision entries in history
        revision_entries = [h for h in state["stage_history"] if h["stage"] == "revision"]
        assert len(revision_entries) == 3
