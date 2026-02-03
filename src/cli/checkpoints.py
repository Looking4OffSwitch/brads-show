"""
Human checkpoint handlers for the sketch comedy writing system.

Provides functions for handling the 3 human checkpoints:
1. Pitch review and selection
2. Beat sheet approval
3. Final script approval
"""

import logging
from typing import Any, Optional

from src.cli.interface import (
    display_beat_sheet,
    display_error,
    display_header,
    display_info,
    display_pitches,
    display_qa_report,
    display_script,
    display_subheader,
    display_success,
    display_warning,
    prompt_selection,
    prompt_user,
    prompt_yes_no,
)
from src.workflow.state import SketchState

logger = logging.getLogger(__name__)


def handle_pitch_review(state: SketchState) -> dict[str, Any]:
    """
    Handle Human Checkpoint #1: Pitch Review.

    Displays all pitches and allows human to select which to develop.

    Args:
        state: Current workflow state with pitches.

    Returns:
        Dictionary with human selections and notes to update state.
    """
    display_header("HUMAN CHECKPOINT #1: PITCH REVIEW")

    pitches = state.get("pitches", [])
    compiled = state.get("compiled_pitches", "")

    if not pitches:
        display_error("No pitches available for review")
        return {
            "human_selected_pitches": [],
            "human_pitch_notes": "No pitches to review",
        }

    # Display compiled pitches if available
    if compiled:
        display_subheader("COMPILED PITCH DOCUMENT")
        print(compiled)
        print()

    # Display individual pitches
    display_pitches(pitches)

    # Display research notes if available
    research_notes = state.get("research_notes_pitches", {})
    if research_notes:
        display_subheader("RESEARCH NOTES")
        print(research_notes.get("content", "No notes"))
        print()

    # Prompt for selection
    display_info("Select 1-3 pitches to develop (the Showrunner will make final selection)")

    pitch_options = [f"Pitch #{i+1}: {p.get('agent', 'Unknown')}" for i, p in enumerate(pitches)]

    selected_indices = prompt_selection(
        "Which pitches would you like to develop?",
        pitch_options,
        allow_multiple=True,
    )

    # Map to pitch IDs
    selected_ids = [pitches[i]["id"] for i in selected_indices if i < len(pitches)]

    # Get notes
    notes = prompt_user(
        "Any direction or notes for the selected pitch(es)?",
        default="No specific notes",
    )

    display_success(f"Selected {len(selected_ids)} pitch(es) for development")

    return {
        "human_selected_pitches": selected_ids,
        "human_pitch_notes": notes,
    }


def handle_beat_review(state: SketchState) -> dict[str, Any]:
    """
    Handle Human Checkpoint #2: Beat Sheet Review.

    Displays the beat sheet and allows human to approve or request changes.

    Args:
        state: Current workflow state with beat sheet.

    Returns:
        Dictionary with approval status and notes to update state.
    """
    display_header("HUMAN CHECKPOINT #2: BEAT SHEET REVIEW")

    beat_sheet = state.get("beat_sheet", "")

    if not beat_sheet:
        display_error("No beat sheet available for review")
        return {
            "human_beat_sheet_approval": False,
            "human_beat_sheet_notes": "No beat sheet to review",
        }

    # Display beat sheet
    display_beat_sheet(beat_sheet)

    # Display validation if available
    validation = state.get("story_editor_validation", {})
    if validation:
        display_subheader("STORY EDITOR VALIDATION")
        print(validation.get("content", "No validation"))
        print()

    # Prompt for approval
    approved = prompt_yes_no(
        "Do you approve this beat sheet for script drafting?",
        default=True,
    )

    if approved:
        notes = prompt_user(
            "Any notes for the writers? (optional)",
            default="",
        )
        display_success("Beat sheet approved! Proceeding to drafting.")
    else:
        notes = prompt_user(
            "What changes would you like? (required)",
            default="",
        )
        while not notes:
            display_warning("Please provide feedback for revision")
            notes = prompt_user("What changes would you like?")
        display_info("Beat sheet will be revised based on your notes.")

    return {
        "human_beat_sheet_approval": approved,
        "human_beat_sheet_notes": notes,
    }


def handle_final_review(state: SketchState) -> dict[str, Any]:
    """
    Handle Human Checkpoint #3: Final Script Review.

    Displays the final formatted script and QA report for approval.

    Args:
        state: Current workflow state with final script and QA report.

    Returns:
        Dictionary with approval status and notes to update state.
    """
    display_header("HUMAN CHECKPOINT #3: FINAL SCRIPT REVIEW")

    formatted_script = state.get("formatted_script", "")
    qa_report = state.get("qa_report", {})
    showrunner_review = state.get("showrunner_final_review", "")

    if not formatted_script:
        display_error("No formatted script available for review")
        return {
            "human_final_approval": False,
            "human_final_notes": "No script to review",
        }

    # Display QA report
    if qa_report:
        display_qa_report(qa_report)

    # Display Showrunner's final review
    if showrunner_review:
        display_subheader("SHOWRUNNER'S FINAL REVIEW")
        print(showrunner_review)
        print()

    # Display the script
    display_script(formatted_script, "FINAL SCRIPT")

    # Prompt for approval
    approved = prompt_yes_no(
        "Do you approve this script for production?",
        default=True,
    )

    if approved:
        notes = prompt_user(
            "Any production notes? (optional)",
            default="",
        )
        display_success("Script approved for production!")
    else:
        notes = prompt_user(
            "What revisions are needed? (required)",
            default="",
        )
        while not notes:
            display_warning("Please provide feedback for revision")
            notes = prompt_user("What revisions are needed?")
        display_info("Script will be revised based on your notes.")

    return {
        "human_final_approval": approved,
        "human_final_notes": notes,
    }


def handle_checkpoint(
    state: SketchState,
    checkpoint_name: str,
) -> dict[str, Any]:
    """
    Route to appropriate checkpoint handler.

    Args:
        state: Current workflow state.
        checkpoint_name: Name of the checkpoint node.

    Returns:
        Dictionary with updates to apply to state.
    """
    handlers = {
        "human_pitch_review": handle_pitch_review,
        "human_beat_review": handle_beat_review,
        "human_final_review": handle_final_review,
    }

    handler = handlers.get(checkpoint_name)

    if handler is None:
        logger.error("Unknown checkpoint: %s", checkpoint_name)
        return {}

    logger.info("Handling checkpoint: %s", checkpoint_name)
    return handler(state)


def mock_pitch_review(
    state: SketchState,
    select_first: bool = True,
) -> dict[str, Any]:
    """
    Mock handler for pitch review (for testing).

    Args:
        state: Current workflow state.
        select_first: Whether to select the first pitch.

    Returns:
        Dictionary with mocked selections.
    """
    pitches = state.get("pitches", [])

    if not pitches:
        return {
            "human_selected_pitches": [],
            "human_pitch_notes": "Mocked: No pitches",
        }

    if select_first:
        selected = [pitches[0]["id"]]
    else:
        selected = [p["id"] for p in pitches[:3]]

    return {
        "human_selected_pitches": selected,
        "human_pitch_notes": "Mocked: Auto-selected for testing",
    }


def mock_beat_review(
    state: SketchState,
    approve: bool = True,
) -> dict[str, Any]:
    """
    Mock handler for beat sheet review (for testing).

    Args:
        state: Current workflow state.
        approve: Whether to approve the beat sheet.

    Returns:
        Dictionary with mocked approval.
    """
    return {
        "human_beat_sheet_approval": approve,
        "human_beat_sheet_notes": (
            "Mocked: Auto-approved for testing" if approve else "Mocked: Needs revision"
        ),
    }


def mock_final_review(
    state: SketchState,
    approve: bool = True,
) -> dict[str, Any]:
    """
    Mock handler for final review (for testing).

    Args:
        state: Current workflow state.
        approve: Whether to approve the final script.

    Returns:
        Dictionary with mocked approval.
    """
    return {
        "human_final_approval": approve,
        "human_final_notes": (
            "Mocked: Auto-approved for testing" if approve else "Mocked: Needs revision"
        ),
    }


def mock_checkpoint(
    state: SketchState,
    checkpoint_name: str,
    approve: bool = True,
) -> dict[str, Any]:
    """
    Route to appropriate mock checkpoint handler.

    Args:
        state: Current workflow state.
        checkpoint_name: Name of the checkpoint node.
        approve: Whether to approve (where applicable).

    Returns:
        Dictionary with mocked updates.
    """
    handlers = {
        "human_pitch_review": lambda s: mock_pitch_review(s),
        "human_beat_review": lambda s: mock_beat_review(s, approve),
        "human_final_review": lambda s: mock_final_review(s, approve),
    }

    handler = handlers.get(checkpoint_name)

    if handler is None:
        logger.error("Unknown checkpoint: %s", checkpoint_name)
        return {}

    logger.info("Mocking checkpoint: %s", checkpoint_name)
    return handler(state)
