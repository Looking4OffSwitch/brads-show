"""
Pytest configuration and shared fixtures for the sketch comedy writing system tests.

This module provides:
- Configuration fixtures (mock config, test show data)
- LLM mock fixtures for testing without API calls
- State fixtures for workflow testing
- Utility fixtures for common test scenarios
"""

import os
import tempfile
from pathlib import Path
from typing import Any, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.utils.config import Config, LLMConfig, ShowConfig, WorkflowConfig
from src.utils.llm import LLMInterface, LLMResponse, ModelTier, TokenUsage
from src.workflow.state import SketchState, create_initial_state


# =============================================================================
# SAMPLE DATA
# =============================================================================

SAMPLE_SHOW_BIBLE = """# Show Bible: Test Show

## Show Identity
### Show Name
Test Show

### What's This Show About?
A test sketch comedy show for unit testing purposes.

## Tone & Style
### Overall Tone
Absurdist-Grounded Hybrid

### Comedy Styles We Embrace
- Character Commitment Comedy
- Escalating Specificity

### Comedy Styles We Avoid
- Mean-Spirited Punching Down

## Content Guidelines
### Topics We Love
- Workplace absurdity
- Service industry extremes

### Topics We Avoid
- Explicit political content

## Reference Points
### Sketches We Love
- "Baby of the Year" (I Think You Should Leave)

## Character Types That Work
- Absurdly Confident Experts
- Rule-Followers in Absurd Systems
"""

SAMPLE_CREATIVE_PROMPT = """# Creative Prompt

## Core Idea (Required)
A tech support agent who treats basic computer problems like life-saving surgery.

### What Sparked This
I was on hold with tech support for 2 hours.

## Specific Requirements
### Must Include
- "Have you tried turning it off and on again?" delivered dramatically
- Computer referred to as "the patient"

### Characters
- Tech support agent with surgeon-level intensity
- Confused customer who just wants their printer to work

## What I'm Hoping For
A sketch that makes fun of how seriously tech support can take minor problems.
"""

SAMPLE_PITCH_CONTENT = """# PITCH CONCEPTS - Staff Writer A

## PITCH #1: Tech Support ER

**Logline:**
A tech support agent treats a simple printer issue like a life-or-death surgery.

**The Game:**
Every mundane computer problem gets the full medical drama treatment.

**Why This Is Fresh:**
Combines medical drama tropes with tech support frustration.
"""

SAMPLE_BEAT_SHEET = """# BEAT SHEET: Tech Support ER

## Premise & Game
**Core Premise:** Tech support agent treats printer problems like surgery
**The Game:** Medical drama escalation for mundane tech issues
**Target Length:** 5 pages

## Characters
**DR. KEVIN MATTHEWS** - Tech support agent, 30s, deadly serious
**SARAH CHEN** - Customer, 40s, just wants to print

## Beat-by-Beat Breakdown

### BEAT 1: OPEN (Page 1)
Sarah calls tech support. Kevin answers like he's in an OR.

### BEAT 2: GAME INTRODUCTION (Page 1-2)
Kevin asks Sarah to "prep the patient" (restart the computer).

### BEAT 3: HEIGHTEN (Page 2-3)
Kevin recruits Sarah as his "surgical assistant."

### BEAT 4: BLOW (Page 4-5)
Solution is embarrassingly simple - it wasn't plugged in.
"""


# =============================================================================
# CONFIGURATION FIXTURES
# =============================================================================


@pytest.fixture
def sample_show_bible() -> str:
    """Return sample show bible content."""
    return SAMPLE_SHOW_BIBLE


@pytest.fixture
def sample_creative_prompt() -> str:
    """Return sample creative prompt content."""
    return SAMPLE_CREATIVE_PROMPT


@pytest.fixture
def temp_project_dir(
    sample_show_bible: str,
    sample_creative_prompt: str,
) -> Generator[Path, None, None]:
    """
    Create a temporary project directory with test show files.

    Yields:
        Path to temporary project root.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

        # Create directory structure
        shows_dir = root / "Shows" / "test_show"
        shows_dir.mkdir(parents=True)
        (shows_dir / "output").mkdir()

        # Create config files
        (root / "pyproject.toml").write_text("[project]\nname = 'test'\n")
        (root / ".env").write_text("ANTHROPIC_API_KEY=test-key-12345\nSHOW_FOLDER=test_show\n")

        # Create show files
        (shows_dir / "show_bible.md").write_text(sample_show_bible)
        (shows_dir / "creative_prompt.md").write_text(sample_creative_prompt)

        # Create Docs directory with agent prompts
        docs_dir = root / "Docs"
        docs_dir.mkdir()
        (docs_dir / "agent-prompts.md").write_text("# Agent Prompts\nTest content")

        yield root


@pytest.fixture
def mock_llm_config() -> LLMConfig:
    """Create a mock LLM configuration."""
    return LLMConfig(
        provider="anthropic",
        api_key="test-api-key-12345",
        creative_model="claude-sonnet-4-20250514",
        support_model="claude-3-5-haiku-20241022",
    )


@pytest.fixture
def mock_workflow_config() -> WorkflowConfig:
    """Create a mock workflow configuration."""
    return WorkflowConfig(
        max_revision_cycles=3,
        target_sketch_length=5,
    )


@pytest.fixture
def mock_show_config(
    temp_project_dir: Path,
    sample_show_bible: str,
    sample_creative_prompt: str,
) -> ShowConfig:
    """Create a mock show configuration."""
    return ShowConfig(
        show_folder="test_show",
        show_bible=sample_show_bible,
        creative_prompt=sample_creative_prompt,
        output_dir=temp_project_dir / "Shows" / "test_show" / "output",
    )


@pytest.fixture
def mock_config(
    mock_llm_config: LLMConfig,
    mock_workflow_config: WorkflowConfig,
    mock_show_config: ShowConfig,
    temp_project_dir: Path,
) -> Config:
    """Create a complete mock configuration."""
    return Config(
        llm=mock_llm_config,
        workflow=mock_workflow_config,
        show=mock_show_config,
        project_root=temp_project_dir,
        debug=True,
    )


# =============================================================================
# LLM MOCK FIXTURES
# =============================================================================


class MockLLMInterface(LLMInterface):
    """Mock LLM interface for testing without API calls."""

    def __init__(
        self,
        config: LLMConfig,
        default_response: str = "Mock LLM response for testing.",
    ) -> None:
        """
        Initialize mock LLM.

        Args:
            config: LLM configuration.
            default_response: Default response content.
        """
        super().__init__(config)
        self.default_response = default_response
        self.call_history: list[dict[str, Any]] = []
        self.response_queue: list[str] = []

    def set_response(self, response: str) -> None:
        """Set the next response to return."""
        self.response_queue.append(response)

    def set_responses(self, responses: list[str]) -> None:
        """Set multiple responses to return in order."""
        self.response_queue.extend(responses)

    def get_model(self, tier: ModelTier) -> MagicMock:
        """Return a mock model."""
        return MagicMock()

    async def acall(
        self,
        messages: list,
        tier: ModelTier = ModelTier.CREATIVE,
        *,
        run_name: str | None = None,
        tags: list[str] | None = None,
        metadata: dict | None = None,
    ) -> LLMResponse:
        """
        Mock async LLM call.

        Records call history and returns queued or default response.
        """
        # Record call including tracing metadata
        self.call_history.append({
            "messages": messages,
            "tier": tier,
            "run_name": run_name,
            "tags": tags,
            "metadata": metadata,
        })

        # Get response
        if self.response_queue:
            content = self.response_queue.pop(0)
        else:
            content = self.default_response

        # Simulate token usage
        prompt_tokens = sum(len(str(m)) for m in messages) // 4
        completion_tokens = len(content) // 4
        total_tokens = prompt_tokens + completion_tokens

        self.usage.add(prompt_tokens, completion_tokens, total_tokens)

        return LLMResponse(
            content=content,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            model="mock-model",
        )


@pytest.fixture
def mock_llm(mock_llm_config: LLMConfig) -> MockLLMInterface:
    """Create a mock LLM interface."""
    return MockLLMInterface(mock_llm_config)


@pytest.fixture
def mock_llm_with_pitches(mock_llm_config: LLMConfig) -> MockLLMInterface:
    """Create a mock LLM that returns pitch-like responses."""
    llm = MockLLMInterface(mock_llm_config, SAMPLE_PITCH_CONTENT)
    return llm


# =============================================================================
# STATE FIXTURES
# =============================================================================


@pytest.fixture
def initial_state(
    sample_show_bible: str,
    sample_creative_prompt: str,
) -> SketchState:
    """Create an initial workflow state."""
    return create_initial_state(
        show_bible=sample_show_bible,
        creative_prompt=sample_creative_prompt,
        session_id="test_session_001",
        target_length=5,
        max_revision_cycles=3,
    )


@pytest.fixture
def state_after_pitches(initial_state: SketchState) -> SketchState:
    """Create state after pitch session has completed."""
    return {
        **initial_state,
        "pitches": [
            {"id": "pitch_001", "agent": "Staff Writer A", "content": SAMPLE_PITCH_CONTENT},
            {"id": "pitch_002", "agent": "Staff Writer B", "content": "Another pitch..."},
            {"id": "pitch_003", "agent": "Senior Writer A", "content": "Senior pitch..."},
        ],
        "compiled_pitches": "Compiled pitch document...",
        "current_stage": "human_pitch_review",
    }


@pytest.fixture
def state_after_pitch_selection(state_after_pitches: SketchState) -> SketchState:
    """Create state after human has selected pitches."""
    return {
        **state_after_pitches,
        "human_selected_pitches": ["pitch_001"],
        "human_pitch_notes": "Love the tech support premise!",
        "showrunner_selected_pitch": SAMPLE_PITCH_CONTENT,
        "showrunner_vision_notes": "Focus on the medical drama escalation.",
        "current_stage": "story_breaking",
    }


@pytest.fixture
def state_after_beat_sheet(state_after_pitch_selection: SketchState) -> SketchState:
    """Create state after beat sheet has been created."""
    return {
        **state_after_pitch_selection,
        "character_details": {"content": "Character details..."},
        "joke_map": {"content": "Joke mapping..."},
        "structural_framework": {"content": "Structure..."},
        "beat_sheet": SAMPLE_BEAT_SHEET,
        "current_stage": "human_beat_review",
    }


@pytest.fixture
def state_approved_beat_sheet(state_after_beat_sheet: SketchState) -> SketchState:
    """Create state with approved beat sheet."""
    return {
        **state_after_beat_sheet,
        "human_beat_sheet_approval": True,
        "human_beat_sheet_notes": "Looks great!",
        "current_stage": "drafting",
    }


@pytest.fixture
def state_needs_revision(state_after_beat_sheet: SketchState) -> SketchState:
    """Create state where beat sheet needs revision."""
    return {
        **state_after_beat_sheet,
        "human_beat_sheet_approval": False,
        "human_beat_sheet_notes": "Need more escalation in act 2.",
    }


@pytest.fixture
def state_in_revision(state_approved_beat_sheet: SketchState) -> SketchState:
    """Create state during revision cycle."""
    return {
        **state_approved_beat_sheet,
        "first_draft": "First draft content...",
        "iteration_count": 1,
        "showrunner_revision_approved": False,
        "current_stage": "revision",
    }


@pytest.fixture
def state_max_revisions(state_in_revision: SketchState) -> SketchState:
    """Create state at max revision iterations."""
    return {
        **state_in_revision,
        "iteration_count": 3,  # Max
        "max_revision_cycles": 3,
    }


@pytest.fixture
def state_revision_approved(state_in_revision: SketchState) -> SketchState:
    """Create state with approved revision."""
    return {
        **state_in_revision,
        "showrunner_revision_approved": True,
        "revised_draft": "Revised draft content...",
    }


@pytest.fixture
def state_final_review(state_revision_approved: SketchState) -> SketchState:
    """Create state ready for final review."""
    return {
        **state_revision_approved,
        "formatted_script": "Formatted final script...",
        "qa_report": {"approved": True, "confidence_score": 8},
        "showrunner_final_review": "Approved for production.",
        "current_stage": "human_final_review",
    }


@pytest.fixture
def state_final_approved(state_final_review: SketchState) -> SketchState:
    """Create state with final approval."""
    return {
        **state_final_review,
        "human_final_approval": True,
        "human_final_notes": "Great work!",
        "final_script": "Final production script...",
    }


# =============================================================================
# UTILITY FIXTURES
# =============================================================================


@pytest.fixture
def patch_load_config(mock_config: Config):
    """Patch load_config to return mock config."""
    with patch("src.utils.config.load_config", return_value=mock_config):
        yield mock_config


@pytest.fixture
def patch_get_llm(mock_llm: MockLLMInterface):
    """Patch get_llm to return mock LLM."""
    with patch("src.utils.llm.get_llm", return_value=mock_llm):
        yield mock_llm


@pytest.fixture(autouse=True)
def reset_logging():
    """Reset logging configuration between tests."""
    import logging
    logging.getLogger().handlers = []
    yield
