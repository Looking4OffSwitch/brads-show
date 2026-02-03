# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a multi-agent sketch comedy writing system using LangGraph and LangChain. It simulates a TV writers' room with 10 specialized LLM agents collaborating through a 6-stage workflow to produce sketch comedy scripts.

**Current Status:** Fully implemented and operational.

## Team

- **Brad** - The writer. Provides all creative material, ideas, and direction. Non-technical; works with markdown files only. See `QUICK_START.md` for his guide.
- **Reed** - The engineer. Handles setup, runs the system, troubleshoots, and monitors via LangSmith.

Checkpoints involve input from both Brad and Reed together.

## How to Use (Quick Reference)

### For Brad (the writer)

See `QUICK_START.md` for the full guide.

```bash
# Create a new show (one time)
./new-show.sh "My Show Name"

# Write a sketch (from show folder)
cd Shows/my_show_name
# 1. Edit creative_prompt.md with your idea
# 2. Run the writers
./write.sh
```

### For Reed (the engineer)

```bash
# Setup (one time)
uv sync --extra dev
cp .env.example .env
# Edit .env with your ANTHROPIC_API_KEY

# Enable LangSmith tracing (optional but recommended)
# In .env, set:
#   LANGCHAIN_TRACING_V2=true
#   LANGCHAIN_API_KEY=<from smith.langchain.com>

# Run tests
pytest

# Run a show's write.sh for Brad
./Shows/silicon_silly/write.sh

# Test without human checkpoints
./Shows/test_show/write.sh --mock-checkpoints
```

## Folder Structure

```
brads_show/
├── Shows/                    # All shows live here
│   └── <show_name>/
│       ├── show_bible.md     # Show's style guide (edit once)
│       ├── creative_prompt.md # Sketch idea (edit each time)
│       ├── write.sh          <- ENTRY POINT for writing
│       └── output/           # Finished scripts
├── config/                   # Agent configuration (Brad can edit!)
│   └── agents/               # Agent definitions in markdown
│       ├── showrunner.md
│       ├── head_writer.md
│       ├── senior_writer_a.md
│       ├── senior_writer_b.md
│       ├── staff_writer_a.md
│       ├── staff_writer_b.md
│       ├── story_editor.md
│       ├── research.md
│       ├── script_coordinator.md
│       └── qa.md
├── new-show.sh              <- Creates new shows
├── QUICK_START.md           <- Brad's guide
├── src/                     # Agent code (Reed's domain)
│   ├── agents/              # Simplified agent classes (~40 lines each)
│   └── config/              # Configuration loaders and validation
└── tests/                   # Test suite
```

## Entry Points

| Who | Command | Purpose |
|-----|---------|---------|
| Brad | `./new-show.sh "Name"` | Create a new show |
| Brad | `./Shows/<show>/write.sh` | Write a sketch |
| Reed | `pytest` | Run tests |

**Note:** The underlying Python script (`src/run_sketch.py`) is called by `write.sh` automatically.

## Tech Stack

- **LangGraph** - Agentic workflow orchestration
- **LangChain** - LLM integration framework
- **LangSmith** - Observability and tracing
- **Python 3.10+** - Core language
- **Anthropic Claude** - LLM provider (Sonnet for creative, Haiku for support)

## Commands

```bash
# Setup
uv sync --extra dev

# Testing
pytest
pytest tests/test_agents.py -v
pytest --cov=src tests/

# Formatting
black src/ tests/

# Validate config without running
./Shows/test_show/write.sh --dry-run
```

## Coding Requirements

All code **must** adhere to modern Python software engineering practices: DRY, encapsulation, abstraction, rigorous error checking, parameter validation, verbose logging, and code readability.

## Agent Configuration Architecture

**NEW as of February 2026:** Agent definitions have been externalized from Python code to markdown configuration files. This allows non-technical users (Brad) to modify agent behaviors, prompts, and personalities without editing Python code.

### Configuration File Structure

Each agent is defined in `config/agents/[agent_name].md` with:

```markdown
---
# YAML Frontmatter - Structured Metadata
role: showrunner
tier: creative  # creative or support
model: claude-sonnet-4-20250514
authority: final  # final, high, medium-high, medium, advisory
description: "Agent's role summary"

collaborators:
  reports_to: null
  works_with:
    head_writer: "Collaboration description"

tasks:
  select_pitch:
    output_format: structured
    required_sections: [decision, rationale, creative_direction]

principles:
  - "Principle 1"
  - "Principle 2"
---

# Agent Name

## System Prompt

[Agent's identity, expertise, responsibilities, authority]

## Task Instructions

### task_name

[Specific instructions for this task]
```

### Loading Process

1. `src/config/agent_loader.py` parses markdown files
2. `src/config/validation.py` validates YAML schema and structure
3. Agents load prompts dynamically at runtime via `AgentLoader`
4. Changes to markdown files take effect immediately (no code restart needed)
5. Configuration errors are caught on startup with helpful messages

### How to Modify Agents

1. **Edit prompts:** Modify the `## System Prompt` or `### task_name` sections
2. **Add principles:** Update the `principles` list in YAML frontmatter
3. **Change authority:** Modify `authority` field (rarely needed)
4. **Validate:** Run `./Shows/test_show/write.sh --dry-run` to check syntax

**Python code reduced:** Agent classes went from ~260 lines to ~40 lines each (84% reduction).

## Architecture

### The 10 Agents

**Leadership:** Showrunner (final authority), Head Writer (orchestrator)
**Creative:** Senior Writer A (premise/character), Senior Writer B (dialogue), Staff Writer A (pitches), Staff Writer B (structure)
**Support:** Story Editor (continuity), Research Agent (facts/references)
**QA:** Script Coordinator (formatting), Quality Assurance (validation)

### 6-Stage Workflow

1. **Pitch Session** → 4 writers generate concepts in parallel → Human Checkpoint #1
2. **Story Breaking** → Beat sheet development → Human Checkpoint #2
3. **Script Drafting** → Parallel section writing → Showrunner review
4. **Table Read Simulation** → 6 agents review in parallel
5. **Revision Cycles** → Targeted fixes (max 3 iterations)
6. **Polish & Finalize** → Formatting + QA validation → Human Checkpoint #3

### State Management

- Shared `TypedDict` state persists across all workflow nodes
- `MemorySaver` for development, `PostgresSaver` for production
- Conditional edges route based on human feedback and quality thresholds

## Key Files

### Brad's Files (per show)
| File | Purpose |
|------|---------|
| `Shows/<show>/show_bible.md` | Show's creative guidelines (edit once) |
| `Shows/<show>/creative_prompt.md` | Sketch idea (edit each session) |
| `Shows/<show>/write.sh` | Run the AI writers |

### Agent Configuration Files (Brad can edit these!)
| File | Purpose |
|------|---------|
| `config/agents/showrunner.md` | Showrunner agent system prompts and task instructions |
| `config/agents/head_writer.md` | Head Writer agent prompts (6 tasks) |
| `config/agents/senior_writer_a.md` | Senior Writer A prompts (premise/character expert) |
| `config/agents/senior_writer_b.md` | Senior Writer B prompts (dialogue/jokes expert) |
| `config/agents/staff_writer_a.md` | Staff Writer A prompts (high-energy pitcher) |
| `config/agents/staff_writer_b.md` | Staff Writer B prompts (structure expert) |
| `config/agents/story_editor.md` | Story Editor prompts (continuity guardian) |
| `config/agents/research.md` | Research agent prompts (facts/references) |
| `config/agents/script_coordinator.md` | Script Coordinator prompts (formatting) |
| `config/agents/qa.md` | QA agent prompts (final validation) |

**Each agent file contains:**
- **YAML frontmatter** (metadata: role, tier, model, authority, tasks, principles)
- **## System Prompt** section (agent's identity and expertise)
- **## Task Instructions** sections (task-specific instructions)

**To modify an agent:** Open the `.md` file, edit the System Prompt or Task Instructions sections. Changes take effect immediately on next run. YAML frontmatter should rarely need changes.

### System Files
| File | Purpose |
|------|---------|
| `QUICK_START.md` | Brad's quick start guide |
| `new-show.sh` | Creates new show folders |
| `Docs/langgraph-workflow.md` | Workflow architecture details |
| `Docs/agent-prompts.md` | **DEPRECATED** - Agent prompts now in `config/agents/` |

## Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...

# Optional: Model overrides
ANTHROPIC_MODEL_CREATIVE=claude-sonnet-4-20250514
ANTHROPIC_MODEL_SUPPORT=claude-3-5-haiku-20241022

# Optional: Workflow settings
MAX_REVISION_CYCLES=3
TARGET_SKETCH_LENGTH=5

# Optional: LangSmith tracing (recommended for debugging)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls-...
LANGCHAIN_PROJECT=sketch-comedy-agents
```

## LangSmith Tracing

When enabled, all LLM calls are traced with:
- **Agent identification** (which of the 10 agents made the call)
- **Task type** (generate_pitches, review_draft, etc.)
- **Session ID** (groups all calls for one sketch)
- **Token usage** and latency

View traces at https://smith.langchain.com

## Development Rules

- **All work must be tested before any task is considered complete.** Run relevant tests or write new tests to verify functionality.
