"""
Unit tests for workflow edge functions.

Tests the src/workflow/edges module including:
- should_revise_beat_sheet
- should_continue_revision
- should_approve_final
- should_skip_to_polish
- get_next_stage_after_pitch_review
- check_qa_gate
"""

import pytest

from src.workflow.edges import (
    check_qa_gate,
    get_next_stage_after_pitch_review,
    should_approve_final,
    should_continue_revision,
    should_revise_beat_sheet,
    should_skip_to_polish,
)
from src.workflow.state import SketchState, create_initial_state


# =============================================================================
# SHOULD REVISE BEAT SHEET TESTS
# =============================================================================


class TestShouldReviseBeatSheet:
    """Tests for should_revise_beat_sheet function."""

    def test_approved_when_approval_true(self):
        """Test that approved flag returns 'approved'."""
        state = create_initial_state("bible", "prompt")
        state["human_beat_sheet_approval"] = True
        result = should_revise_beat_sheet(state)
        assert result == "approved"

    def test_needs_revision_when_approval_false(self):
        """Test that False approval returns 'needs_revision'."""
        state = create_initial_state("bible", "prompt")
        state["human_beat_sheet_approval"] = False
        result = should_revise_beat_sheet(state)
        assert result == "needs_revision"

    def test_needs_revision_when_approval_missing(self):
        """Test that missing approval defaults to 'needs_revision'."""
        state = create_initial_state("bible", "prompt")
        # Don't set human_beat_sheet_approval - should default to False
        result = should_revise_beat_sheet(state)
        assert result == "needs_revision"

    def test_approved_with_notes(self):
        """Test approval with notes still returns 'approved'."""
        state = create_initial_state("bible", "prompt")
        state["human_beat_sheet_approval"] = True
        state["human_beat_sheet_notes"] = "Looks great, minor polish needed"
        result = should_revise_beat_sheet(state)
        assert result == "approved"

    def test_needs_revision_with_notes(self):
        """Test rejection with notes returns 'needs_revision'."""
        state = create_initial_state("bible", "prompt")
        state["human_beat_sheet_approval"] = False
        state["human_beat_sheet_notes"] = "Need more escalation in act 2"
        result = should_revise_beat_sheet(state)
        assert result == "needs_revision"


# =============================================================================
# SHOULD CONTINUE REVISION TESTS
# =============================================================================


class TestShouldContinueRevision:
    """Tests for should_continue_revision function."""

    def test_approved_when_showrunner_approves(self):
        """Test that Showrunner approval returns 'approved'."""
        state = create_initial_state("bible", "prompt")
        state["iteration_count"] = 1
        state["showrunner_revision_approved"] = True
        result = should_continue_revision(state)
        assert result == "approved"

    def test_needs_more_revision_when_not_approved(self):
        """Test that unapproved revision returns 'needs_more_revision'."""
        state = create_initial_state("bible", "prompt")
        state["iteration_count"] = 1
        state["showrunner_revision_approved"] = False
        result = should_continue_revision(state)
        assert result == "needs_more_revision"

    def test_max_iterations_at_limit(self):
        """Test that hitting max iterations returns 'max_iterations'."""
        state = create_initial_state("bible", "prompt", max_revision_cycles=3)
        state["iteration_count"] = 3
        state["showrunner_revision_approved"] = False
        result = should_continue_revision(state)
        assert result == "max_iterations"

    def test_max_iterations_over_limit(self):
        """Test that exceeding max iterations returns 'max_iterations'."""
        state = create_initial_state("bible", "prompt", max_revision_cycles=3)
        state["iteration_count"] = 5
        state["showrunner_revision_approved"] = False
        result = should_continue_revision(state)
        assert result == "max_iterations"

    def test_max_iterations_trumps_approval(self):
        """Test that max iterations is checked before approval."""
        state = create_initial_state("bible", "prompt", max_revision_cycles=3)
        state["iteration_count"] = 3
        state["showrunner_revision_approved"] = True  # Approved but at max
        result = should_continue_revision(state)
        # Note: Current implementation checks max_iterations first
        assert result == "max_iterations"

    def test_approved_before_max(self):
        """Test approval before reaching max iterations."""
        state = create_initial_state("bible", "prompt", max_revision_cycles=5)
        state["iteration_count"] = 2
        state["showrunner_revision_approved"] = True
        result = should_continue_revision(state)
        assert result == "approved"

    def test_defaults_when_fields_missing(self):
        """Test defaults when optional fields are missing."""
        state = create_initial_state("bible", "prompt")
        # Don't set iteration_count or showrunner_revision_approved
        result = should_continue_revision(state)
        # iteration_count defaults to 0, approval defaults to False
        assert result == "needs_more_revision"

    def test_iteration_count_one_below_max(self):
        """Test at one iteration below max."""
        state = create_initial_state("bible", "prompt", max_revision_cycles=3)
        state["iteration_count"] = 2
        state["showrunner_revision_approved"] = False
        result = should_continue_revision(state)
        assert result == "needs_more_revision"

    def test_custom_max_iterations(self):
        """Test with custom max iterations setting."""
        state = create_initial_state("bible", "prompt", max_revision_cycles=10)
        state["iteration_count"] = 5
        state["showrunner_revision_approved"] = False
        result = should_continue_revision(state)
        assert result == "needs_more_revision"


# =============================================================================
# SHOULD APPROVE FINAL TESTS
# =============================================================================


class TestShouldApproveFinal:
    """Tests for should_approve_final function."""

    def test_approved_when_approval_true(self):
        """Test that True approval returns 'approved'."""
        state = create_initial_state("bible", "prompt")
        state["human_final_approval"] = True
        result = should_approve_final(state)
        assert result == "approved"

    def test_needs_revision_when_approval_false(self):
        """Test that False approval returns 'needs_revision'."""
        state = create_initial_state("bible", "prompt")
        state["human_final_approval"] = False
        result = should_approve_final(state)
        assert result == "needs_revision"

    def test_needs_revision_when_approval_missing(self):
        """Test that missing approval defaults to 'needs_revision'."""
        state = create_initial_state("bible", "prompt")
        result = should_approve_final(state)
        assert result == "needs_revision"

    def test_approved_with_notes(self):
        """Test approval with celebratory notes."""
        state = create_initial_state("bible", "prompt")
        state["human_final_approval"] = True
        state["human_final_notes"] = "Great work! Ready for production."
        result = should_approve_final(state)
        assert result == "approved"

    def test_needs_revision_with_detailed_notes(self):
        """Test rejection with detailed revision notes."""
        state = create_initial_state("bible", "prompt")
        state["human_final_approval"] = False
        state["human_final_notes"] = "The ending needs work. Punchline falls flat."
        result = should_approve_final(state)
        assert result == "needs_revision"


# =============================================================================
# SHOULD SKIP TO POLISH TESTS
# =============================================================================


class TestShouldSkipToPolish:
    """Tests for should_skip_to_polish function."""

    def test_always_continues(self):
        """Test that function always returns 'continue'."""
        state = create_initial_state("bible", "prompt")
        result = should_skip_to_polish(state)
        assert result == "continue"

    def test_continues_with_any_state(self):
        """Test that any state returns 'continue'."""
        state = create_initial_state("bible", "prompt")
        state["first_draft"] = "Some draft content"
        state["iteration_count"] = 2
        result = should_skip_to_polish(state)
        assert result == "continue"


# =============================================================================
# GET NEXT STAGE AFTER PITCH REVIEW TESTS
# =============================================================================


class TestGetNextStageAfterPitchReview:
    """Tests for get_next_stage_after_pitch_review function."""

    def test_always_returns_showrunner_select(self):
        """Test that function always returns 'showrunner_select'."""
        state = create_initial_state("bible", "prompt")
        result = get_next_stage_after_pitch_review(state)
        assert result == "showrunner_select"

    def test_with_selected_pitches(self):
        """Test with pitches selected."""
        state = create_initial_state("bible", "prompt")
        state["human_selected_pitches"] = ["pitch_001", "pitch_002"]
        result = get_next_stage_after_pitch_review(state)
        assert result == "showrunner_select"

    def test_with_empty_selection(self):
        """Test with empty selection (defaults to showrunner selecting all)."""
        state = create_initial_state("bible", "prompt")
        state["human_selected_pitches"] = []
        result = get_next_stage_after_pitch_review(state)
        assert result == "showrunner_select"

    def test_with_single_selection(self):
        """Test with single pitch selected."""
        state = create_initial_state("bible", "prompt")
        state["human_selected_pitches"] = ["pitch_001"]
        result = get_next_stage_after_pitch_review(state)
        assert result == "showrunner_select"


# =============================================================================
# CHECK QA GATE TESTS
# =============================================================================


class TestCheckQAGate:
    """Tests for check_qa_gate function."""

    def test_pass_when_qa_approved(self):
        """Test that QA approval returns 'pass'."""
        state = create_initial_state("bible", "prompt")
        state["qa_report"] = {"approved": True, "confidence_score": 8}
        result = check_qa_gate(state)
        assert result == "pass"

    def test_fail_when_qa_rejected(self):
        """Test that QA rejection returns 'fail'."""
        state = create_initial_state("bible", "prompt")
        state["qa_report"] = {"approved": False, "confidence_score": 3}
        result = check_qa_gate(state)
        assert result == "fail"

    def test_fail_when_qa_report_missing(self):
        """Test that missing QA report defaults to 'fail'."""
        state = create_initial_state("bible", "prompt")
        # No qa_report set
        result = check_qa_gate(state)
        assert result == "fail"

    def test_fail_when_approved_field_missing(self):
        """Test that missing approved field defaults to 'fail'."""
        state = create_initial_state("bible", "prompt")
        state["qa_report"] = {"confidence_score": 7}  # No approved field
        result = check_qa_gate(state)
        assert result == "fail"

    def test_pass_with_detailed_report(self):
        """Test pass with full QA report."""
        state = create_initial_state("bible", "prompt")
        state["qa_report"] = {
            "approved": True,
            "confidence_score": 9,
            "checklist_results": {"formatting": True, "content": True},
            "strengths": ["Great structure", "Strong jokes"],
            "critical_issues": [],
        }
        result = check_qa_gate(state)
        assert result == "pass"

    def test_fail_with_critical_issues(self):
        """Test fail with critical issues in report."""
        state = create_initial_state("bible", "prompt")
        state["qa_report"] = {
            "approved": False,
            "confidence_score": 4,
            "critical_issues": ["Game unclear", "Ending weak"],
        }
        result = check_qa_gate(state)
        assert result == "fail"


# =============================================================================
# EDGE INTEGRATION TESTS
# =============================================================================


class TestEdgeIntegration:
    """Integration tests for edge functions in typical workflow scenarios."""

    def test_happy_path_beat_to_draft(self, state_approved_beat_sheet: SketchState):
        """Test happy path from beat approval to drafting."""
        result = should_revise_beat_sheet(state_approved_beat_sheet)
        assert result == "approved"

    def test_revision_needed_beat_sheet(self, state_needs_revision: SketchState):
        """Test revision path for beat sheet."""
        result = should_revise_beat_sheet(state_needs_revision)
        assert result == "needs_revision"

    def test_revision_cycle_continues(self, state_in_revision: SketchState):
        """Test revision cycle continues when not approved."""
        state_in_revision["showrunner_revision_approved"] = False
        state_in_revision["iteration_count"] = 1
        result = should_continue_revision(state_in_revision)
        assert result == "needs_more_revision"

    def test_revision_cycle_max_reached(self, state_max_revisions: SketchState):
        """Test revision cycle stops at max iterations."""
        state_max_revisions["showrunner_revision_approved"] = False
        result = should_continue_revision(state_max_revisions)
        assert result == "max_iterations"

    def test_final_approval_workflow(self, state_final_approved: SketchState):
        """Test final approval in workflow."""
        result = should_approve_final(state_final_approved)
        assert result == "approved"

    def test_final_needs_revision(self, state_final_review: SketchState):
        """Test final review needs revision."""
        state_final_review["human_final_approval"] = False
        state_final_review["human_final_notes"] = "Not quite there yet"
        result = should_approve_final(state_final_review)
        assert result == "needs_revision"


# =============================================================================
# BOUNDARY AND EDGE CASE TESTS
# =============================================================================


class TestBoundaryConditions:
    """Boundary condition tests for edge functions."""

    def test_iteration_count_exactly_at_max(self):
        """Test iteration count exactly at max boundary."""
        state = create_initial_state("bible", "prompt", max_revision_cycles=3)
        state["iteration_count"] = 3
        state["showrunner_revision_approved"] = True
        # At max, should return max_iterations regardless of approval
        result = should_continue_revision(state)
        assert result == "max_iterations"

    def test_iteration_count_just_below_max(self):
        """Test iteration count just below max boundary."""
        state = create_initial_state("bible", "prompt", max_revision_cycles=3)
        state["iteration_count"] = 2
        state["showrunner_revision_approved"] = True
        # Just below max with approval should be approved
        result = should_continue_revision(state)
        assert result == "approved"

    def test_zero_max_iterations(self):
        """Test edge case of zero max iterations."""
        state = create_initial_state("bible", "prompt")
        state["max_revision_cycles"] = 0
        state["iteration_count"] = 0
        state["showrunner_revision_approved"] = False
        # Even at 0/0, should trigger max_iterations
        result = should_continue_revision(state)
        assert result == "max_iterations"

    def test_empty_string_notes(self):
        """Test with empty string notes."""
        state = create_initial_state("bible", "prompt")
        state["human_beat_sheet_approval"] = False
        state["human_beat_sheet_notes"] = ""
        result = should_revise_beat_sheet(state)
        assert result == "needs_revision"

    def test_whitespace_only_notes(self):
        """Test with whitespace-only notes."""
        state = create_initial_state("bible", "prompt")
        state["human_final_approval"] = True
        state["human_final_notes"] = "   \n\t  "
        result = should_approve_final(state)
        assert result == "approved"
