# LangGraph Workflow Diagram
## Sketch Comedy Agent System Architecture

**Version:** 1.0  
**Framework:** LangGraph by LangChain  
**Last Updated:** February 2, 2026

---

## Visual Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         INITIALIZATION                                   │
│                                                                          │
│  [Load Configuration Files]                                             │
│   ├── show_bible.md                                                     │
│   ├── creative_prompt.md                                                │
│   └── agent_prompts.md                                                  │
│                            │                                             │
│                            ▼                                             │
│                    [Initialize State]                                    │
│                   (Shared Memory Store)                                  │
└─────────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      STAGE 1: PITCH SESSION                              │
│                     (Parallel Execution)                                 │
│                                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐│
│  │ Staff Writer │  │ Staff Writer │  │Senior Writer │  │Senior Writer ││
│  │      A       │  │      B       │  │      A       │  │      B       ││
│  │  (3 pitches) │  │  (3 pitches) │  │  (2 pitches) │  │  (2 pitches) ││
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘│
│         │                 │                 │                 │         │
│         └─────────────────┴─────────────────┴─────────────────┘         │
│                             │                                            │
│                             ▼                                            │
│                    [Research Agent]                                      │
│                  (Validates references)                                  │
│                             │                                            │
│                             ▼                                            │
│                    [Head Writer Agent]                                   │
│                  (Compiles all pitches)                                  │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                  HUMAN CHECKPOINT #1                                     │
│                                                                          │
│  [Human Reviews 8-12 Pitches]                                           │
│   ├── Selects 1-3 concepts to develop                                   │
│   └── Provides vision/direction notes                                   │
│                            │                                             │
│                            ▼                                             │
│                  [Showrunner Agent]                                      │
│             (Chooses final concept + vision)                             │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                STAGE 2: STORY BREAKING                                   │
│                  (Collaborative)                                         │
│                                                                          │
│                    [Head Writer Agent]                                   │
│                   (Facilitates session)                                  │
│                            │                                             │
│         ┌──────────────────┼──────────────────┐                         │
│         │                  │                  │                         │
│         ▼                  ▼                  ▼                         │
│  [Senior Writer A]  [Senior Writer B]  [Staff Writer B]                │
│   (Premise/Char)     (Jokes/Rhythm)     (Structure)                     │
│         │                  │                  │                         │
│         └──────────────────┼──────────────────┘                         │
│                            │                                             │
│         ┌──────────────────┴──────────────────┐                         │
│         │                                      │                         │
│         ▼                                      ▼                         │
│  [Story Editor Agent]                [Research Agent]                   │
│  (Validates structure)                (Provides details)                 │
│         │                                      │                         │
│         └──────────────────┬──────────────────┘                         │
│                            │                                             │
│                            ▼                                             │
│                    [Head Writer Agent]                                   │
│                 (Synthesizes beat sheet)                                 │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                  HUMAN CHECKPOINT #2                                     │
│                                                                          │
│  [Human Reviews Beat Sheet]                                             │
│   ├── Approves structure OR                                             │
│   └── Requests changes (loops back to Story Breaking)                   │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                STAGE 3: SCRIPT DRAFTING                                  │
│                  (Assigned Writing)                                      │
│                                                                          │
│                    [Head Writer Agent]                                   │
│                  (Assigns sections)                                      │
│                            │                                             │
│         ┌──────────────────┴──────────────────┐                         │
│         │                                      │                         │
│         ▼                                      ▼                         │
│  [Senior Writer A]                    [Senior Writer B]                 │
│  (Character sections)                 (Dialogue sections)                │
│         │                                      │                         │
│         └──────────────────┬──────────────────┘                         │
│                            │                                             │
│    ┌───────────────────────┼───────────────────────┐                    │
│    │                       │                       │                    │
│    ▼                       ▼                       ▼                    │
│ [Staff Writer B]    [Story Editor]         [Research Agent]            │
│ (Structure check)   (Continuity check)    (Detail requests)             │
│    │                       │                       │                    │
│    └───────────────────────┼───────────────────────┘                    │
│                            │                                             │
│                            ▼                                             │
│                    [Head Writer Agent]                                   │
│              (Assembles unified draft)                                   │
│                            │                                             │
│                            ▼                                             │
│                  [Showrunner Agent]                                      │
│              (Reviews, provides notes)                                   │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│            STAGE 4: TABLE READ SIMULATION                                │
│                  (Comprehensive Review)                                  │
│                                                                          │
│  All Creative Agents Review Draft in Parallel:                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐       │
│  │ Senior A   │  │ Senior B   │  │ Staff A    │  │ Staff B    │       │
│  │ (Character)│  │ (Jokes)    │  │ (Energy)   │  │ (Structure)│       │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘       │
│        │                │                │                │              │
│        └────────────────┴────────────────┴────────────────┘              │
│                            │                                             │
│         ┌──────────────────┴──────────────────┐                         │
│         │                                      │                         │
│         ▼                                      ▼                         │
│  [Story Editor Agent]                [Research Agent]                   │
│  (Compiles issues)                   (Validates facts)                   │
│         │                                      │                         │
│         └──────────────────┬──────────────────┘                         │
│                            │                                             │
│                            ▼                                             │
│                    [Head Writer Agent]                                   │
│              (Synthesizes revision plan)                                 │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│              STAGE 5: REVISION CYCLES                                    │
│                 (Iterative - May Loop)                                   │
│                                                                          │
│                    [Head Writer Agent]                                   │
│                  (Assigns revision tasks)                                │
│                            │                                             │
│         ┌──────────────────┼──────────────────┐                         │
│         │                  │                  │                         │
│         ▼                  ▼                  ▼                         │
│  [Senior Writer A]  [Senior Writer B]  [Staff Writer B]                │
│  (Character fixes)  (Punch-up/jokes)  (Structure fixes)                 │
│         │                  │                  │                         │
│         └──────────────────┼──────────────────┘                         │
│                            │                                             │
│                            ▼                                             │
│                   [Story Editor Agent]                                   │
│                  (Validates fixes work)                                  │
│                            │                                             │
│                            ▼                                             │
│                    [Head Writer Agent]                                   │
│                  (Integrates changes)                                    │
│                            │                                             │
│                            ▼                                             │
│                  [Showrunner Agent]                                      │
│                   (Reviews revision)                                     │
│                            │                                             │
│         ┌──────────────────┴──────────────────┐                         │
│         │                                      │                         │
│         ▼                                      ▼                         │
│  [Quality Sufficient]              [Needs More Work]                    │
│         │                                      │                         │
│         │                                      └─────────┐               │
│         │                                                │               │
└─────────┼────────────────────────────────────────────────┼───────────────┘
          │                                                │
          │                                       Loop back to Stage 4
          │                                      (Max 3 iterations)
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│            STAGE 6: POLISH & FINALIZE                                    │
│                                                                          │
│                 [Script Coordinator Agent]                               │
│              (Formats to industry standard)                              │
│                            │                                             │
│                            ▼                                             │
│              [Quality Assurance Agent]                                   │
│               (Final validation checklist)                               │
│                            │                                             │
│                            ▼                                             │
│                  [Showrunner Agent]                                      │
│                   (Final review)                                         │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                  HUMAN CHECKPOINT #3                                     │
│                                                                          │
│  [Human Reviews Final Script + QA Report]                               │
│   ├── APPROVES for production (DONE!) OR                                │
│   └── REQUESTS revision (loops back to Stage 5)                         │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                         [COMPLETE]
                    Production-Ready Script
```

---

## LangGraph Implementation Concepts

### 1. State Schema

```python
from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph

class SketchState(TypedDict):
    # Configuration
    show_bible: str
    creative_prompt: str
    
    # Stage 1: Pitch Session
    pitches: List[dict]  # All pitch concepts
    research_notes_pitches: dict
    compiled_pitches: str
    human_selected_pitches: List[str]
    showrunner_selected_pitch: str
    showrunner_vision_notes: str
    
    # Stage 2: Story Breaking
    character_details: dict
    joke_map: dict
    structural_framework: dict
    research_details: dict
    story_editor_validation: dict
    beat_sheet: str
    human_beat_sheet_approval: bool
    human_beat_sheet_notes: str
    
    # Stage 3: Drafting
    section_assignments: dict
    drafted_sections: List[str]
    first_draft: str
    showrunner_draft_notes: str
    
    # Stage 4: Table Read
    table_read_feedback: dict
    story_editor_report: str
    revision_plan: str
    
    # Stage 5: Revision
    revision_assignments: dict
    revised_sections: List[str]
    revised_draft: str
    iteration_count: int
    
    # Stage 6: Polish
    formatted_script: str
    qa_report: dict
    qa_approved: bool
    showrunner_final_review: str
    
    # Final
    human_final_approval: bool
    final_script: str
```

### 2. Node Definitions

```python
# Nodes are functions that process state and return updated state

def pitch_session_node(state: SketchState) -> SketchState:
    """Stage 1: Parallel pitch generation"""
    # Execute 4 agents in parallel
    # Update state with pitches
    # Return updated state
    pass

def human_pitch_review_node(state: SketchState) -> SketchState:
    """Human Checkpoint 1: Review pitches"""
    # Pause workflow
    # Display pitches to human
    # Collect human selection
    # Update state
    # Resume workflow
    pass

def story_breaking_node(state: SketchState) -> SketchState:
    """Stage 2: Collaborative beat sheet creation"""
    # Execute agents collaboratively
    # Synthesize beat sheet
    # Return updated state
    pass

# ... etc for all stages
```

### 3. Conditional Edges (Decision Points)

```python
def should_revise_beat_sheet(state: SketchState) -> str:
    """Decide if beat sheet needs revision"""
    if state["human_beat_sheet_approval"]:
        return "approved"  # Proceed to drafting
    else:
        return "needs_revision"  # Loop back to story breaking

def should_continue_revision(state: SketchState) -> str:
    """Decide if revision cycle continues"""
    if state["iteration_count"] >= 3:
        return "max_iterations"  # Force proceed
    elif state["showrunner_revision_approved"]:
        return "approved"  # Proceed to polish
    else:
        return "needs_more_revision"  # Loop back to table read
```

### 4. Graph Construction

```python
# Initialize graph
workflow = StateGraph(SketchState)

# Add nodes (stages)
workflow.add_node("pitch_session", pitch_session_node)
workflow.add_node("human_pitch_review", human_pitch_review_node)
workflow.add_node("showrunner_select", showrunner_select_node)
workflow.add_node("story_breaking", story_breaking_node)
workflow.add_node("human_beat_review", human_beat_review_node)
workflow.add_node("drafting", drafting_node)
workflow.add_node("table_read", table_read_node)
workflow.add_node("revision", revision_node)
workflow.add_node("polish", polish_node)
workflow.add_node("human_final_review", human_final_review_node)

# Add edges (flow)
workflow.add_edge("pitch_session", "human_pitch_review")
workflow.add_edge("human_pitch_review", "showrunner_select")
workflow.add_edge("showrunner_select", "story_breaking")
workflow.add_edge("story_breaking", "human_beat_review")

# Add conditional edges (decision points)
workflow.add_conditional_edges(
    "human_beat_review",
    should_revise_beat_sheet,
    {
        "approved": "drafting",
        "needs_revision": "story_breaking"
    }
)

workflow.add_edge("drafting", "table_read")
workflow.add_edge("table_read", "revision")

workflow.add_conditional_edges(
    "revision",
    should_continue_revision,
    {
        "approved": "polish",
        "needs_more_revision": "table_read",
        "max_iterations": "polish"
    }
)

workflow.add_edge("polish", "human_final_review")

workflow.add_conditional_edges(
    "human_final_review",
    lambda state: "approved" if state["human_final_approval"] else "needs_revision",
    {
        "approved": END,
        "needs_revision": "revision"
    }
)

# Set entry point
workflow.set_entry_point("pitch_session")

# Compile
app = workflow.compile()
```

### 5. Human-in-the-Loop Implementation

LangGraph provides built-in interrupt/resume for human checkpoints:

```python
from langgraph.checkpoint import MemorySaver

# Add checkpointer for persistence
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

# Execution with interrupts
config = {"configurable": {"thread_id": "sketch_001"}}

# Run until first interrupt (human checkpoint)
for event in app.stream(initial_state, config):
    print(event)
    
# Workflow pauses at human_pitch_review node
# Display pitches to human via UI
# Human provides feedback

# Resume with human input
human_feedback = {
    "human_selected_pitches": ["pitch_3"],
    "human_notes": "Love the tech support premise!"
}

# Update state and resume
app.update_state(config, human_feedback)

# Continue execution
for event in app.stream(None, config):
    print(event)
```

---

## Parallel Execution Patterns

### Stage 1: Pitch Session (4 agents in parallel)

```python
import asyncio

async def pitch_session_node(state: SketchState):
    """Execute 4 pitch agents in parallel"""
    
    # Create async tasks for each agent
    tasks = [
        generate_pitches(state, "staff_writer_a", count=3),
        generate_pitches(state, "staff_writer_b", count=3),
        generate_pitches(state, "senior_writer_a", count=2),
        generate_pitches(state, "senior_writer_b", count=2)
    ]
    
    # Execute in parallel
    results = await asyncio.gather(*tasks)
    
    # Combine results
    all_pitches = []
    for pitches in results:
        all_pitches.extend(pitches)
    
    # Research agent validates
    research_notes = await validate_pitches(all_pitches)
    
    # Head writer compiles
    compiled = await compile_pitches(all_pitches, research_notes)
    
    return {
        **state,
        "pitches": all_pitches,
        "research_notes_pitches": research_notes,
        "compiled_pitches": compiled
    }
```

### Stage 4: Table Read (All creative agents in parallel)

```python
async def table_read_node(state: SketchState):
    """All agents review draft in parallel"""
    
    draft = state["first_draft"]
    
    # Create review tasks for each agent
    tasks = [
        review_draft(draft, "senior_writer_a", focus="character"),
        review_draft(draft, "senior_writer_b", focus="jokes"),
        review_draft(draft, "staff_writer_a", focus="energy"),
        review_draft(draft, "staff_writer_b", focus="structure"),
        review_draft(draft, "research_agent", focus="facts")
    ]
    
    # Execute in parallel
    feedback = await asyncio.gather(*tasks)
    
    # Story editor compiles
    story_editor_report = await compile_feedback(feedback)
    
    # Head writer creates revision plan
    revision_plan = await create_revision_plan(feedback, story_editor_report)
    
    return {
        **state,
        "table_read_feedback": feedback,
        "story_editor_report": story_editor_report,
        "revision_plan": revision_plan
    }
```

---

## State Persistence

LangGraph's checkpointing enables:
- **Resume after crashes**: Workflow state persists
- **Human review points**: Pause/resume seamlessly
- **Debugging**: Inspect state at any point
- **Versioning**: Track state evolution

```python
# Save state to database
from langgraph.checkpoint.postgres import PostgresSaver

checkpointer = PostgresSaver.from_conn_string(
    "postgresql://user:pass@localhost/sketches"
)

app = workflow.compile(checkpointer=checkpointer)

# State automatically persists at each node
# Can resume from any point
```

---

## Error Handling & Retry Logic

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def call_agent_with_retry(agent_prompt: str):
    """Call LLM with automatic retry on failure"""
    try:
        response = await llm.ainvoke(agent_prompt)
        return response
    except Exception as e:
        print(f"Agent call failed: {e}")
        raise  # Will trigger retry

# Use in agent nodes
async def senior_writer_a_node(state: SketchState):
    prompt = build_prompt(state, "senior_writer_a")
    response = await call_agent_with_retry(prompt)
    return parse_response(response)
```

---

## Monitoring & Observability

LangGraph integrates with LangSmith for monitoring:

```python
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your_key"
os.environ["LANGCHAIN_PROJECT"] = "sketch-comedy-agents"

# Automatic tracing of all agent calls
# View in LangSmith dashboard:
# - Agent execution times
# - Token usage per agent
# - Success/failure rates
# - State transitions
# - Human checkpoint durations
```

---

## Configuration Files Integration

```python
def load_configuration():
    """Load show bible and creative prompt"""
    with open("show_bible.md", "r") as f:
        show_bible = f.read()
    
    with open("creative_prompt.md", "r") as f:
        creative_prompt = f.read()
    
    return {
        "show_bible": show_bible,
        "creative_prompt": creative_prompt
    }

# Initialize workflow with config
initial_state = {
    **load_configuration(),
    "iteration_count": 0,
    "pitches": [],
    # ... other initial values
}

# Run workflow
result = app.invoke(initial_state, config={"thread_id": "sketch_001"})
```

---

## Next Steps for Implementation

1. **Set up LangGraph environment** (see README.md)
2. **Implement core state schema** (as shown above)
3. **Create agent node functions** (using prompts from agent-prompts.md)
4. **Build graph structure** (add nodes, edges, conditionals)
5. **Implement human checkpoint UI** (web interface or CLI)
6. **Add monitoring** (LangSmith integration)
7. **Test with sample creative prompt**
8. **Iterate and refine prompts based on outputs**

---

**For detailed implementation instructions, see README.md**

---

**Document Version:** 1.0  
**Last Updated:** February 2, 2026  
**Framework:** LangGraph by LangChain  
**Estimated Implementation Time:** 4-8 weeks for full system
