"""
Workflow state definition for the sketch comedy writing system.

Defines the SketchState TypedDict that persists across all workflow nodes,
containing all data needed throughout the 6-stage writing process.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Annotated, Any, Optional, TypedDict

from langgraph.graph import add_messages

logger = logging.getLogger(__name__)


class WorkflowStage(Enum):
    """Enumeration of workflow stages."""

    INITIALIZATION = "initialization"
    PITCH_SESSION = "pitch_session"
    HUMAN_PITCH_REVIEW = "human_pitch_review"
    SHOWRUNNER_SELECT = "showrunner_select"
    STORY_BREAKING = "story_breaking"
    HUMAN_BEAT_REVIEW = "human_beat_review"
    SCRIPT_DRAFTING = "script_drafting"
    TABLE_READ = "table_read"
    REVISION = "revision"
    POLISH = "polish"
    HUMAN_FINAL_REVIEW = "human_final_review"
    COMPLETE = "complete"


@dataclass
class Pitch:
    """A single pitch concept from a writer."""

    id: str
    title: str
    logline: str
    game: str
    agent: str
    character_types: list[str] = field(default_factory=list)
    escalation_path: str = ""
    research_notes: str = ""
    score: Optional[float] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert pitch to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "logline": self.logline,
            "game": self.game,
            "agent": self.agent,
            "character_types": self.character_types,
            "escalation_path": self.escalation_path,
            "research_notes": self.research_notes,
            "score": self.score,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Pitch":
        """Create pitch from dictionary."""
        return cls(
            id=data.get("id", ""),
            title=data.get("title", ""),
            logline=data.get("logline", ""),
            game=data.get("game", ""),
            agent=data.get("agent", ""),
            character_types=data.get("character_types", []),
            escalation_path=data.get("escalation_path", ""),
            research_notes=data.get("research_notes", ""),
            score=data.get("score"),
        )


@dataclass
class TableReadFeedback:
    """Feedback from a single agent during table read."""

    agent: str
    focus_area: str
    issues: list[dict[str, Any]] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    raw_content: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert feedback to dictionary."""
        return {
            "agent": self.agent,
            "focus_area": self.focus_area,
            "issues": self.issues,
            "strengths": self.strengths,
            "suggestions": self.suggestions,
            "raw_content": self.raw_content,
        }


@dataclass
class QAReport:
    """Quality assurance report from QA agent."""

    approved: bool
    confidence_score: int  # 1-10
    checklist_results: dict[str, dict[str, bool]] = field(default_factory=dict)
    critical_issues: list[str] = field(default_factory=list)
    minor_issues: list[str] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)
    raw_content: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "approved": self.approved,
            "confidence_score": self.confidence_score,
            "checklist_results": self.checklist_results,
            "critical_issues": self.critical_issues,
            "minor_issues": self.minor_issues,
            "strengths": self.strengths,
            "raw_content": self.raw_content,
        }


class SketchState(TypedDict, total=False):
    """
    Complete state for the sketch comedy writing workflow.

    This TypedDict persists across all workflow nodes and contains all data
    needed throughout the 6-stage writing process. Fields are organized by
    the stage where they are primarily used.

    Attributes:
        Configuration (loaded at start):
            show_bible: Content of show_bible.md
            creative_prompt: Content of creative_prompt.md
            session_id: Unique identifier for this writing session
            target_length: Target sketch length in pages
            max_revision_cycles: Maximum revision iterations allowed

        Stage 1 - Pitch Session:
            pitches: All pitch concepts from writers
            research_notes_pitches: Research validation for pitches
            compiled_pitches: Head Writer's compiled pitch document

        Human Checkpoint #1:
            human_selected_pitches: Pitch IDs selected by human
            human_pitch_notes: Human's notes on selected pitches

        Showrunner Selection:
            showrunner_selected_pitch: Final pitch chosen by Showrunner
            showrunner_vision_notes: Creative direction from Showrunner

        Stage 2 - Story Breaking:
            character_details: Character development from Senior Writer A
            joke_map: Joke density mapping from Senior Writer B
            structural_framework: Structure from Staff Writer B
            research_details: Supporting details from Research Agent
            story_editor_validation: Validation from Story Editor
            beat_sheet: Synthesized beat sheet from Head Writer

        Human Checkpoint #2:
            human_beat_sheet_approval: Whether human approved beat sheet
            human_beat_sheet_notes: Human's notes on beat sheet

        Stage 3 - Script Drafting:
            section_assignments: Which agent writes which section
            drafted_sections: Individual drafted sections
            first_draft: Assembled first draft
            showrunner_draft_notes: Showrunner's notes on first draft

        Stage 4 - Table Read:
            table_read_feedback: Feedback from all reviewing agents
            story_editor_report: Compiled issues from Story Editor
            revision_plan: Head Writer's revision plan

        Stage 5 - Revision:
            revision_assignments: Which agent fixes what
            revised_sections: Individual revised sections
            revised_draft: Integrated revised draft
            iteration_count: Current revision cycle number
            showrunner_revision_approved: Whether Showrunner approved revision

        Stage 6 - Polish:
            formatted_script: Script after formatting
            qa_report: Quality assurance report
            showrunner_final_review: Showrunner's final review

        Human Checkpoint #3:
            human_final_approval: Whether human approved final script
            human_final_notes: Human's notes on final script

        Final Output:
            final_script: Production-ready script

        Metadata:
            current_stage: Current workflow stage
            stage_history: List of completed stages with timestamps
            error_log: Any errors encountered
            token_usage: Cumulative token usage tracking
    """

    # Configuration (loaded at initialization)
    show_bible: str
    creative_prompt: str
    session_id: str
    target_length: int
    max_revision_cycles: int

    # Stage 1: Pitch Session
    pitches: list[dict[str, Any]]
    research_notes_pitches: dict[str, Any]
    compiled_pitches: str

    # Human Checkpoint #1
    human_selected_pitches: list[str]
    human_pitch_notes: str

    # Showrunner Selection
    showrunner_selected_pitch: str
    showrunner_vision_notes: str

    # Stage 2: Story Breaking
    character_details: dict[str, Any]
    joke_map: dict[str, Any]
    structural_framework: dict[str, Any]
    research_details: dict[str, Any]
    story_editor_validation: dict[str, Any]
    beat_sheet: str

    # Human Checkpoint #2
    human_beat_sheet_approval: bool
    human_beat_sheet_notes: str

    # Stage 3: Script Drafting
    section_assignments: dict[str, Any]
    drafted_sections: list[dict[str, Any]]
    first_draft: str
    showrunner_draft_notes: str

    # Stage 4: Table Read
    table_read_feedback: list[dict[str, Any]]
    story_editor_report: str
    revision_plan: str

    # Stage 5: Revision
    revision_assignments: dict[str, Any]
    revised_sections: list[dict[str, Any]]
    revised_draft: str
    iteration_count: int
    showrunner_revision_approved: bool

    # Stage 6: Polish
    formatted_script: str
    qa_report: dict[str, Any]
    showrunner_final_review: str

    # Human Checkpoint #3
    human_final_approval: bool
    human_final_notes: str

    # Final Output
    final_script: str

    # Metadata
    current_stage: str
    stage_history: list[dict[str, Any]]
    error_log: list[dict[str, Any]]
    token_usage: dict[str, int]


def create_initial_state(
    show_bible: str,
    creative_prompt: str,
    session_id: Optional[str] = None,
    target_length: int = 5,
    max_revision_cycles: int = 3,
) -> SketchState:
    """
    Create initial state for a new writing session.

    Args:
        show_bible: Content of show_bible.md file.
        creative_prompt: Content of creative_prompt.md file.
        session_id: Optional session identifier. If None, generates one.
        target_length: Target sketch length in pages.
        max_revision_cycles: Maximum revision iterations.

    Returns:
        Initialized SketchState with all required fields.
    """
    if session_id is None:
        session_id = f"sketch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    logger.info("Creating initial state for session: %s", session_id)

    return SketchState(
        # Configuration
        show_bible=show_bible,
        creative_prompt=creative_prompt,
        session_id=session_id,
        target_length=target_length,
        max_revision_cycles=max_revision_cycles,
        # Stage 1
        pitches=[],
        research_notes_pitches={},
        compiled_pitches="",
        # Human Checkpoint #1
        human_selected_pitches=[],
        human_pitch_notes="",
        # Showrunner Selection
        showrunner_selected_pitch="",
        showrunner_vision_notes="",
        # Stage 2
        character_details={},
        joke_map={},
        structural_framework={},
        research_details={},
        story_editor_validation={},
        beat_sheet="",
        # Human Checkpoint #2
        human_beat_sheet_approval=False,
        human_beat_sheet_notes="",
        # Stage 3
        section_assignments={},
        drafted_sections=[],
        first_draft="",
        showrunner_draft_notes="",
        # Stage 4
        table_read_feedback=[],
        story_editor_report="",
        revision_plan="",
        # Stage 5
        revision_assignments={},
        revised_sections=[],
        revised_draft="",
        iteration_count=0,
        showrunner_revision_approved=False,
        # Stage 6
        formatted_script="",
        qa_report={},
        showrunner_final_review="",
        # Human Checkpoint #3
        human_final_approval=False,
        human_final_notes="",
        # Final
        final_script="",
        # Metadata
        current_stage=WorkflowStage.INITIALIZATION.value,
        stage_history=[
            {
                "stage": WorkflowStage.INITIALIZATION.value,
                "timestamp": datetime.now().isoformat(),
                "status": "started",
            }
        ],
        error_log=[],
        token_usage={
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        },
    )


def update_stage(state: SketchState, new_stage: WorkflowStage) -> SketchState:
    """
    Update the current stage and record in history.

    Args:
        state: Current workflow state.
        new_stage: Stage to transition to.

    Returns:
        Updated state with new stage.
    """
    logger.info("Transitioning from %s to %s", state.get("current_stage"), new_stage.value)

    history = state.get("stage_history", [])
    history.append(
        {
            "stage": new_stage.value,
            "timestamp": datetime.now().isoformat(),
            "status": "started",
        }
    )

    return {
        **state,
        "current_stage": new_stage.value,
        "stage_history": history,
    }


def add_error(state: SketchState, error: str, context: Optional[str] = None) -> SketchState:
    """
    Add an error to the error log.

    Args:
        state: Current workflow state.
        error: Error message.
        context: Optional context about where error occurred.

    Returns:
        Updated state with error logged.
    """
    logger.error("Workflow error: %s (context: %s)", error, context)

    error_log = state.get("error_log", [])
    error_log.append(
        {
            "error": error,
            "context": context,
            "stage": state.get("current_stage"),
            "timestamp": datetime.now().isoformat(),
        }
    )

    return {**state, "error_log": error_log}


def update_token_usage(
    state: SketchState,
    prompt_tokens: int,
    completion_tokens: int,
) -> SketchState:
    """
    Update cumulative token usage.

    Args:
        state: Current workflow state.
        prompt_tokens: Prompt tokens used.
        completion_tokens: Completion tokens used.

    Returns:
        Updated state with token usage added.
    """
    usage = state.get("token_usage", {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0})

    new_usage = {
        "prompt_tokens": usage["prompt_tokens"] + prompt_tokens,
        "completion_tokens": usage["completion_tokens"] + completion_tokens,
        "total_tokens": usage["total_tokens"] + prompt_tokens + completion_tokens,
    }

    logger.debug(
        "Token usage updated: +%d prompt, +%d completion (total: %d)",
        prompt_tokens,
        completion_tokens,
        new_usage["total_tokens"],
    )

    return {**state, "token_usage": new_usage}
