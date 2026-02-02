"""
Workflow edge functions for conditional routing.

These functions determine which path to take at decision points in the workflow.
"""

import logging
from typing import Literal

from src.workflow.state import SketchState

logger = logging.getLogger(__name__)


def should_revise_beat_sheet(state: SketchState) -> Literal["approved", "needs_revision"]:
    """
    Decide if beat sheet needs revision after human review.

    Routes to:
    - "approved": Proceed to script drafting
    - "needs_revision": Loop back to story breaking

    Args:
        state: Current workflow state with human feedback.

    Returns:
        Routing decision string.
    """
    approval = state.get("human_beat_sheet_approval", False)
    notes = state.get("human_beat_sheet_notes", "")

    if approval:
        logger.info("Beat sheet approved by human, proceeding to drafting")
        return "approved"
    else:
        logger.info("Beat sheet needs revision: %s", notes[:100] if notes else "No notes")
        return "needs_revision"


def should_continue_revision(
    state: SketchState,
) -> Literal["approved", "needs_more_revision", "max_iterations"]:
    """
    Decide if revision cycle should continue.

    Routes to:
    - "approved": Revision is good, proceed to polish
    - "needs_more_revision": Loop back to table read for another cycle
    - "max_iterations": Hit max iterations, force proceed to polish

    Args:
        state: Current workflow state with revision results.

    Returns:
        Routing decision string.
    """
    iteration_count = state.get("iteration_count", 0)
    max_iterations = state.get("max_revision_cycles", 3)
    showrunner_approved = state.get("showrunner_revision_approved", False)

    # Check if we've hit max iterations
    if iteration_count >= max_iterations:
        logger.warning(
            "Max revision iterations (%d) reached, forcing proceed to polish",
            max_iterations,
        )
        return "max_iterations"

    # Check if Showrunner approved
    if showrunner_approved:
        logger.info("Showrunner approved revision, proceeding to polish")
        return "approved"

    # Need more work
    logger.info(
        "Revision cycle %d: needs more work (max: %d)",
        iteration_count,
        max_iterations,
    )
    return "needs_more_revision"


def should_approve_final(
    state: SketchState,
) -> Literal["approved", "needs_revision"]:
    """
    Decide if final script is approved after human review.

    Routes to:
    - "approved": Script is done, workflow complete
    - "needs_revision": Loop back to revision for more work

    Args:
        state: Current workflow state with human final review.

    Returns:
        Routing decision string.
    """
    approval = state.get("human_final_approval", False)
    notes = state.get("human_final_notes", "")

    if approval:
        logger.info("Final script approved by human, workflow complete!")
        return "approved"
    else:
        logger.info("Final script needs revision: %s", notes[:100] if notes else "No notes")
        return "needs_revision"


def should_skip_to_polish(state: SketchState) -> Literal["skip", "continue"]:
    """
    Check if we should skip table read (e.g., after beat sheet revision).

    This is used when looping back from human beat review - we don't need
    a full table read on a revised beat sheet.

    Args:
        state: Current workflow state.

    Returns:
        "skip" to go directly to polish, "continue" for normal flow.
    """
    # For now, always continue normal flow
    # Could add logic to skip based on minor revisions
    return "continue"


def get_next_stage_after_pitch_review(state: SketchState) -> str:
    """
    Determine next stage after pitch review based on selections.

    Args:
        state: Current workflow state.

    Returns:
        Next node name.
    """
    selected = state.get("human_selected_pitches", [])

    if not selected:
        logger.warning("No pitches selected, defaulting to showrunner selection of all")

    return "showrunner_select"


def check_qa_gate(state: SketchState) -> Literal["pass", "fail"]:
    """
    Check if QA gate allows progression to human final review.

    Args:
        state: Current workflow state with QA report.

    Returns:
        "pass" if QA approved, "fail" if blocked.
    """
    qa_report = state.get("qa_report", {})
    approved = qa_report.get("approved", False)

    if approved:
        logger.info("QA gate passed")
        return "pass"
    else:
        logger.warning("QA gate failed - script needs more work")
        return "fail"
