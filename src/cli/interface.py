"""
Terminal interface functions for the sketch comedy writing system.

Provides display functions, progress indicators, and user interaction helpers.
"""

import logging
import sys
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger(__name__)

# ANSI color codes for terminal output
COLORS = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
}

# Check if terminal supports colors
SUPPORTS_COLOR = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def _color(text: str, color: str) -> str:
    """Apply color to text if terminal supports it."""
    if SUPPORTS_COLOR and color in COLORS:
        return f"{COLORS[color]}{text}{COLORS['reset']}"
    return text


def display_header(title: str, width: int = 60) -> None:
    """
    Display a formatted header.

    Args:
        title: Header title text.
        width: Width of header box.
    """
    border = "=" * width
    padding = (width - len(title) - 2) // 2
    padded_title = f" {' ' * padding}{title}{' ' * padding} "

    if len(padded_title) < width:
        padded_title += " "

    print()
    print(_color(border, "cyan"))
    print(_color(padded_title, "bold"))
    print(_color(border, "cyan"))
    print()


def display_subheader(title: str) -> None:
    """Display a subheader."""
    print()
    print(_color(f"--- {title} ---", "yellow"))
    print()


def display_stage(stage_name: str, stage_number: int, total_stages: int = 6) -> None:
    """
    Display current workflow stage.

    Args:
        stage_name: Name of the current stage.
        stage_number: Current stage number (1-based).
        total_stages: Total number of stages.
    """
    progress = f"[{stage_number}/{total_stages}]"
    print()
    print(_color(f"{progress} ", "dim") + _color(stage_name, "bold"))
    print(_color("-" * (len(progress) + len(stage_name) + 1), "dim"))


def display_progress(message: str, current: int, total: int) -> None:
    """
    Display progress indicator.

    Args:
        message: Progress message.
        current: Current item number.
        total: Total items.
    """
    percentage = (current / total) * 100 if total > 0 else 0
    bar_width = 30
    filled = int(bar_width * current / total) if total > 0 else 0
    bar = "█" * filled + "░" * (bar_width - filled)

    print(f"\r{message}: [{bar}] {percentage:.0f}% ({current}/{total})", end="")
    if current >= total:
        print()


def display_spinner(message: str, frame: int = 0) -> None:
    """
    Display a spinning progress indicator.

    Args:
        message: Message to display.
        frame: Current animation frame.
    """
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    spinner = frames[frame % len(frames)]
    print(f"\r{_color(spinner, 'cyan')} {message}", end="", flush=True)


def display_success(message: str) -> None:
    """Display success message."""
    print(_color("✓ ", "green") + message)


def display_error(message: str) -> None:
    """Display error message."""
    print(_color("✗ ", "red") + _color(message, "red"))


def display_warning(message: str) -> None:
    """Display warning message."""
    print(_color("⚠ ", "yellow") + message)


def display_info(message: str) -> None:
    """Display info message."""
    print(_color("ℹ ", "blue") + message)


def display_pitch(pitch: dict[str, Any], index: int) -> None:
    """
    Display a single pitch concept.

    Args:
        pitch: Pitch data dictionary.
        index: Pitch number for display.
    """
    print()
    print(_color(f"PITCH #{index}", "bold"))
    print(_color(f"From: {pitch.get('agent', 'Unknown')}", "dim"))
    print("-" * 40)
    print(pitch.get("content", "No content"))
    print()


def display_pitches(pitches: list[dict[str, Any]]) -> None:
    """
    Display all pitches for review.

    Args:
        pitches: List of pitch dictionaries.
    """
    display_subheader(f"PITCH CONCEPTS ({len(pitches)} total)")

    for i, pitch in enumerate(pitches, 1):
        display_pitch(pitch, i)


def display_beat_sheet(beat_sheet: str) -> None:
    """
    Display the beat sheet for review.

    Args:
        beat_sheet: Beat sheet content.
    """
    display_subheader("BEAT SHEET")
    print(beat_sheet)
    print()


def display_script(script: str, title: str = "SCRIPT") -> None:
    """
    Display a script draft.

    Args:
        script: Script content.
        title: Title for the display.
    """
    display_subheader(title)
    print(script)
    print()


def display_qa_report(report: dict[str, Any]) -> None:
    """
    Display QA report.

    Args:
        report: QA report dictionary.
    """
    display_subheader("QA REPORT")

    approved = report.get("approved", False)
    status = _color("APPROVED", "green") if approved else _color("NEEDS WORK", "red")
    print(f"Status: {status}")
    print()

    if "content" in report:
        print(report["content"])
    print()


def display_token_usage(usage: dict[str, int]) -> None:
    """
    Display token usage statistics.

    Args:
        usage: Token usage dictionary.
    """
    print()
    print(_color("Token Usage:", "dim"))
    print(f"  Prompt tokens:     {usage.get('prompt_tokens', 0):,}")
    print(f"  Completion tokens: {usage.get('completion_tokens', 0):,}")
    print(f"  Total tokens:      {usage.get('total_tokens', 0):,}")
    print()


def display_errors(errors: list[dict[str, Any]]) -> None:
    """
    Display error log.

    Args:
        errors: List of error dictionaries.
    """
    if not errors:
        return

    display_subheader(f"ERRORS ({len(errors)})")
    for error in errors:
        print(_color(f"[{error.get('stage', 'unknown')}]", "dim"), end=" ")
        print(_color(error.get("error", "Unknown error"), "red"))
        if error.get("context"):
            print(f"  Context: {error['context']}")
    print()


def prompt_user(message: str, default: Optional[str] = None) -> str:
    """
    Prompt user for input.

    Args:
        message: Prompt message.
        default: Default value if user presses Enter.

    Returns:
        User input or default.
    """
    if default:
        prompt = f"{message} [{default}]: "
    else:
        prompt = f"{message}: "

    response = input(_color(prompt, "cyan")).strip()

    if not response and default:
        return default
    return response


def prompt_yes_no(message: str, default: bool = True) -> bool:
    """
    Prompt user for yes/no confirmation.

    Args:
        message: Prompt message.
        default: Default value.

    Returns:
        True for yes, False for no.
    """
    default_str = "Y/n" if default else "y/N"
    response = input(_color(f"{message} [{default_str}]: ", "cyan")).strip().lower()

    if not response:
        return default
    return response in ("y", "yes", "true", "1")


def prompt_selection(
    message: str,
    options: list[str],
    allow_multiple: bool = False,
) -> list[int]:
    """
    Prompt user to select from options.

    Args:
        message: Prompt message.
        options: List of option strings.
        allow_multiple: Whether to allow multiple selections.

    Returns:
        List of selected indices (0-based).
    """
    print()
    print(_color(message, "bold"))
    print()

    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")

    print()

    if allow_multiple:
        hint = "Enter numbers separated by commas (e.g., 1,3)"
    else:
        hint = "Enter number"

    response = input(_color(f"{hint}: ", "cyan")).strip()

    try:
        if allow_multiple:
            indices = [int(x.strip()) - 1 for x in response.split(",")]
        else:
            indices = [int(response) - 1]

        # Validate indices
        valid = [i for i in indices if 0 <= i < len(options)]
        return valid

    except ValueError:
        display_warning("Invalid selection, returning first option")
        return [0]


def display_workflow_complete(
    session_id: str,
    output_path: str,
    token_usage: dict[str, int],
) -> None:
    """
    Display workflow completion message.

    Args:
        session_id: Session identifier.
        output_path: Path to output file.
        token_usage: Final token usage stats.
    """
    display_header("WORKFLOW COMPLETE")

    display_success(f"Session: {session_id}")
    display_success(f"Output saved to: {output_path}")

    display_token_usage(token_usage)

    print(_color("Thank you for using the Sketch Comedy Writing System!", "cyan"))
    print()


def clear_screen() -> None:
    """Clear the terminal screen."""
    print("\033[2J\033[H", end="")


def wait_for_keypress(message: str = "Press Enter to continue...") -> None:
    """Wait for user to press Enter."""
    input(_color(message, "dim"))
