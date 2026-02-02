# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a multi-agent sketch comedy writing system using LangGraph and LangChain. It simulates a TV writers' room with 10 specialized LLM agents collaborating through a 6-stage workflow to produce sketch comedy scripts.

**Current Status:** Documentation and architecture specification complete; implementation code pending.

## Team

- **Brad** - The writer. Provides all creative material, ideas, and direction. Non-technical; works with markdown files only.
- **Reed** - The engineer. Enters information into the system, runs the workflow, and handles all technical issues.

Checkpoints involve input from both Brad and Reed together.

## Multi-Project Support

This system supports multiple shows/skits simultaneously. Each project lives in its own folder under `Shows/`, while sharing the same agent architecture. The folder structure and agent coordination remain consistent; only the creative content changes per project.

### Creating a New Show

```bash
./new-show.sh "Show Name"
```

This creates a folder at `Shows/show_name/` with:
- `show_bible.md` - Template for the show's creative guidelines
- `creative_prompt.md` - Template for sketch ideas
- `write.sh` - Script to run the writing system (stub for now)
- `output/` - Folder for finished scripts

### Folder Structure

```
brads_show/
├── Shows/                    # All show projects live here
│   └── <show_name>/
│       ├── show_bible.md     # Brad edits: show's style guide
│       ├── creative_prompt.md # Brad edits: sketch idea
│       ├── write.sh          # Runs the writing system
│       └── output/           # Finished scripts
├── templates/                # Template files for new shows
├── new-show.sh              # Creates new show folders
└── src/                     # Agent system code (Reed's domain)
```

## Tech Stack

- **LangGraph** - Agentic workflow orchestration
- **LangChain** - LLM integration framework
- **Python 3.10+** - Core language
- **Anthropic** - LLM provider (Claude Sonnet for creative roles, Claude Haiku for support roles)

## Commands

```bash
# Setup
uv venv
source .venv/bin/activate
uv sync

# Run workflow
python run_sketch.py
python run_sketch.py --session "sketch_001"
python run_sketch.py --debug
python run_sketch.py --stage pitch_session --mock-checkpoints

# Verify setup
python verify_setup.py

# Testing
pytest
pytest tests/test_agents.py
pytest tests/test_workflow.py
pytest --cov=src tests/

# Formatting
black src/ tests/
```

## Coding requirements

All code **must** adhere to modern Python software engineering practices and guidelines. The includes "don't repeat yourself (DRY)", encapsulation, abstraction, rigorous error checking, parameter validation, verbose logging to make debugging easier, and code readability and code comments.

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
| `Shows/<show>/show_bible.md` | Show's creative guidelines (edit once at setup) |
| `Shows/<show>/creative_prompt.md` | Per-sketch starting prompt (edit each session) |

### System Files
| File | Purpose |
|------|---------|
| `new-show.sh` | Creates new show folders with templates |
| `HOW_TO_CREATE_A_SKIT.md` | Brad's guide for creating sketches |
| `templates/` | Template files copied to new shows |
| `agent-prompts.md` | Complete system prompts for all 10 agents |
| `langgraph-workflow.md` | Detailed workflow architecture and LangGraph implementation |

## Environment Variables

```bash
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL_CREATIVE=claude-sonnet-4-20250514
ANTHROPIC_MODEL_SUPPORT=claude-3-5-haiku-20241022

# Project Settings
SHOW_FOLDER=test_show  # Which show folder to use from Shows/
MAX_REVISION_CYCLES=3
TARGET_SKETCH_LENGTH=5

# Optional monitoring
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls-...
LANGCHAIN_PROJECT=sketch-comedy-agents
```

## Implementation Notes

- Agents communicate asynchronously via shared state (no direct agent-to-agent calls)
- Head Writer synthesizes outputs from multiple agents
- Prompts in `agent-prompts.md` include role identity, task instructions, output formats, and comedy principles
- Human feedback uses structured markdown templates
- Parallelization at Stage 1 (4 writers) and Stage 4 (6 reviewers) for efficiency

## Development Rules

- **All work must be tested before any task is considered complete.** Run relevant checkpoint tests or write new tests to verify functionality before marking implementation done.
