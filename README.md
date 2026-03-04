# Sketch Comedy LLM Agent System - README
## Complete Setup and Usage Guide

**Version:** 1.0  
**Last Updated:** February 2, 2026  
**Framework:** LangGraph by LangChain  
**Python Version:** 3.10+

---

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Prerequisites](#prerequisites)
4. [Installation & Setup](#installation--setup)
5. [Configuration Files](#configuration-files)
6. [Running the System](#running-the-system)
7. [Understanding the Workflow](#understanding-the-workflow)
8. [For Non-Technical Users](#for-non-technical-users)
9. [For Engineers](#for-engineers)
10. [Troubleshooting](#troubleshooting)
11. [Costs & Performance](#costs--performance)
12. [Roadmap](#roadmap)

---

## Overview

This system uses 10 specialized LLM agents that collaborate to write high-quality sketch comedy scripts from concept through final draft. It simulates a professional TV writers' room with roles like Showrunner, Head Writer, Senior Writers, Staff Writers, Story Editor, Research Agent, Script Coordinator, and Quality Assurance.

### Key Features

- ✅ **Quality-First**: Multiple revision cycles and collaborative refinement
- ✅ **Human-in-the-Loop**: 3 strategic checkpoints for creative control
- ✅ **Professional Output**: Industry-standard formatted scripts
- ✅ **Configurable**: Easy-to-edit markdown files for creative direction
- ✅ **Transparent**: See which agent did what at every stage
- ✅ **Resumable**: Workflow persists - can pause and resume anytime

### What You Get

**Input:**
- `show_bible.md` - Your show's creative guidelines
- `creative_prompt.md` - Your sketch idea/theme

**Output:**
- Production-ready sketch script (4-6 pages)
- Properly formatted for production
- QA report with quality assessment
- Full audit trail of agent contributions

---

## System Architecture

### The 10 Agents

#### Leadership Tier
1. **Showrunner Agent** - Final creative authority, maintains show vision
2. **Head Writer Agent** - Process manager, synthesizes all inputs

#### Creative Tier
3. **Senior Writer Agent A** - Premise & character specialist
4. **Senior Writer Agent B** - Dialogue & punch-up specialist
5. **Staff Writer Agent A** - High-volume pitch generator
6. **Staff Writer Agent B** - Structure & callback specialist

#### Support Tier
7. **Story Editor Agent** - Continuity & quality control
8. **Research Agent** - Facts, references, cultural context

#### QA Tier
9. **Script Coordinator Agent** - Formatting & technical standards
10. **Quality Assurance Agent** - Final validation gatekeeper

### The 6 Workflow Stages

1. **Pitch Session** - Generate 8-12 diverse concepts (parallel)
2. **Story Breaking** - Develop chosen concept into beat sheet
3. **Script Drafting** - Write complete first draft
4. **Table Read Simulation** - All agents review and provide feedback
5. **Revision Cycles** - Execute improvements (iterative, up to 3x)
6. **Polish & Finalize** - Format and validate for production

### The 3 Human Checkpoints

- **After Stage 1**: Review pitches, select concept to develop
- **After Stage 2**: Approve beat sheet structure
- **After Stage 6**: Final approval or request revision

---

## Prerequisites

### Required Software

- **Python 3.10+** ([Download](https://www.python.org/downloads/))
- **Git** ([Download](https://git-scm.com/downloads))
- **Text Editor** (VS Code, Sublime, Atom, or any markdown editor)

### Required API Keys

You'll need access to LLM providers. Recommended setup:

- **OpenAI API Key** (GPT-4 for creative leads, GPT-3.5 for support roles)
  - Get key: https://platform.openai.com/api-keys
  - Or **Anthropic API Key** (Claude 3.5 Sonnet alternative)
  - Get key: https://console.anthropic.com/

### Recommended Hardware

- **Minimum**: 8GB RAM, modern processor
- **Recommended**: 16GB RAM, multi-core processor
- **Internet**: Stable connection for API calls

---

## Installation & Setup

### Step 1: Clone or Download Repository

```bash
# If using git
git clone https://github.com/yourusername/sketch-comedy-agents.git
cd sketch-comedy-agents

# Or download and extract ZIP, then navigate to folder
cd sketch-comedy-agents
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
# Install required packages
pip install --upgrade pip
pip install langgraph langchain langchain-openai
pip install python-dotenv tenacity pydantic

# For monitoring (optional)
pip install langsmith

# For development (optional)
pip install jupyter black pytest
```

### Step 4: Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Copy template
cp .env.example .env

# Edit with your API keys
nano .env  # or use your preferred editor
```

Add your API keys to `.env`:

```
# OpenAI Configuration
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL_CREATIVE=gpt-4  # For creative agents
OPENAI_MODEL_SUPPORT=gpt-3.5-turbo  # For support agents

# Alternative: Anthropic Configuration
# ANTHROPIC_API_KEY=sk-ant-your-key-here
# ANTHROPIC_MODEL_CREATIVE=claude-3-5-sonnet-20241022

# LangSmith Monitoring (Optional)
# LANGCHAIN_TRACING_V2=true
# LANGCHAIN_API_KEY=ls-your-key-here
# LANGCHAIN_PROJECT=sketch-comedy-agents

# Project Configuration
SHOW_NAME="My Sketch Show"
MAX_REVISION_CYCLES=3
TARGET_SKETCH_LENGTH=5  # pages
```

### Step 5: Verify Installation

```bash
# Run verification script
python verify_setup.py

# Should output:
# ✅ Python version: 3.10.x
# ✅ Virtual environment: Active
# ✅ LangGraph installed: X.X.X
# ✅ API keys configured: OpenAI
# ✅ Configuration files found: 3/3
# ✅ System ready!
```

---

## Configuration Files

### Three Files You'll Edit

#### 1. `show_bible.md` - Your Show's Creative DNA

**Purpose:** Defines your show's tone, style, content guidelines, and quality standards.

**Edit this once**, then update as you learn what works.

**Key Sections:**
- Show identity and audience
- Comedy styles you embrace/avoid
- Content guidelines and boundaries
- Reference sketches you love
- Success indicators

**Location:** Project root  
**Who Edits:** Non-technical partner (creative director)  
**When to Edit:** Once at setup, then quarterly reviews

**Example:**
```markdown
## Show Identity
We create smart, character-driven sketch comedy...

## Comedy Styles We Embrace
1. **Character Commitment Comedy**
   Description: Characters fully believe in absurd perspectives
   Example: Wedding planner insisting every wedding needs "battle royale"
```

#### 2. `creative_prompt.md` - Your Sketch Starting Point

**Purpose:** The creative prompt for each new sketch session.

**Edit this every time** you want to generate a new sketch.

**Key Sections:**
- Theme/inspiration (what's the sketch about?)
- Specific requirements (must-include elements)
- Character types
- Tone and setting
- What you hope for

**Location:** Project root  
**Who Edits:** Non-technical partner (writer/creative)  
**When to Edit:** Every new sketch session

**Example:**
```markdown
## Theme / Inspiration
A tech support agent who treats basic computer problems like 
life-saving surgery, complete with dramatic countdowns...

## Specific Requirements
- Must include "have you tried turning it off and on again?" delivered dramatically
- Tech support agent asks customer to "scrub in"
- Computer referred to as "the patient"
```

#### 3. `feedback_template.md` - How You Provide Feedback

**Purpose:** Structured format for providing feedback at human checkpoints.

**Edit this at human checkpoints** during workflow.

**Key Sections:**
- Decision (approve / request changes / select option)
- What's working
- What needs improvement (with priority)
- Questions/concerns

**Location:** `feedback/` folder  
**Who Edits:** Non-technical partner (reviewer)  
**When to Edit:** At each of 3 human checkpoints

**Example:**
```markdown
## Checkpoint: Pitch Review

**Decision:** Select Option

**Selected:** Pitch #3 (Tech Support ER)

**Notes:**
- Love the medical drama energy
- Make sure we don't mock actual tech support workers
- Want at least one moment where "patient" (computer) "flatlines"
```

---

## Running the System

### Quick Start (CLI)

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Run the system
python run_sketch.py

# Override model for all agents (by default, creative agents use Sonnet and support agents use Haiku)
python run_sketch.py --model claude-sonnet-4-6
python run_sketch.py --model claude-opus-4-6      # highest quality

# Follow prompts:
# 1. System loads show_bible.md and creative_prompt.md
# 2. Stage 1 executes (pitch generation)
# 3. You review pitches in terminal
# 4. Select concept, workflow continues
# 5. Review beat sheet when prompted
# 6. Review final script when complete
```

### Detailed Workflow

#### Step 1: Prepare Your Creative Prompt

```bash
# Edit your creative prompt
nano creative_prompt.md

# Or open in your preferred editor
code creative_prompt.md
```

Fill in what you want the sketch to be about.

#### Step 2: Start the Workflow

```bash
python run_sketch.py --session "sketch_001"

# Output:
# ✅ Loaded show bible: "My Sketch Show"
# ✅ Loaded creative prompt: "Tech Support ER"
# ✅ Initializing 10 agents...
# ✅ Starting Stage 1: Pitch Session
#
# 🔄 Staff Writer A: Generating 3 pitches...
# 🔄 Staff Writer B: Generating 3 pitches...
# 🔄 Senior Writer A: Generating 2 pitches...
# 🔄 Senior Writer B: Generating 2 pitches...
# ✅ All pitches generated
# 🔄 Research Agent: Validating references...
# ✅ Research validation complete
# 🔄 Head Writer: Compiling pitches...
# ✅ Compilation complete
#
# ⏸️  HUMAN CHECKPOINT #1: PITCH REVIEW
```

#### Step 3: Human Checkpoint #1 - Review Pitches

The system will display all pitches and pause:

```
═══════════════════════════════════════════════════════
  HUMAN CHECKPOINT #1: PITCH REVIEW
═══════════════════════════════════════════════════════

Total Pitches: 10

─────────────────────────────────────────────────────
PITCH #1: "Artisanal Water Sommelier"
From: Staff Writer A

Logline: A pretentious water sommelier at an upscale 
restaurant describes the "terroir" and "vintage" of tap 
water, getting increasingly absurd...

The Game: Each water description gets more absurdly 
specific and less appetizing...

Research Notes: ✅ Water sommeliers are real 
(validated reference)
─────────────────────────────────────────────────────

[... 9 more pitches ...]

─────────────────────────────────────────────────────
YOUR TURN: Which pitch(es) do you want to develop?

Enter pitch number(s): 3
Add notes (optional): Love this premise, emphasize 
the medical drama commitment

Confirming selection...
```

System resumes, passes to Showrunner Agent for final selection.

#### Step 4: Story Breaking (Automatic)

```
✅ Showrunner selected: Pitch #3 "Tech Support ER"
✅ Showrunner vision: "Full commitment to medical drama..."

🔄 Starting Stage 2: Story Breaking...
🔄 Senior Writer A: Developing characters...
🔄 Senior Writer B: Mapping joke opportunities...
🔄 Staff Writer B: Proposing structure...
🔄 Story Editor: Validating structure...
🔄 Research Agent: Gathering details...
🔄 Head Writer: Synthesizing beat sheet...
✅ Beat sheet complete

⏸️  HUMAN CHECKPOINT #2: BEAT SHEET REVIEW
```

#### Step 5: Human Checkpoint #2 - Review Beat Sheet

```
═══════════════════════════════════════════════════════
  HUMAN CHECKPOINT #2: BEAT SHEET REVIEW
═══════════════════════════════════════════════════════

BEAT SHEET: "Tech Support ER"

Premise: Tech support agent treats basic computer 
problem like life-saving surgery...

The Game: Each troubleshooting step treated with 
increasing medical drama...

BEAT 1: OPEN (Page 1)
Customer calls with printer problem. Agent answers 
like surgeon entering OR...

[... full beat sheet displayed ...]

─────────────────────────────────────────────────────
YOUR TURN: Approve this structure?

[A]pprove  [R]equest Changes: A
```

If you approve, workflow continues to drafting. If you request changes, system loops back to story breaking with your notes.

#### Step 6: Drafting, Table Read, Revision (Automatic)

```
✅ Beat sheet approved

🔄 Starting Stage 3: Script Drafting...
🔄 Head Writer: Assigning sections...
🔄 Senior Writer A: Drafting character sections...
🔄 Senior Writer B: Drafting dialogue sections...
🔄 Head Writer: Assembling draft...
✅ First draft complete (5 pages)

🔄 Showrunner: Reviewing draft...
✅ Showrunner notes: "Strengthen ending, add one more medical callback"

🔄 Starting Stage 4: Table Read Simulation...
🔄 All agents reviewing in parallel...
✅ Feedback compiled

🔄 Head Writer: Creating revision plan...
✅ Revision plan ready

🔄 Starting Stage 5: Revision Cycle #1...
🔄 Senior Writer B: Executing punch-up...
🔄 Staff Writer B: Adding callback...
🔄 Story Editor: Validating fixes...
🔄 Head Writer: Integrating changes...
✅ Revision complete

🔄 Showrunner: Reviewing revision...
✅ Showrunner: Quality sufficient, proceeding to polish

🔄 Starting Stage 6: Polish & Finalize...
🔄 Script Coordinator: Formatting script...
🔄 QA Agent: Final validation...
✅ QA Report: 28/30 checklist items passed
✅ QA Decision: APPROVED FOR HUMAN REVIEW

🔄 Showrunner: Final review...
✅ Showrunner: APPROVED for human review

⏸️  HUMAN CHECKPOINT #3: FINAL APPROVAL
```

#### Step 7: Human Checkpoint #3 - Final Approval

```
═══════════════════════════════════════════════════════
  HUMAN CHECKPOINT #3: FINAL APPROVAL
═══════════════════════════════════════════════════════

✅ Script formatted and validated
✅ QA Score: 28/30 (93%)

[Full formatted script displayed here]

─────────────────────────────────────────────────────
QA REPORT SUMMARY

Strengths:
- Clear game with strong escalation
- High joke density (3.2 laughs/page)
- Excellent character commitment
- Perfect length (5 pages)

Minor Notes:
- One callback could be stronger (page 4)
- Optional: Add one more physical comedy beat

Overall: Production-ready
─────────────────────────────────────────────────────

YOUR TURN: Final decision?

[A]pprove for Production  [R]equest Revision: A

✅ APPROVED! Script saved to: output/script.txt
```

#### Step 8: Get Your Script

```
═══════════════════════════════════════════════════════
  SKETCH COMPLETE!
═══════════════════════════════════════════════════════

Final script saved to:
  📄 output/script.txt (production script)
  📄 output/beat_sheet.txt (reference)
  📄 output/qa_report.txt (quality assessment)

Stats:
  Total time: 47 minutes
  Revision cycles: 1
  Final length: 5 pages
  QA score: 93%
  Joke density: 3.2 laughs/page

Agent contributions:
  Senior Writer B: 47 interventions (most active)
  Senior Writer A: 32 interventions
  Staff Writer B: 28 interventions
  [... full breakdown ...]

✅ Ready for production!
```

---

## Understanding the Workflow

### Stage-by-Stage Breakdown

#### Stage 1: Pitch Session (5-10 minutes)

**What Happens:**
- 4 writer agents generate pitches in parallel
- Staff Writer A: 3 high-energy, topical pitches
- Staff Writer B: 3 structure-focused pitches
- Senior Writer A: 2 premise-driven pitches
- Senior Writer B: 2 dialogue-led pitches
- Research Agent validates topical references
- Head Writer compiles all pitches

**What You Do:**
- Review 8-12 pitch concepts
- Select 1-3 you like
- Provide optional notes/direction
- Showrunner Agent makes final selection

**Output:** 1 selected pitch + creative direction notes

---

#### Stage 2: Story Breaking (10-15 minutes)

**What Happens:**
- Senior Writer A develops characters and premise game
- Senior Writer B maps joke opportunities and rhythm
- Staff Writer B proposes structural framework
- Story Editor validates structure
- Research Agent provides enriching details
- Head Writer synthesizes comprehensive beat sheet

**What You Do:**
- Review beat sheet (structure outline)
- Approve OR request changes
- If changes: provide specific notes, system loops back

**Output:** Approved beat sheet (detailed scene-by-scene breakdown)

---

#### Stage 3: Script Drafting (15-20 minutes)

**What Happens:**
- Head Writer assigns sections to Senior Writers
- Senior Writer A drafts character-heavy sections
- Senior Writer B drafts dialogue-intensive sections
- Staff Writer B monitors structural integrity
- Story Editor tracks continuity
- Research Agent provides on-demand details
- Head Writer assembles unified first draft
- Showrunner Agent reviews and provides high-level notes

**What You Do:**
- Nothing - this stage is automatic
- Optional: Can peek at progress if curious

**Output:** Complete first draft + Showrunner notes

---

#### Stage 4: Table Read Simulation (10-15 minutes)

**What Happens:**
- All 4 writer agents review draft in parallel
  - Senior Writer A: Character consistency feedback
  - Senior Writer B: Joke density and punch-up notes
  - Staff Writer A: Energy and topical freshness
  - Staff Writer B: Structure and callback effectiveness
- Story Editor compiles all continuity/logic issues
- Research Agent validates all facts and references
- Head Writer synthesizes comprehensive revision plan

**What You Do:**
- Nothing - this stage is automatic
- System determines what needs fixing

**Output:** Revision plan with prioritized tasks

---

#### Stage 5: Revision Cycles (10-20 minutes per cycle)

**What Happens:**
- Head Writer assigns revision tasks to appropriate agents
- Senior Writer A fixes character issues
- Senior Writer B executes punch-up improvements
- Staff Writer B fixes structural problems
- Story Editor validates fixes don't create new issues
- Head Writer integrates all changes
- Showrunner Agent reviews revised draft
- **Decision:** Quality sufficient? → Proceed. Needs more? → Loop (max 3x)

**What You Do:**
- Nothing - revision cycles are automatic
- System iterates until quality threshold met

**Output:** Polished draft meeting quality standards

---

#### Stage 6: Polish & Finalize (5-10 minutes)

**What Happens:**
- Script Coordinator formats to industry standard
- QA Agent performs comprehensive validation
- Showrunner Agent conducts final review
- System generates QA report

**What You Do:**
- Review final formatted script
- Review QA report
- APPROVE for production OR request revision
- If revision: provide notes, returns to Stage 5

**Output:** Production-ready formatted script + QA report

---

### Typical Timeline

| Stage | Duration | Human Time | Agent Time |
|-------|----------|------------|------------|
| Stage 1: Pitch | 5-10 min | 2-3 min review | 7-8 min generation |
| Stage 2: Breaking | 10-15 min | 3-5 min review | 10 min collaboration |
| Stage 3: Drafting | 15-20 min | 0 min | 15-20 min writing |
| Stage 4: Table Read | 10-15 min | 0 min | 10-15 min review |
| Stage 5: Revision | 10-20 min | 0 min | 10-20 min fixes |
| Stage 6: Polish | 5-10 min | 3-5 min review | 5 min formatting |
| **Total** | **55-90 min** | **8-13 min** | **47-78 min** |

**Your actual time:** 8-13 minutes of review across 3 checkpoints  
**Agent work time:** 47-78 minutes of automated processing

---

## For Non-Technical Users

### Your Workflow (Simple Version)

#### Before You Start
1. Open `show_bible.md` in any text editor
2. Fill in your show's creative guidelines
3. Save it (this becomes your show's creative DNA)

#### Each Time You Want a New Sketch
1. Open `creative_prompt.md` in text editor
2. Write what you want the sketch to be about
3. Save it
4. Run the system (ask your engineer partner for command)
5. Wait for Checkpoint #1 → Review pitches → Select one
6. Wait for Checkpoint #2 → Review beat sheet → Approve or request changes
7. Wait for Checkpoint #3 → Review final script → Approve or request revision
8. Done! You have a production-ready sketch script

### The Three Files You Edit

**File 1: `show_bible.md`**
- **What:** Your show's style guide
- **Edit when:** Once at setup, then quarterly
- **What to write:** Comedy styles you like, topics you love/avoid, quality standards

**File 2: `creative_prompt.md`**
- **What:** Your sketch idea for this session
- **Edit when:** Every new sketch
- **What to write:** Theme, must-include elements, character types, tone

**File 3: `feedback_template.md`**
- **What:** Your feedback at checkpoints
- **Edit when:** At each checkpoint during workflow
- **What to write:** What you like, what needs fixing, your decision

### Tips for Success

#### Writing Good Creative Prompts
- **Be specific about the core idea**: "Wedding planner who insists all weddings need battle royale" not just "wedding sketch"
- **Include must-have elements**: List 2-3 specific things you want to see
- **Describe the energy**: "Grounded then absurd" or "High-energy throughout"
- **Share inspiration**: "Like that SNL sketch where..." helps agents understand

#### Giving Good Feedback at Checkpoints
- **Be specific**: "The ending feels weak" not "I don't like it"
- **Prioritize**: Mark which notes are critical vs. nice-to-have
- **Explain why**: "This doesn't match our show tone because..."
- **Suggest solutions**: "Maybe try having the character..." not just "fix this"

#### When to Approve vs. Request Changes

**Approve the beat sheet if:**
- The structure makes sense (clear beginning, middle, end)
- The "game" (repeating pattern) is clear
- You can imagine it being funny
- Minor tweaks can happen during drafting

**Request changes if:**
- The structure is confusing
- The "game" isn't clear
- Major elements are missing
- It doesn't match your vision

**Approve the final script if:**
- It makes you laugh (or would make your audience laugh)
- QA score is 80%+ (24/30 checklist items)
- Any remaining issues are minor polish

**Request revision if:**
- It's not funny enough (low joke density)
- Major problems in QA report
- Doesn't match show tone
- Ending is weak

### Don't Worry About

- ❌ Technical stuff (API keys, Python, code)
- ❌ How agents communicate with each other
- ❌ The workflow internals
- ❌ File paths and terminal commands

Your engineer partner handles all technical aspects. You focus on creative direction.

---

## For Engineers

### Project Structure

```
sketch-comedy-agents/
├── README.md                    # This file
├── .env                         # Environment variables (API keys)
├── .env.example                 # Template for .env
├── requirements.txt             # Python dependencies
├── verify_setup.py              # Installation verification script
│
├── config/
│   ├── show_bible.md            # Show creative guidelines (user edits)
│   ├── creative_prompt.md       # Sketch prompt (user edits per session)
│   └── feedback_template.md     # Feedback format (user edits at checkpoints)
│
├── prompts/
│   └── agent_prompts.md         # All 10 agent prompts with variations
│
├── src/
│   ├── __init__.py
│   ├── agents/                  # Agent implementations
│   │   ├── __init__.py
│   │   ├── showrunner.py
│   │   ├── head_writer.py
│   │   ├── senior_writer_a.py
│   │   ├── senior_writer_b.py
│   │   ├── staff_writer_a.py
│   │   ├── staff_writer_b.py
│   │   ├── story_editor.py
│   │   ├── research.py
│   │   ├── script_coordinator.py
│   │   └── qa.py
│   │
│   ├── workflow/                # LangGraph workflow
│   │   ├── __init__.py
│   │   ├── graph.py             # Graph definition
│   │   ├── state.py             # State schema
│   │   ├── nodes.py             # Node implementations
│   │   └── edges.py             # Edge conditions
│   │
│   ├── utils/                   # Utilities
│   │   ├── __init__.py
│   │   ├── config.py            # Config loading
│   │   ├── prompts.py           # Prompt assembly
│   │   ├── llm.py               # LLM interface with retry
│   │   └── formatting.py        # Script formatting
│   │
│   └── cli/                     # CLI interface
│       ├── __init__.py
│       ├── interface.py         # Terminal UI
│       └── checkpoints.py       # Human checkpoint handlers
│
├── output/                      # Generated sketches (gitignored)
│   ├── script.txt              # Final production script
│   ├── beat_sheet.txt          # Story structure reference
│   └── qa_report.txt           # Quality assessment
│
├── tests/                       # Unit tests
│   ├── test_agents.py
│   ├── test_workflow.py
│   └── test_formatting.py
│
├── docs/                        # Additional documentation
│   ├── langgraph-workflow.md    # Detailed workflow diagram
│   ├── architecture.md          # System architecture deep-dive
│   └── deployment.md            # Deployment guide
│
└── run_sketch.py               # Main entry point
```

### Key Implementation Files

#### `src/workflow/state.py` - State Schema

```python
from typing import TypedDict, List, Dict, Optional
from langgraph.graph import StateGraph

class SketchState(TypedDict):
    """
    Complete state for sketch generation workflow.
    Persists across all nodes and checkpoints.
    """
    
    # Configuration
    show_bible: str
    creative_prompt: str
    session_id: str
    
    # Stage 1: Pitch Session
    pitches: List[Dict]  # All pitch concepts
    research_notes_pitches: Dict
    compiled_pitches: str
    human_selected_pitches: List[str]
    showrunner_selected_pitch: str
    showrunner_vision_notes: str
    
    # Stage 2: Story Breaking
    character_details: Dict
    joke_map: Dict
    structural_framework: Dict
    research_details: Dict
    story_editor_validation: Dict
    beat_sheet: str
    human_beat_sheet_approval: bool
    human_beat_sheet_notes: str
    
    # Stage 3: Drafting
    section_assignments: Dict
    drafted_sections: List[str]
    first_draft: str
    showrunner_draft_notes: str
    
    # Stage 4: Table Read
    table_read_feedback: Dict
    story_editor_report: str
    revision_plan: str
    
    # Stage 5: Revision
    revision_assignments: Dict
    revised_sections: List[str]
    revised_draft: str
    iteration_count: int
    showrunner_revision_approved: bool
    
    # Stage 6: Polish
    formatted_script: str
    qa_report: Dict
    qa_approved: bool
    showrunner_final_review: str
    
    # Final
    human_final_approval: bool
    final_script: str
    
    # Metadata
    start_time: float
    end_time: Optional[float]
    agent_call_count: Dict[str, int]
    token_usage: Dict[str, int]
```

#### `src/workflow/graph.py` - LangGraph Definition

```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres import PostgresSaver
from .state import SketchState
from .nodes import *
from .edges import *

def build_workflow_graph():
    """
    Constructs the complete LangGraph workflow.
    """
    
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
    
    # Add edges (unconditional flow)
    workflow.add_edge("pitch_session", "human_pitch_review")
    workflow.add_edge("human_pitch_review", "showrunner_select")
    workflow.add_edge("showrunner_select", "story_breaking")
    workflow.add_edge("story_breaking", "human_beat_review")
    workflow.add_edge("drafting", "table_read")
    workflow.add_edge("table_read", "revision")
    workflow.add_edge("polish", "human_final_review")
    
    # Add conditional edges (decision points)
    workflow.add_conditional_edges(
        "human_beat_review",
        should_revise_beat_sheet,
        {
            "approved": "drafting",
            "needs_revision": "story_breaking"
        }
    )
    
    workflow.add_conditional_edges(
        "revision",
        should_continue_revision,
        {
            "approved": "polish",
            "needs_more_revision": "table_read",
            "max_iterations": "polish"
        }
    )
    
    workflow.add_conditional_edges(
        "human_final_review",
        should_approve_final,
        {
            "approved": END,
            "needs_revision": "revision"
        }
    )
    
    # Set entry point
    workflow.set_entry_point("pitch_session")
    
    return workflow

def compile_app(checkpointer=None):
    """
    Compiles the workflow into executable app.
    """
    workflow = build_workflow_graph()
    
    if checkpointer is None:
        from langgraph.checkpoint import MemorySaver
        checkpointer = MemorySaver()
    
    app = workflow.compile(checkpointer=checkpointer)
    
    return app
```

#### `src/agents/base.py` - Base Agent Class

```python
from abc import ABC, abstractmethod
from typing import Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential
import os

class BaseAgent(ABC):
    """
    Base class for all agents.
    Handles prompt assembly, LLM calls with retry, and response parsing.
    """
    
    def __init__(self, name: str, model: str = None):
        self.name = name
        self.model = model or os.getenv("OPENAI_MODEL_CREATIVE", "gpt-4")
        self.call_count = 0
        self.total_tokens = 0
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Returns the agent's system prompt (identity, role, expertise).
        Implemented by each specific agent.
        """
        pass
    
    @abstractmethod
    def build_task_prompt(self, state: Dict[str, Any], task_type: str) -> str:
        """
        Builds task-specific prompt from state and task type.
        Implemented by each specific agent.
        """
        pass
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def call_llm(self, messages: List[Dict]) -> str:
        """
        Calls LLM with retry logic.
        Tracks token usage and call count.
        """
        from langchain_openai import ChatOpenAI
        
        llm = ChatOpenAI(model=self.model, temperature=0.7)
        
        response = await llm.ainvoke(messages)
        
        self.call_count += 1
        self.total_tokens += response.usage.total_tokens
        
        return response.content
    
    async def execute(self, state: Dict[str, Any], task_type: str) -> str:
        """
        Main execution method.
        Assembles prompt, calls LLM, returns response.
        """
        system_prompt = self.get_system_prompt()
        task_prompt = self.build_task_prompt(state, task_type)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task_prompt}
        ]
        
        response = await self.call_llm(messages)
        
        return response
    
    def get_stats(self) -> Dict:
        """Returns usage statistics for monitoring."""
        return {
            "agent": self.name,
            "calls": self.call_count,
            "tokens": self.total_tokens
        }
```

#### `src/agents/senior_writer_a.py` - Example Agent Implementation

```python
from .base import BaseAgent

class SeniorWriterA(BaseAgent):
    """
    Senior Writer Agent A - Premise & Character Specialist
    """
    
    def __init__(self):
        super().__init__(name="Senior Writer A")
    
    def get_system_prompt(self) -> str:
        """
        Returns complete system prompt from agent_prompts.md
        """
        # In production, load from prompts/agent_prompts.md
        # For now, return the core prompt
        return """
        # SENIOR WRITER AGENT A - PREMISE & CHARACTER SPECIALIST
        
        ## YOUR ROLE
        You are the Premise & Character expert. You generate high-concept 
        sketch premises with clear games, develop distinctive character 
        voices, and ensure characters drive the comedy through their 
        unique perspectives.
        
        ## YOUR EXPERTISE
        - Premise identification and "What if..." thinking
        - Character voice distinction and consistency
        - Understanding sketch comedy "game" structure
        - Heightening and escalation principles
        - Creating specificity that drives comedy
        
        ## YOUR RESPONSIBILITIES
        - Generate premise-driven pitch concepts
        - Develop character details and voices during story breaking
        - Draft character-heavy sections of scripts
        - Validate character consistency during table reads
        - Fix character-related issues during revision
        
        [... full prompt from agent_prompts.md ...]
        """
    
    def build_task_prompt(self, state: dict, task_type: str) -> str:
        """
        Builds task-specific prompt based on workflow stage.
        """
        show_bible = state.get("show_bible", "")
        creative_prompt = state.get("creative_prompt", "")
        
        if task_type == "generate_pitches":
            return f"""
            # TASK: GENERATE PREMISE-DRIVEN PITCH CONCEPTS
            
            Generate 2 strong sketch pitch concepts based on the creative prompt.
            
            ## Creative Prompt
            {creative_prompt}
            
            ## Show Bible (Your Show's Guidelines)
            {show_bible}
            
            ## Your Task
            Generate 2 pitches that:
            - Have clear, repeatable "games"
            - Feature strong character perspectives
            - Align with show tone
            - Include escalation potential
            
            ## Output Format
            [Format as specified in agent_prompts.md]
            """
        
        elif task_type == "develop_characters":
            beat_concept = state.get("showrunner_selected_pitch", "")
            vision = state.get("showrunner_vision_notes", "")
            
            return f"""
            # TASK: DEVELOP CHARACTER DETAILS FOR STORY BREAKING
            
            ## Selected Pitch
            {beat_concept}
            
            ## Showrunner's Vision
            {vision}
            
            ## Show Bible
            {show_bible}
            
            ## Your Task
            Develop complete character details...
            [Full task prompt]
            """
        
        # ... other task types ...
    
    async def generate_pitches(self, state: dict) -> List[Dict]:
        """
        Convenience method for pitch generation.
        """
        response = await self.execute(state, "generate_pitches")
        pitches = self.parse_pitches(response)
        return pitches
    
    def parse_pitches(self, response: str) -> List[Dict]:
        """
        Parses LLM response into structured pitch objects.
        """
        # Parse response into structured format
        # Return list of pitch dicts
        pass
```

### Running in Development

```bash
# Run with debug logging
python run_sketch.py --debug --session "test_001"

# Run specific stage only (for testing)
python run_sketch.py --stage pitch_session --mock-checkpoints

# Override model for all agents (by default, creative agents use Sonnet and support agents use Haiku)
python run_sketch.py --model claude-sonnet-4-6
python run_sketch.py --model claude-opus-4-6      # highest quality

# Run with custom config
python run_sketch.py --show-bible custom_bible.md --prompt custom_prompt.md

# View workflow graph
python -c "from src.workflow.graph import build_workflow_graph; \
           graph = build_workflow_graph(); \
           graph.get_graph().draw_mermaid_png(output_file='workflow.png')"
```

### Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_agents.py

# Run with coverage
pytest --cov=src tests/

# Test individual agent
python -m pytest tests/test_agents.py::test_senior_writer_a_pitch_generation
```

### Monitoring & Observability

```bash
# Set up LangSmith monitoring
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=your_langsmith_key
export LANGCHAIN_PROJECT=sketch-comedy-agents

# View traces at: https://smith.langchain.com
```

### Deployment Considerations

**Local Development:**
- Use MemorySaver for checkpointing (state in memory)
- Run CLI interface
- Manual human checkpoints

**Production:**
- Use PostgresSaver for persistent checkpointing
- Build web UI for human checkpoints (Flask/FastAPI + React)
- Add authentication for multi-user access
- Queue system for batch processing
- Monitoring dashboard

### Performance Optimization

**Model Selection:**
```python
# agents/config.py
AGENT_MODELS = {
    # Creative leads: Use best model
    "showrunner": "gpt-4",
    "senior_writer_a": "gpt-4",
    "senior_writer_b": "gpt-4",
    
    # Support roles: Use faster model
    "story_editor": "gpt-3.5-turbo",
    "research": "gpt-3.5-turbo",
    "script_coordinator": "gpt-3.5-turbo",
    "qa": "gpt-4",  # QA needs good judgment
}
```

**Caching:**
```python
# Cache show bible (doesn't change often)
from functools import lru_cache

@lru_cache(maxsize=1)
def load_show_bible():
    with open("show_bible.md") as f:
        return f.read()
```

**Parallel Execution:**
```python
# Use asyncio for parallel agent calls
import asyncio

async def pitch_session():
    tasks = [
        staff_writer_a.generate_pitches(state),
        staff_writer_b.generate_pitches(state),
        senior_writer_a.generate_pitches(state),
        senior_writer_b.generate_pitches(state)
    ]
    results = await asyncio.gather(*tasks)
    return results
```

---

## Troubleshooting

### Common Issues

#### Issue: "API Key Not Found"

```
Error: OpenAI API key not found
```

**Solution:**
1. Check `.env` file exists in project root
2. Verify `OPENAI_API_KEY=sk-...` is set correctly
3. Restart terminal/reload environment
4. Verify with: `python -c "import os; print(os.getenv('OPENAI_API_KEY'))"`

---

#### Issue: "Module Not Found"

```
ModuleNotFoundError: No module named 'langgraph'
```

**Solution:**
1. Activate virtual environment: `source venv/bin/activate`
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Verify installation: `pip list | grep langgraph`

---

#### Issue: "Agent Timeout"

```
Error: Agent call timed out after 30 seconds
```

**Solution:**
1. Check internet connection
2. Verify API key is valid (not rate-limited)
3. Increase timeout in `src/utils/llm.py`:
   ```python
   llm = ChatOpenAI(model=model, timeout=60)  # Increase to 60s
   ```

---

#### Issue: "Checkpoint Not Found"

```
Error: Could not resume workflow - checkpoint not found
```

**Solution:**
1. If using MemorySaver: State is lost after restart (expected)
2. If using PostgresSaver: Check database connection
3. Start fresh session: `python run_sketch.py --new-session`

---

#### Issue: "Poor Quality Output"

**Symptoms:** Agents produce generic/weak content

**Solution:**
1. **Improve show_bible.md**: Add more specific examples and guidelines
2. **Improve creative_prompt.md**: Be more specific about what you want
3. **Adjust prompts**: Edit `prompts/agent_prompts.md` with better examples
4. **Change models**: Try GPT-4 for all agents (higher cost, better quality)
5. **Increase temperature**: In `src/utils/llm.py`, try `temperature=0.8`

---

#### Issue: "Revision Loop"

**Symptoms:** System stuck in endless revision cycles

**Solution:**
1. Check `MAX_REVISION_CYCLES` in `.env` (should be 3)
2. Verify Showrunner approval logic in `src/agents/showrunner.py`
3. Lower quality threshold temporarily for testing
4. Add debug logging to see why approval fails

---

### Debug Mode

```bash
# Run with verbose logging
python run_sketch.py --debug

# Output shows:
# 🔍 [DEBUG] Loading show bible from: show_bible.md
# 🔍 [DEBUG] Loaded 2,347 characters
# 🔍 [DEBUG] Initializing Staff Writer A agent...
# 🔍 [DEBUG] Calling LLM with prompt (1,234 tokens)...
# 🔍 [DEBUG] Received response (567 tokens)
# 🔍 [DEBUG] Parsed 3 pitches from response
# ... etc
```

---

## Costs & Performance

### Estimated Costs per Sketch

Based on OpenAI API pricing (as of Feb 2026):

**Configuration: GPT-4 for creative, GPT-3.5 for support**

| Stage | Agents | Tokens (avg) | Cost |
|-------|--------|--------------|------|
| Pitch Session | 4 creative | ~8,000 | $0.24 |
| Story Breaking | 3 creative + 2 support | ~12,000 | $0.36 |
| Drafting | 2 creative + 2 support | ~15,000 | $0.45 |
| Table Read | 4 creative + 2 support | ~10,000 | $0.30 |
| Revision (1 cycle) | 2 creative + 1 support | ~8,000 | $0.24 |
| Polish | 2 support | ~3,000 | $0.06 |
| **Total per sketch** | | **~56,000** | **$1.65** |

**With 2 revision cycles:** ~$2.13 per sketch  
**With 3 revision cycles:** ~$2.61 per sketch

**Monthly cost estimates:**
- 5 sketches/month: $8-13
- 10 sketches/month: $16-26
- 20 sketches/month: $33-52

**Configuration: GPT-4 for all agents** (highest quality):
- ~$2.80 per sketch
- 10 sketches/month: ~$28

**Configuration: GPT-3.5 for all agents** (fastest/cheapest):
- ~$0.28 per sketch
- 10 sketches/month: ~$2.80

### Time Performance

**Average sketch generation time:** 55-90 minutes

| Stage | Time |
|-------|------|
| Pitch Session | 5-10 min |
| Human Review #1 | 2-3 min |
| Story Breaking | 10-15 min |
| Human Review #2 | 3-5 min |
| Drafting | 15-20 min |
| Table Read | 10-15 min |
| Revision (1x) | 10-20 min |
| Polish | 5-10 min |
| Human Review #3 | 3-5 min |

**Parallelization improvements:**
- Pitch session: 4 agents in parallel → 7-8 min (vs. 28-32 min sequential)
- Table read: 6 agents in parallel → 10-15 min (vs. 60-90 min sequential)

**Bottlenecks:**
1. LLM API response time (network latency)
2. Human review time (depends on human availability)
3. Token generation speed (model-dependent)

### Optimization Strategies

**For Speed:**
1. Use GPT-3.5 for support agents (2x faster)
2. Implement caching for unchanged content
3. Reduce revision cycles (accept earlier)
4. Batch multiple sketch sessions

**For Cost:**
1. Use GPT-3.5 for all agents ($0.28/sketch)
2. Reduce max tokens per agent call
3. Implement prompt compression
4. Cache research results across sketches

**For Quality:**
1. Use GPT-4 for all agents ($2.80/sketch)
2. Increase revision cycles to 3
3. Add quality filters before human review
4. Enhance agent prompts with better examples

---

## Roadmap

### Phase 1: MVP (Weeks 1-2) ✅
- [x] Core agent prompts
- [x] LangGraph workflow structure
- [x] Basic CLI interface
- [x] Human checkpoints
- [x] Simple output files

### Phase 2: Production (Weeks 3-4)
- [ ] Web UI for human checkpoints
- [ ] PostgreSQL persistence
- [ ] Enhanced error handling
- [ ] Comprehensive testing suite
- [ ] Documentation site

### Phase 3: Enhancement (Weeks 5-6)
- [ ] Agent memory/learning
- [ ] Quality prediction (skip bad sketches early)
- [ ] A/B testing different prompt strategies
- [ ] Analytics dashboard
- [ ] Batch processing mode

### Phase 4: Advanced (Weeks 7-8)
- [ ] Fine-tuned models for specific agents
- [ ] Real-time collaboration (multiple humans)
- [ ] Version control for sketches
- [ ] Sketch library with search
- [ ] Automated production exports

### Future Ideas
- [ ] Voice-based human checkpoints
- [ ] Visual storyboarding agents
- [ ] Character consistency across multiple sketches
- [ ] Integration with production systems
- [ ] Mobile app for reviews on-the-go

---

## Support & Resources

### Documentation
- **This README**: Complete setup and usage guide
- **agent-prompts.md**: All agent prompt templates
- **langgraph-workflow.md**: Detailed workflow architecture
- **show_bible.md**: Example show bible (template)
- **creative_prompt.md**: Example creative prompt (template)

### External Resources
- [LangGraph Documentation](https://python.langchain.com/docs/langgraph)
- [LangChain Documentation](https://python.langchain.com/docs/)
- [OpenAI API Documentation](https://platform.openai.com/docs/)
- [Sketch Comedy Writing Guide](https://www.ucbcomedy.com/manual)

### Getting Help
1. **Check this README first** (most questions answered here)
2. **Review example outputs** in `examples/` folder
3. **Check GitHub Issues** for known problems
4. **LangGraph Discord** for framework questions
5. **Create GitHub Issue** for bugs or feature requests

### Contributing
- Fork repository
- Create feature branch
- Submit pull request
- Follow code style (Black formatter)
- Add tests for new features

---

## License

MIT License - See LICENSE file for details

---

## Credits

**System Design:** Based on real TV writers' room structures  
**Framework:** LangGraph by LangChain  
**Prompting:** Based on best practices from OpenAI and Anthropic  
**Comedy Principles:** Informed by UCB, Second City, and SNL methodologies

---

**Document Version:** 1.0  
**Last Updated:** February 2, 2026  
**Maintainer:** [Your Name]  
**Contact:** [Your Email]

---

**Ready to create amazing sketches? Run `python run_sketch.py` and let's go!** 🎭🎬✨
