"""
LangGraph workflow construction for the sketch comedy writing system.

Builds and compiles the complete 6-stage workflow graph with all nodes,
edges, and conditional routing.
"""

import logging
from typing import Optional

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from src.workflow.edges import (
    should_approve_final,
    should_continue_revision,
    should_revise_beat_sheet,
)
from src.workflow.nodes import (
    drafting_node,
    human_beat_review_node,
    human_final_review_node,
    human_pitch_review_node,
    pitch_session_node,
    polish_node,
    revision_node,
    showrunner_select_node,
    story_breaking_node,
    table_read_node,
)
from src.workflow.state import SketchState

logger = logging.getLogger(__name__)


def build_workflow_graph() -> StateGraph:
    """
    Build the complete workflow graph for sketch comedy writing.

    Creates a StateGraph with all nodes and edges representing the
    6-stage workflow:

    1. Pitch Session (parallel pitch generation)
    2. Story Breaking (collaborative beat sheet)
    3. Script Drafting (assigned section writing)
    4. Table Read (parallel review)
    5. Revision Cycles (iterative fixes)
    6. Polish & Finalize (formatting + QA)

    With 3 human checkpoints:
    - After pitch session (select pitch)
    - After story breaking (approve beat sheet)
    - After polish (approve final script)

    Returns:
        Configured StateGraph ready for compilation.
    """
    logger.info("Building workflow graph...")

    # Initialize graph with state schema
    workflow = StateGraph(SketchState)

    # ==========================================================================
    # ADD NODES
    # ==========================================================================

    # Stage 1: Pitch Session
    workflow.add_node("pitch_session", pitch_session_node)
    workflow.add_node("human_pitch_review", human_pitch_review_node)
    workflow.add_node("showrunner_select", showrunner_select_node)

    # Stage 2: Story Breaking
    workflow.add_node("story_breaking", story_breaking_node)
    workflow.add_node("human_beat_review", human_beat_review_node)

    # Stage 3: Script Drafting
    workflow.add_node("drafting", drafting_node)

    # Stage 4: Table Read
    workflow.add_node("table_read", table_read_node)

    # Stage 5: Revision
    workflow.add_node("revision", revision_node)

    # Stage 6: Polish
    workflow.add_node("polish", polish_node)
    workflow.add_node("human_final_review", human_final_review_node)

    logger.debug("Added 10 nodes to workflow graph")

    # ==========================================================================
    # ADD EDGES
    # ==========================================================================

    # Set entry point
    workflow.set_entry_point("pitch_session")

    # Stage 1 flow
    workflow.add_edge("pitch_session", "human_pitch_review")
    workflow.add_edge("human_pitch_review", "showrunner_select")
    workflow.add_edge("showrunner_select", "story_breaking")

    # Stage 2 flow with conditional
    workflow.add_edge("story_breaking", "human_beat_review")
    workflow.add_conditional_edges(
        "human_beat_review",
        should_revise_beat_sheet,
        {
            "approved": "drafting",
            "needs_revision": "story_breaking",
        },
    )

    # Stage 3 flow
    workflow.add_edge("drafting", "table_read")

    # Stage 4 flow
    workflow.add_edge("table_read", "revision")

    # Stage 5 flow with conditional
    workflow.add_conditional_edges(
        "revision",
        should_continue_revision,
        {
            "approved": "polish",
            "needs_more_revision": "table_read",
            "max_iterations": "polish",
        },
    )

    # Stage 6 flow with conditional
    workflow.add_edge("polish", "human_final_review")
    workflow.add_conditional_edges(
        "human_final_review",
        should_approve_final,
        {
            "approved": END,
            "needs_revision": "revision",
        },
    )

    logger.info("Workflow graph built successfully with 10 nodes and conditional edges")

    return workflow


def compile_app(
    checkpointer: Optional[MemorySaver] = None,
    interrupt_before: Optional[list[str]] = None,
    interrupt_after: Optional[list[str]] = None,
):
    """
    Compile the workflow graph into a runnable application.

    Args:
        checkpointer: Optional checkpointer for state persistence.
            If None, uses MemorySaver for development.
        interrupt_before: List of node names to interrupt before.
            Defaults to human checkpoint nodes.
        interrupt_after: List of node names to interrupt after.

    Returns:
        Compiled LangGraph application ready for execution.

    Example:
        >>> app = compile_app()
        >>> result = app.invoke(initial_state, config={"configurable": {"thread_id": "session_1"}})
    """
    logger.info("Compiling workflow application...")

    # Build the graph
    workflow = build_workflow_graph()

    # Set up checkpointer
    if checkpointer is None:
        checkpointer = MemorySaver()
        logger.debug("Using MemorySaver for state persistence")

    # Default interrupt points at human checkpoints
    if interrupt_before is None:
        interrupt_before = [
            "human_pitch_review",
            "human_beat_review",
            "human_final_review",
        ]

    # Compile with checkpointer and interrupts
    app = workflow.compile(
        checkpointer=checkpointer,
        interrupt_before=interrupt_before,
        interrupt_after=interrupt_after or [],
    )

    logger.info(
        "Workflow compiled with interrupts before: %s",
        interrupt_before,
    )

    return app


def compile_app_no_interrupts(checkpointer: Optional[MemorySaver] = None):
    """
    Compile workflow without human checkpoint interrupts.

    Useful for testing or automated runs where human input is mocked.

    Args:
        checkpointer: Optional checkpointer for state persistence.

    Returns:
        Compiled LangGraph application without interrupts.
    """
    logger.info("Compiling workflow without interrupts (for testing)...")

    workflow = build_workflow_graph()

    if checkpointer is None:
        checkpointer = MemorySaver()

    app = workflow.compile(
        checkpointer=checkpointer,
        interrupt_before=[],
        interrupt_after=[],
    )

    logger.info("Workflow compiled without interrupts")
    return app


def get_graph_visualization():
    """
    Get a text representation of the workflow graph for debugging.

    Returns:
        String representation of the graph structure.
    """
    workflow = build_workflow_graph()

    nodes = [
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

    edges = [
        ("pitch_session", "human_pitch_review"),
        ("human_pitch_review", "showrunner_select"),
        ("showrunner_select", "story_breaking"),
        ("story_breaking", "human_beat_review"),
        ("human_beat_review", "drafting [if approved]"),
        ("human_beat_review", "story_breaking [if needs revision]"),
        ("drafting", "table_read"),
        ("table_read", "revision"),
        ("revision", "polish [if approved/max]"),
        ("revision", "table_read [if needs more]"),
        ("polish", "human_final_review"),
        ("human_final_review", "END [if approved]"),
        ("human_final_review", "revision [if needs revision]"),
    ]

    viz = ["WORKFLOW GRAPH", "=" * 50, ""]
    viz.append("NODES:")
    for i, node in enumerate(nodes, 1):
        viz.append(f"  {i:2}. {node}")

    viz.append("")
    viz.append("EDGES:")
    for src, dst in edges:
        viz.append(f"  {src} -> {dst}")

    viz.append("")
    viz.append("HUMAN CHECKPOINTS:")
    viz.append("  1. human_pitch_review (select pitch to develop)")
    viz.append("  2. human_beat_review (approve beat sheet)")
    viz.append("  3. human_final_review (approve final script)")

    return "\n".join(viz)
