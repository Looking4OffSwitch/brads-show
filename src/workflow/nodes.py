"""
Workflow node implementations for the sketch comedy writing system.

Each node is a function that processes state and returns updated state.
Nodes implement the 6-stage workflow plus human checkpoints.
"""

import asyncio
import logging
import uuid
from typing import Any

from src.agents import (
    AgentContext,
    HeadWriterAgent,
    QAAgent,
    ResearchAgent,
    ScriptCoordinatorAgent,
    SeniorWriterA,
    SeniorWriterB,
    ShowrunnerAgent,
    StaffWriterA,
    StaffWriterB,
    StoryEditorAgent,
)
from src.utils.config import Config, load_config
from src.utils.llm import LLMInterface, get_llm
from src.workflow.state import (
    SketchState,
    WorkflowStage,
    add_error,
    update_stage,
    update_token_usage,
)

logger = logging.getLogger(__name__)


def _get_config_and_llm(state: SketchState) -> tuple[Config, LLMInterface]:
    """
    Get or create config and LLM interface.

    Note: In production, these would be injected or cached.
    For now, we load fresh each time.
    """
    config = load_config()
    llm = get_llm(config)
    return config, llm


def _update_tokens_from_output(state: SketchState, output: Any) -> SketchState:
    """Update token usage from agent output if available."""
    if hasattr(output, "token_usage") and output.token_usage:
        return update_token_usage(
            state,
            output.token_usage.get("prompt_tokens", 0),
            output.token_usage.get("completion_tokens", 0),
        )
    return state


# =============================================================================
# STAGE 1: PITCH SESSION
# =============================================================================


async def pitch_session_node(state: SketchState) -> SketchState:
    """
    Stage 1: Parallel pitch generation.

    Executes 4 pitch agents in parallel:
    - Staff Writer A: 3 pitches (high volume, topical)
    - Staff Writer B: 3 pitches (structure-focused)
    - Senior Writer A: 2 pitches (premise/character)
    - Senior Writer B: 2 pitches (dialogue-driven)

    Then Research Agent validates and Head Writer compiles.
    """
    logger.info("=== STAGE 1: PITCH SESSION ===")
    state = update_stage(state, WorkflowStage.PITCH_SESSION)

    config, llm = _get_config_and_llm(state)

    # Create context for pitch generation
    context = AgentContext(
        show_bible=state["show_bible"],
        creative_prompt=state["creative_prompt"],
        task_type="generate_pitches",
    )

    # Initialize agents
    staff_a = StaffWriterA(config, llm)
    staff_b = StaffWriterB(config, llm)
    senior_a = SeniorWriterA(config, llm)
    senior_b = SeniorWriterB(config, llm)

    # Execute pitch generation in parallel
    logger.info("Generating pitches from 4 agents in parallel...")
    results = await asyncio.gather(
        staff_a.execute(context),
        staff_b.execute(context),
        senior_a.execute(context),
        senior_b.execute(context),
        return_exceptions=True,
    )

    # Collect pitches
    all_pitches = []
    for i, result in enumerate(results):
        agent_name = ["Staff Writer A", "Staff Writer B", "Senior Writer A", "Senior Writer B"][i]
        if isinstance(result, Exception):
            logger.error("Agent %s failed: %s", agent_name, result)
            state = add_error(state, str(result), f"pitch_session:{agent_name}")
        elif result.success:
            pitch_id = f"pitch_{uuid.uuid4().hex[:8]}"
            all_pitches.append({
                "id": pitch_id,
                "agent": agent_name,
                "content": result.content,
                "raw": True,  # Not yet parsed
            })
            state = _update_tokens_from_output(state, result)
            logger.info("Received pitches from %s", agent_name)
        else:
            logger.error("Agent %s failed: %s", agent_name, result.error_message)
            state = add_error(state, result.error_message or "Unknown error", f"pitch_session:{agent_name}")

    state["pitches"] = all_pitches

    # Research Agent validates pitches
    logger.info("Research Agent validating pitches...")
    research = ResearchAgent(config, llm)
    research_context = AgentContext(
        show_bible=state["show_bible"],
        creative_prompt=state["creative_prompt"],
        task_type="validate_pitches",
        previous_output="\n\n".join([p["content"] for p in all_pitches]),
    )
    research_result = await research.execute(research_context)
    if research_result.success:
        state["research_notes_pitches"] = {"content": research_result.content}
        state = _update_tokens_from_output(state, research_result)
    else:
        state = add_error(state, research_result.error_message or "Research failed", "pitch_session:research")

    # Head Writer compiles pitches
    logger.info("Head Writer compiling pitches...")
    head_writer = HeadWriterAgent(config, llm)
    compile_context = AgentContext(
        show_bible=state["show_bible"],
        creative_prompt=state["creative_prompt"],
        task_type="compile_pitches",
        previous_output="\n\n---\n\n".join([p["content"] for p in all_pitches]),
        additional_context={"research_notes": state.get("research_notes_pitches", {})},
    )
    compile_result = await head_writer.execute(compile_context)
    if compile_result.success:
        state["compiled_pitches"] = compile_result.content
        state = _update_tokens_from_output(state, compile_result)
    else:
        state = add_error(state, compile_result.error_message or "Compilation failed", "pitch_session:compile")

    logger.info("Pitch session complete. %d pitches generated.", len(all_pitches))
    return state


async def human_pitch_review_node(state: SketchState) -> SketchState:
    """
    Human Checkpoint #1: Review pitches.

    This node pauses for human input. The human reviews all pitches
    and selects 1-3 concepts to develop.

    Note: In actual execution, this node triggers an interrupt for human input.
    The human_selected_pitches and human_pitch_notes fields are populated
    externally before resuming.
    """
    logger.info("=== HUMAN CHECKPOINT #1: PITCH REVIEW ===")
    state = update_stage(state, WorkflowStage.HUMAN_PITCH_REVIEW)

    # This is a checkpoint - workflow pauses here
    # Human input is provided externally via state update
    logger.info(
        "Awaiting human review of %d pitches. Resume with pitch selection.",
        len(state.get("pitches", [])),
    )

    return state


async def showrunner_select_node(state: SketchState) -> SketchState:
    """
    Showrunner selects final pitch and provides creative direction.

    Takes human's selected pitches and makes final selection with
    detailed creative direction for development.
    """
    logger.info("=== SHOWRUNNER SELECTION ===")
    state = update_stage(state, WorkflowStage.SHOWRUNNER_SELECT)

    config, llm = _get_config_and_llm(state)

    # Get human selections
    selected_ids = state.get("human_selected_pitches", [])
    human_notes = state.get("human_pitch_notes", "")

    # Filter to selected pitches
    all_pitches = state.get("pitches", [])
    selected_content = [p["content"] for p in all_pitches if p["id"] in selected_ids]

    if not selected_content:
        # If no specific selection, use all pitches
        selected_content = [p["content"] for p in all_pitches]

    # Showrunner makes final selection
    showrunner = ShowrunnerAgent(config, llm)
    context = AgentContext(
        show_bible=state["show_bible"],
        creative_prompt=state["creative_prompt"],
        task_type="select_pitch",
        previous_output="\n\n---\n\n".join(selected_content),
        direction_notes=human_notes,
    )

    result = await showrunner.execute(context)
    if result.success:
        state["showrunner_selected_pitch"] = result.content
        state["showrunner_vision_notes"] = result.content  # Contains direction
        state = _update_tokens_from_output(state, result)
        logger.info("Showrunner selected pitch and provided direction")
    else:
        state = add_error(state, result.error_message or "Selection failed", "showrunner_select")

    return state


# =============================================================================
# STAGE 2: STORY BREAKING
# =============================================================================


async def story_breaking_node(state: SketchState) -> SketchState:
    """
    Stage 2: Collaborative beat sheet development.

    Multiple agents contribute:
    - Senior Writer A: Character details
    - Senior Writer B: Joke map
    - Staff Writer B: Structural framework
    - Research Agent: Supporting details
    - Story Editor: Validation
    - Head Writer: Synthesizes beat sheet
    """
    logger.info("=== STAGE 2: STORY BREAKING ===")
    state = update_stage(state, WorkflowStage.STORY_BREAKING)

    config, llm = _get_config_and_llm(state)

    selected_pitch = state.get("showrunner_selected_pitch", "")
    vision_notes = state.get("showrunner_vision_notes", "")

    # Parallel contributions from writers
    senior_a = SeniorWriterA(config, llm)
    senior_b = SeniorWriterB(config, llm)
    staff_b = StaffWriterB(config, llm)
    research = ResearchAgent(config, llm)

    base_context = {
        "show_bible": state["show_bible"],
        "creative_prompt": state["creative_prompt"],
        "previous_output": selected_pitch,
        "direction_notes": vision_notes,
    }

    # Execute contributions in parallel
    logger.info("Gathering story breaking contributions in parallel...")
    results = await asyncio.gather(
        senior_a.execute(AgentContext(**base_context, task_type="develop_characters")),
        senior_b.execute(AgentContext(**base_context, task_type="map_jokes")),
        staff_b.execute(AgentContext(**base_context, task_type="propose_structure")),
        research.execute(AgentContext(**base_context, task_type="provide_details")),
        return_exceptions=True,
    )

    # Process results
    agent_names = ["Senior Writer A", "Senior Writer B", "Staff Writer B", "Research"]
    field_names = ["character_details", "joke_map", "structural_framework", "research_details"]

    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error("%s failed: %s", agent_names[i], result)
            state = add_error(state, str(result), f"story_breaking:{agent_names[i]}")
        elif result.success:
            state[field_names[i]] = {"content": result.content}
            state = _update_tokens_from_output(state, result)
            logger.info("Received contribution from %s", agent_names[i])
        else:
            state = add_error(state, result.error_message or "Unknown error", f"story_breaking:{agent_names[i]}")

    # Story Editor validates
    logger.info("Story Editor validating structure...")
    story_editor = StoryEditorAgent(config, llm)
    validation_context = AgentContext(
        show_bible=state["show_bible"],
        creative_prompt=state["creative_prompt"],
        task_type="validate_beat_sheet",
        previous_output=f"""
Selected Pitch:
{selected_pitch}

Character Details:
{state.get('character_details', {}).get('content', 'N/A')}

Structural Framework:
{state.get('structural_framework', {}).get('content', 'N/A')}
""",
    )
    validation_result = await story_editor.execute(validation_context)
    if validation_result.success:
        state["story_editor_validation"] = {"content": validation_result.content}
        state = _update_tokens_from_output(state, validation_result)
    else:
        state = add_error(state, validation_result.error_message or "Validation failed", "story_breaking:validation")

    # Head Writer synthesizes beat sheet
    logger.info("Head Writer synthesizing beat sheet...")
    head_writer = HeadWriterAgent(config, llm)
    synthesis_context = AgentContext(
        show_bible=state["show_bible"],
        creative_prompt=state["creative_prompt"],
        task_type="synthesize_beat_sheet",
        previous_output=f"""
Selected Pitch:
{selected_pitch}

Showrunner Vision:
{vision_notes}

Character Details (Senior Writer A):
{state.get('character_details', {}).get('content', 'N/A')}

Joke Map (Senior Writer B):
{state.get('joke_map', {}).get('content', 'N/A')}

Structural Framework (Staff Writer B):
{state.get('structural_framework', {}).get('content', 'N/A')}

Research Details:
{state.get('research_details', {}).get('content', 'N/A')}

Story Editor Validation:
{state.get('story_editor_validation', {}).get('content', 'N/A')}
""",
    )
    synthesis_result = await head_writer.execute(synthesis_context)
    if synthesis_result.success:
        state["beat_sheet"] = synthesis_result.content
        state = _update_tokens_from_output(state, synthesis_result)
        logger.info("Beat sheet synthesized successfully")
    else:
        state = add_error(state, synthesis_result.error_message or "Synthesis failed", "story_breaking:synthesis")

    return state


async def human_beat_review_node(state: SketchState) -> SketchState:
    """
    Human Checkpoint #2: Review beat sheet.

    Human reviews the beat sheet and either approves or requests changes.
    """
    logger.info("=== HUMAN CHECKPOINT #2: BEAT SHEET REVIEW ===")
    state = update_stage(state, WorkflowStage.HUMAN_BEAT_REVIEW)

    logger.info("Awaiting human review of beat sheet. Resume with approval or notes.")
    return state


# =============================================================================
# STAGE 3: SCRIPT DRAFTING
# =============================================================================


async def drafting_node(state: SketchState) -> SketchState:
    """
    Stage 3: Script drafting.

    Head Writer assigns sections, Senior Writers draft, then assembled.
    """
    logger.info("=== STAGE 3: SCRIPT DRAFTING ===")
    state = update_stage(state, WorkflowStage.SCRIPT_DRAFTING)

    config, llm = _get_config_and_llm(state)

    beat_sheet = state.get("beat_sheet", "")
    vision_notes = state.get("showrunner_vision_notes", "")

    # Head Writer assigns sections
    logger.info("Head Writer assigning drafting sections...")
    head_writer = HeadWriterAgent(config, llm)
    assignment_context = AgentContext(
        show_bible=state["show_bible"],
        creative_prompt=state["creative_prompt"],
        task_type="assign_drafting",
        previous_output=beat_sheet,
        direction_notes=vision_notes,
    )
    assignment_result = await head_writer.execute(assignment_context)
    if assignment_result.success:
        state["section_assignments"] = {"content": assignment_result.content}
        state = _update_tokens_from_output(state, assignment_result)
    else:
        state = add_error(state, assignment_result.error_message or "Assignment failed", "drafting:assignment")

    # Senior Writers draft sections in parallel
    logger.info("Senior Writers drafting sections in parallel...")
    senior_a = SeniorWriterA(config, llm)
    senior_b = SeniorWriterB(config, llm)

    draft_context_base = {
        "show_bible": state["show_bible"],
        "creative_prompt": state["creative_prompt"],
        "direction_notes": f"""
Beat Sheet:
{beat_sheet}

Section Assignments:
{state.get('section_assignments', {}).get('content', 'N/A')}
""",
    }

    draft_results = await asyncio.gather(
        senior_a.execute(AgentContext(**draft_context_base, task_type="draft_section", previous_output="Draft opening and character-heavy sections")),
        senior_b.execute(AgentContext(**draft_context_base, task_type="draft_section", previous_output="Draft dialogue-intensive sections")),
        return_exceptions=True,
    )

    drafted_sections = []
    for i, result in enumerate(draft_results):
        agent = "Senior Writer A" if i == 0 else "Senior Writer B"
        if isinstance(result, Exception):
            state = add_error(state, str(result), f"drafting:{agent}")
        elif result.success:
            drafted_sections.append({"agent": agent, "content": result.content})
            state = _update_tokens_from_output(state, result)
        else:
            state = add_error(state, result.error_message or "Draft failed", f"drafting:{agent}")

    state["drafted_sections"] = drafted_sections

    # Head Writer assembles draft
    logger.info("Head Writer assembling first draft...")
    assemble_context = AgentContext(
        show_bible=state["show_bible"],
        creative_prompt=state["creative_prompt"],
        task_type="assemble_draft",
        previous_output="\n\n---\n\n".join([s["content"] for s in drafted_sections]),
        direction_notes=f"Beat Sheet:\n{beat_sheet}",
    )
    assemble_result = await head_writer.execute(assemble_context)
    if assemble_result.success:
        state["first_draft"] = assemble_result.content
        state = _update_tokens_from_output(state, assemble_result)
    else:
        state = add_error(state, assemble_result.error_message or "Assembly failed", "drafting:assembly")

    # Showrunner reviews draft
    logger.info("Showrunner reviewing first draft...")
    showrunner = ShowrunnerAgent(config, llm)
    review_context = AgentContext(
        show_bible=state["show_bible"],
        creative_prompt=state["creative_prompt"],
        task_type="review_draft",
        previous_output=state.get("first_draft", ""),
        direction_notes=f"Beat Sheet:\n{beat_sheet}",
    )
    review_result = await showrunner.execute(review_context)
    if review_result.success:
        state["showrunner_draft_notes"] = review_result.content
        state = _update_tokens_from_output(state, review_result)
    else:
        state = add_error(state, review_result.error_message or "Review failed", "drafting:showrunner_review")

    logger.info("First draft complete")
    return state


# =============================================================================
# STAGE 4: TABLE READ SIMULATION
# =============================================================================


async def table_read_node(state: SketchState) -> SketchState:
    """
    Stage 4: Table read simulation.

    All creative agents review the draft in parallel from their specialist perspectives.
    """
    logger.info("=== STAGE 4: TABLE READ SIMULATION ===")
    state = update_stage(state, WorkflowStage.TABLE_READ)

    config, llm = _get_config_and_llm(state)

    first_draft = state.get("first_draft", "")
    beat_sheet = state.get("beat_sheet", "")

    # Create review context
    review_context_base = {
        "show_bible": state["show_bible"],
        "creative_prompt": state["creative_prompt"],
        "previous_output": first_draft,
        "direction_notes": f"Beat Sheet:\n{beat_sheet}",
        "task_type": "table_read_review",
    }

    # Initialize all reviewing agents
    senior_a = SeniorWriterA(config, llm)
    senior_b = SeniorWriterB(config, llm)
    staff_a = StaffWriterA(config, llm)
    staff_b = StaffWriterB(config, llm)
    research = ResearchAgent(config, llm)
    story_editor = StoryEditorAgent(config, llm)

    # Execute reviews in parallel
    logger.info("Executing table read with 6 agents in parallel...")
    results = await asyncio.gather(
        senior_a.execute(AgentContext(**review_context_base)),
        senior_b.execute(AgentContext(**review_context_base)),
        staff_a.execute(AgentContext(**review_context_base)),
        staff_b.execute(AgentContext(**review_context_base)),
        research.execute(AgentContext(**review_context_base, task_type="fact_check")),
        return_exceptions=True,
    )

    # Collect feedback
    agent_names = ["Senior Writer A", "Senior Writer B", "Staff Writer A", "Staff Writer B", "Research"]
    focus_areas = ["Character", "Jokes", "Energy", "Structure", "Facts"]

    feedback_list = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            state = add_error(state, str(result), f"table_read:{agent_names[i]}")
        elif result.success:
            feedback_list.append({
                "agent": agent_names[i],
                "focus_area": focus_areas[i],
                "content": result.content,
            })
            state = _update_tokens_from_output(state, result)
        else:
            state = add_error(state, result.error_message or "Review failed", f"table_read:{agent_names[i]}")

    state["table_read_feedback"] = feedback_list

    # Story Editor compiles issues
    logger.info("Story Editor compiling feedback...")
    compile_context = AgentContext(
        show_bible=state["show_bible"],
        creative_prompt=state["creative_prompt"],
        task_type="compile_issues",
        previous_output=f"""
First Draft:
{first_draft}

Agent Feedback:
{chr(10).join([f"=== {f['agent']} ({f['focus_area']}) ==={chr(10)}{f['content']}" for f in feedback_list])}
""",
    )
    compile_result = await story_editor.execute(compile_context)
    if compile_result.success:
        state["story_editor_report"] = compile_result.content
        state = _update_tokens_from_output(state, compile_result)
    else:
        state = add_error(state, compile_result.error_message or "Compilation failed", "table_read:compile")

    # Head Writer creates revision plan
    logger.info("Head Writer creating revision plan...")
    head_writer = HeadWriterAgent(config, llm)
    plan_context = AgentContext(
        show_bible=state["show_bible"],
        creative_prompt=state["creative_prompt"],
        task_type="synthesize_feedback",
        previous_output=f"""
First Draft:
{first_draft}

Story Editor Report:
{state.get('story_editor_report', 'N/A')}

All Feedback:
{chr(10).join([f"=== {f['agent']} ==={chr(10)}{f['content']}" for f in feedback_list])}
""",
    )
    plan_result = await head_writer.execute(plan_context)
    if plan_result.success:
        state["revision_plan"] = plan_result.content
        state = _update_tokens_from_output(state, plan_result)
    else:
        state = add_error(state, plan_result.error_message or "Plan failed", "table_read:plan")

    logger.info("Table read complete")
    return state


# =============================================================================
# STAGE 5: REVISION CYCLES
# =============================================================================


async def revision_node(state: SketchState) -> SketchState:
    """
    Stage 5: Revision cycle.

    Writers fix issues identified in table read. May loop back.
    """
    logger.info("=== STAGE 5: REVISION CYCLE %d ===", state.get("iteration_count", 0) + 1)
    state = update_stage(state, WorkflowStage.REVISION)

    # Increment iteration counter
    state["iteration_count"] = state.get("iteration_count", 0) + 1

    config, llm = _get_config_and_llm(state)

    current_draft = state.get("revised_draft") or state.get("first_draft", "")
    revision_plan = state.get("revision_plan", "")
    beat_sheet = state.get("beat_sheet", "")

    # Senior Writers execute revisions in parallel
    senior_a = SeniorWriterA(config, llm)
    senior_b = SeniorWriterB(config, llm)

    revision_base = {
        "show_bible": state["show_bible"],
        "creative_prompt": state["creative_prompt"],
        "previous_output": current_draft,
        "direction_notes": f"Revision Plan:\n{revision_plan}\n\nBeat Sheet:\n{beat_sheet}",
    }

    logger.info("Executing revisions in parallel...")
    results = await asyncio.gather(
        senior_a.execute(AgentContext(**revision_base, task_type="fix_character_issues")),
        senior_b.execute(AgentContext(**revision_base, task_type="punch_up")),
        return_exceptions=True,
    )

    revised_sections = []
    for i, result in enumerate(results):
        agent = "Senior Writer A" if i == 0 else "Senior Writer B"
        if isinstance(result, Exception):
            state = add_error(state, str(result), f"revision:{agent}")
        elif result.success:
            revised_sections.append({"agent": agent, "content": result.content})
            state = _update_tokens_from_output(state, result)
        else:
            state = add_error(state, result.error_message or "Revision failed", f"revision:{agent}")

    state["revised_sections"] = revised_sections

    # Head Writer integrates revisions
    logger.info("Head Writer integrating revisions...")
    head_writer = HeadWriterAgent(config, llm)
    integrate_context = AgentContext(
        show_bible=state["show_bible"],
        creative_prompt=state["creative_prompt"],
        task_type="coordinate_revision",
        previous_output=f"""
Current Draft:
{current_draft}

Revisions:
{chr(10).join([f"=== {s['agent']} ==={chr(10)}{s['content']}" for s in revised_sections])}
""",
    )
    integrate_result = await head_writer.execute(integrate_context)
    if integrate_result.success:
        state["revised_draft"] = integrate_result.content
        state = _update_tokens_from_output(state, integrate_result)
    else:
        state = add_error(state, integrate_result.error_message or "Integration failed", "revision:integrate")

    # Showrunner reviews revision
    logger.info("Showrunner reviewing revision...")
    showrunner = ShowrunnerAgent(config, llm)
    review_context = AgentContext(
        show_bible=state["show_bible"],
        creative_prompt=state["creative_prompt"],
        task_type="review_draft",
        previous_output=state.get("revised_draft", ""),
    )
    review_result = await showrunner.execute(review_context)
    if review_result.success:
        # Check if approved (simplified - real implementation would parse response)
        state["showrunner_revision_approved"] = "approved" in review_result.content.lower() or "strong" in review_result.content.lower()
        state = _update_tokens_from_output(state, review_result)
    else:
        state = add_error(state, review_result.error_message or "Review failed", "revision:showrunner")

    logger.info("Revision cycle %d complete", state["iteration_count"])
    return state


# =============================================================================
# STAGE 6: POLISH & FINALIZE
# =============================================================================


async def polish_node(state: SketchState) -> SketchState:
    """
    Stage 6: Polish and finalize.

    Script Coordinator formats, QA validates, Showrunner gives final review.
    """
    logger.info("=== STAGE 6: POLISH & FINALIZE ===")
    state = update_stage(state, WorkflowStage.POLISH)

    config, llm = _get_config_and_llm(state)

    # Use revised draft or first draft
    draft = state.get("revised_draft") or state.get("first_draft", "")

    # Script Coordinator formats
    logger.info("Script Coordinator formatting script...")
    coordinator = ScriptCoordinatorAgent(config, llm)
    format_context = AgentContext(
        show_bible=state["show_bible"],
        creative_prompt=state["creative_prompt"],
        task_type="format_script",
        previous_output=draft,
    )
    format_result = await coordinator.execute(format_context)
    if format_result.success:
        state["formatted_script"] = format_result.content
        state = _update_tokens_from_output(state, format_result)
    else:
        state = add_error(state, format_result.error_message or "Formatting failed", "polish:format")

    # QA Agent validates
    logger.info("QA Agent performing final validation...")
    qa = QAAgent(config, llm)
    qa_context = AgentContext(
        show_bible=state["show_bible"],
        creative_prompt=state["creative_prompt"],
        task_type="final_validation",
        previous_output=state.get("formatted_script", ""),
        direction_notes=f"Beat Sheet:\n{state.get('beat_sheet', '')}",
    )
    qa_result = await qa.execute(qa_context)
    if qa_result.success:
        state["qa_report"] = {
            "content": qa_result.content,
            "approved": "approved" in qa_result.content.lower(),
        }
        state = _update_tokens_from_output(state, qa_result)
    else:
        state = add_error(state, qa_result.error_message or "QA failed", "polish:qa")

    # Showrunner final review
    logger.info("Showrunner performing final review...")
    showrunner = ShowrunnerAgent(config, llm)
    final_context = AgentContext(
        show_bible=state["show_bible"],
        creative_prompt=state["creative_prompt"],
        task_type="final_approval",
        previous_output=state.get("formatted_script", ""),
        additional_context={"qa_report": state.get("qa_report", {})},
    )
    final_result = await showrunner.execute(final_context)
    if final_result.success:
        state["showrunner_final_review"] = final_result.content
        state = _update_tokens_from_output(state, final_result)
    else:
        state = add_error(state, final_result.error_message or "Final review failed", "polish:final")

    logger.info("Polish complete")
    return state


async def human_final_review_node(state: SketchState) -> SketchState:
    """
    Human Checkpoint #3: Final script review.

    Human reviews formatted script and QA report, approves or requests changes.
    """
    logger.info("=== HUMAN CHECKPOINT #3: FINAL REVIEW ===")
    state = update_stage(state, WorkflowStage.HUMAN_FINAL_REVIEW)

    logger.info("Awaiting human review of final script. Resume with approval or revision request.")
    return state


# =============================================================================
# SYNCHRONOUS WRAPPERS
# =============================================================================


def pitch_session_node_sync(state: SketchState) -> SketchState:
    """Synchronous wrapper for pitch_session_node."""
    return asyncio.run(pitch_session_node(state))


def human_pitch_review_node_sync(state: SketchState) -> SketchState:
    """Synchronous wrapper for human_pitch_review_node."""
    return asyncio.run(human_pitch_review_node(state))


def showrunner_select_node_sync(state: SketchState) -> SketchState:
    """Synchronous wrapper for showrunner_select_node."""
    return asyncio.run(showrunner_select_node(state))


def story_breaking_node_sync(state: SketchState) -> SketchState:
    """Synchronous wrapper for story_breaking_node."""
    return asyncio.run(story_breaking_node(state))


def human_beat_review_node_sync(state: SketchState) -> SketchState:
    """Synchronous wrapper for human_beat_review_node."""
    return asyncio.run(human_beat_review_node(state))


def drafting_node_sync(state: SketchState) -> SketchState:
    """Synchronous wrapper for drafting_node."""
    return asyncio.run(drafting_node(state))


def table_read_node_sync(state: SketchState) -> SketchState:
    """Synchronous wrapper for table_read_node."""
    return asyncio.run(table_read_node(state))


def revision_node_sync(state: SketchState) -> SketchState:
    """Synchronous wrapper for revision_node."""
    return asyncio.run(revision_node(state))


def polish_node_sync(state: SketchState) -> SketchState:
    """Synchronous wrapper for polish_node."""
    return asyncio.run(polish_node(state))


def human_final_review_node_sync(state: SketchState) -> SketchState:
    """Synchronous wrapper for human_final_review_node."""
    return asyncio.run(human_final_review_node(state))
