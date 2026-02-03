#!/usr/bin/env python3
"""
Main entry point for the Sketch Comedy Writing System.

Usage:
    python run_sketch.py                        # Run full workflow
    python run_sketch.py --session "sketch_001" # Resume or name session
    python run_sketch.py --debug                # Enable debug logging
    python run_sketch.py --mock-checkpoints     # Auto-approve human checkpoints
    python run_sketch.py --stage pitch_session  # Run single stage only
    python run_sketch.py --help                 # Show help
"""

# === CRITICAL: Initialize tracing BEFORE any LangChain imports ===
# LangChain checks LANGCHAIN_TRACING_V2 on module import, so we must
# load environment variables and validate tracing config first.
import os

from dotenv import load_dotenv

load_dotenv()


def _init_langsmith_tracing() -> None:
    """Initialize LangSmith tracing from environment if enabled."""
    if os.getenv("LANGCHAIN_TRACING_V2", "").lower() == "true":
        if not os.getenv("LANGCHAIN_API_KEY"):
            print(
                "WARNING: LANGCHAIN_TRACING_V2=true but LANGCHAIN_API_KEY not set - tracing disabled"
            )
            os.environ["LANGCHAIN_TRACING_V2"] = "false"
        else:
            project = os.getenv("LANGCHAIN_PROJECT", "sketch-comedy-agents")
            print(f"LangSmith tracing enabled for project: {project}")


_init_langsmith_tracing()
# === End tracing initialization ===

import argparse
import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add project root to path so imports work when script is in src/
_project_root = Path(__file__).parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from src.cli.checkpoints import handle_checkpoint, mock_checkpoint
from src.cli.interface import (
    display_error,
    display_errors,
    display_header,
    display_info,
    display_stage,
    display_success,
    display_token_usage,
    display_warning,
    display_workflow_complete,
)
from src.utils.config import Config, ConfigurationError, load_config
from src.workflow.graph import compile_app, compile_app_no_interrupts
from src.workflow.state import SketchState, WorkflowStage, create_initial_state

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Sketch Comedy Multi-Agent Writing System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s                           Run complete workflow
    %(prog)s --session my_sketch       Name or resume a session
    %(prog)s --debug                   Enable debug logging
    %(prog)s --mock-checkpoints        Skip human reviews (for testing)
    %(prog)s --show another_show       Use different show folder
        """,
    )

    parser.add_argument(
        "--session",
        type=str,
        default=None,
        help="Session ID for the writing session (default: auto-generated)",
    )

    parser.add_argument(
        "--show",
        type=str,
        default=None,
        help="Show folder to use from Shows/ directory (overrides SHOW_FOLDER env)",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )

    parser.add_argument(
        "--mock-checkpoints",
        action="store_true",
        help="Auto-approve human checkpoints (for testing)",
    )

    parser.add_argument(
        "--stage",
        type=str,
        choices=[
            "pitch_session",
            "story_breaking",
            "drafting",
            "table_read",
            "revision",
            "polish",
        ],
        default=None,
        help="Run only a specific stage (for testing)",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate configuration without running workflow",
    )

    return parser.parse_args()


def setup_logging(debug: bool) -> None:
    """Configure logging based on debug flag."""
    level = logging.DEBUG if debug else logging.INFO
    logging.getLogger().setLevel(level)

    # Reduce noise from libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("anthropic").setLevel(logging.WARNING)


def save_output(
    state: SketchState,
    config: Config,
    session_id: str,
) -> str:
    """
    Save workflow outputs to files.

    Args:
        state: Final workflow state.
        config: System configuration.
        session_id: Session identifier.

    Returns:
        Path to main output file.
    """
    output_dir = config.show.output_dir
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save final script
    final_script = (
        state.get("final_script")
        or state.get("formatted_script")
        or state.get("revised_draft")
        or state.get("first_draft", "")
    )
    script_path = output_dir / f"{session_id}_{timestamp}_FINAL.txt"

    if final_script:
        script_path.write_text(final_script, encoding="utf-8")
        logger.info("Saved final script to: %s", script_path)

    # Save beat sheet
    beat_sheet = state.get("beat_sheet", "")
    if beat_sheet:
        beat_path = output_dir / f"{session_id}_{timestamp}_beat_sheet.txt"
        beat_path.write_text(beat_sheet, encoding="utf-8")
        logger.info("Saved beat sheet to: %s", beat_path)

    # Save QA report
    qa_report = state.get("qa_report", {})
    if qa_report:
        qa_path = output_dir / f"{session_id}_{timestamp}_QA_report.txt"
        qa_content = qa_report.get("content", str(qa_report))
        qa_path.write_text(qa_content, encoding="utf-8")
        logger.info("Saved QA report to: %s", qa_path)

    return str(script_path)


async def run_workflow(
    config: Config,
    session_id: str,
    mock_checkpoints: bool = False,
    single_stage: Optional[str] = None,
) -> SketchState:
    """
    Run the sketch writing workflow.

    Args:
        config: System configuration.
        session_id: Session identifier.
        mock_checkpoints: Whether to auto-approve checkpoints.
        single_stage: If set, run only this stage.

    Returns:
        Final workflow state.
    """
    display_header("SKETCH COMEDY WRITING SYSTEM")
    display_info(f"Session: {session_id}")
    display_info(f"Show: {config.show.show_folder}")

    # Create initial state
    initial_state = create_initial_state(
        show_bible=config.show.show_bible,
        creative_prompt=config.show.creative_prompt,
        session_id=session_id,
        target_length=config.workflow.target_sketch_length,
        max_revision_cycles=config.workflow.max_revision_cycles,
    )

    # Compile workflow
    if mock_checkpoints:
        display_warning("Mock checkpoints enabled - human reviews will be auto-approved")
        app = compile_app_no_interrupts()
    else:
        app = compile_app()

    # Create thread config for persistence
    thread_config = {"configurable": {"thread_id": session_id}}

    # Track stages for progress display
    stage_order = [
        ("pitch_session", "Pitch Session", 1),
        ("human_pitch_review", "Human Pitch Review", 1),
        ("showrunner_select", "Showrunner Selection", 1),
        ("story_breaking", "Story Breaking", 2),
        ("human_beat_review", "Human Beat Review", 2),
        ("drafting", "Script Drafting", 3),
        ("table_read", "Table Read", 4),
        ("revision", "Revision", 5),
        ("polish", "Polish & Finalize", 6),
        ("human_final_review", "Final Review", 6),
    ]

    current_state = initial_state

    if mock_checkpoints:
        # Run without interrupts
        display_stage("Running Full Workflow", 1, 6)
        logger.info("Starting workflow execution with mocked checkpoints...")

        # Stream through the workflow
        async for event in app.astream(initial_state, thread_config):
            # Log progress
            for node_name, node_output in event.items():
                if node_name == "__end__":
                    continue

                # Find stage info
                stage_info = next((s for s in stage_order if s[0] == node_name), None)
                if stage_info:
                    display_stage(stage_info[1], stage_info[2], 6)

                # Update state
                if isinstance(node_output, dict):
                    current_state = {**current_state, **node_output}

                    # Mock checkpoints
                    if node_name in [
                        "human_pitch_review",
                        "human_beat_review",
                        "human_final_review",
                    ]:
                        mock_updates = mock_checkpoint(current_state, node_name)
                        current_state = {**current_state, **mock_updates}

        logger.info("Workflow execution complete")

    else:
        # Run with interrupts for human checkpoints
        logger.info("Starting workflow with human checkpoints...")

        # Run until first interrupt
        async for event in app.astream(initial_state, thread_config):
            for node_name, node_output in event.items():
                if node_name == "__end__":
                    continue

                stage_info = next((s for s in stage_order if s[0] == node_name), None)
                if stage_info:
                    display_stage(stage_info[1], stage_info[2], 6)

                if isinstance(node_output, dict):
                    current_state = {**current_state, **node_output}

        # Handle checkpoints
        while True:
            # Get current state from checkpointer
            snapshot = app.get_state(thread_config)

            if not snapshot.next:
                # No more nodes to run
                break

            next_node = snapshot.next[0]

            # Check if this is a human checkpoint
            if next_node in ["human_pitch_review", "human_beat_review", "human_final_review"]:
                # Get current state
                current_state = snapshot.values

                # Handle the checkpoint
                updates = handle_checkpoint(current_state, next_node)

                # Update state
                app.update_state(thread_config, updates)

            # Continue execution
            async for event in app.astream(None, thread_config):
                for node_name, node_output in event.items():
                    if node_name == "__end__":
                        continue

                    stage_info = next((s for s in stage_order if s[0] == node_name), None)
                    if stage_info:
                        display_stage(stage_info[1], stage_info[2], 6)

                    if isinstance(node_output, dict):
                        current_state = {**current_state, **node_output}

        logger.info("Workflow complete")

    return current_state


def main() -> int:
    """Main entry point."""
    args = parse_args()

    # Setup logging
    setup_logging(args.debug)

    try:
        # Load configuration
        display_info("Loading configuration...")
        config = load_config(
            show_folder=args.show,
            debug=args.debug,
        )
        display_success(f"Configuration loaded for show: {config.show.show_folder}")

        # Dry run check
        if args.dry_run:
            display_success("Dry run successful - configuration is valid")
            return 0

        # Generate session ID
        session_id = args.session or f"sketch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Run workflow
        final_state = asyncio.run(
            run_workflow(
                config=config,
                session_id=session_id,
                mock_checkpoints=args.mock_checkpoints,
                single_stage=args.stage,
            )
        )

        # Display any errors
        errors = final_state.get("error_log", [])
        if errors:
            display_errors(errors)

        # Save outputs
        output_path = save_output(final_state, config, session_id)

        # Display completion
        token_usage = final_state.get("token_usage", {})
        display_workflow_complete(session_id, output_path, token_usage)

        return 0

    except ConfigurationError as e:
        display_error(f"Configuration error: {e}")
        logger.exception("Configuration error")
        return 1

    except KeyboardInterrupt:
        display_warning("Workflow interrupted by user")
        return 130

    except Exception as e:
        display_error(f"Unexpected error: {e}")
        logger.exception("Unexpected error during workflow execution")
        return 1


if __name__ == "__main__":
    sys.exit(main())
