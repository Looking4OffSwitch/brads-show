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
├── new-show.sh              <- Creates new shows
├── QUICK_START.md           <- Brad's guide
├── src/                     # Agent code (Reed's domain)
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

### System Files
| File | Purpose |
|------|---------|
| `QUICK_START.md` | Brad's quick start guide |
| `new-show.sh` | Creates new show folders |
| `Docs/agent-prompts.md` | System prompts for all 10 agents |
| `Docs/langgraph-workflow.md` | Workflow architecture details |

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
