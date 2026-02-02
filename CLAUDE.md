# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a multi-agent sketch comedy writing system using LangGraph and LangChain. It simulates a TV writers' room with 10 specialized LLM agents collaborating through a 6-stage workflow to produce sketch comedy scripts.

**Current Status:** Documentation and architecture specification complete; implementation code pending.

## Tech Stack

- **LangGraph** - Agentic workflow orchestration
- **LangChain** - LLM integration framework
- **Python 3.10+** - Core language
- **OpenAI/Anthropic** - LLM providers (GPT-4 for creative, GPT-3.5-turbo for support roles)

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

| File | Purpose |
|------|---------|
| `show_bible.md` | Show's creative guidelines (edit once at setup) |
| `creative_prompt.md` | Per-sketch starting prompt (edit each session) |
| `agent-prompts.md` | Complete system prompts for all 10 agents |
| `langgraph-workflow.md` | Detailed workflow architecture and LangGraph implementation |

## Environment Variables

```bash
OPENAI_API_KEY=sk-...
OPENAI_MODEL_CREATIVE=gpt-4
OPENAI_MODEL_SUPPORT=gpt-3.5-turbo
# OR
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL_CREATIVE=claude-3-5-sonnet-20241022

# Optional monitoring
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls-...
LANGCHAIN_PROJECT=sketch-comedy-agents

MAX_REVISION_CYCLES=3
TARGET_SKETCH_LENGTH=5
```

## Implementation Notes

- Agents communicate asynchronously via shared state (no direct agent-to-agent calls)
- Head Writer synthesizes outputs from multiple agents
- Prompts in `agent-prompts.md` include role identity, task instructions, output formats, and comedy principles
- Human feedback uses structured markdown templates
- Parallelization at Stage 1 (4 writers) and Stage 4 (6 reviewers) for efficiency
