# TODO.md

Step-by-step guide to setup, configure, and implement the Sketch Comedy LLM Agent System.

Each phase has a **Checkpoint** section with tests to verify everything is working before moving on.

---

## Phase 1: Environment Setup

### 1.1 Install Python 3.10+

**For everyone:**

Download and install Python from https://www.python.org/downloads/

Choose version 3.10 or higher.

**Checkpoint:**
```bash
python3 --version
```
Expected output: `Python 3.10.x` or higher (3.11, 3.12, etc.)

---

### 1.2 Install uv (Python Package Manager)

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

After installation, restart your terminal.

**Checkpoint:**
```bash
uv --version
```
Expected output: `uv 0.x.x` (any version number)

---

### 1.3 Create Virtual Environment and Install Dependencies

Navigate to the project folder and run:

```bash
cd /path/to/brads_show
uv venv
source .venv/bin/activate  # macOS/Linux
# OR
.venv\Scripts\activate  # Windows
```

Then install dependencies:
```bash
uv sync
```

**Checkpoint:**
```bash
uv pip list | grep langgraph
```
Expected output: `langgraph` with a version number

If `uv sync` fails because there's no `pyproject.toml`, proceed to Phase 2.1 first.

---

## Phase 2: Project Configuration

### 2.1 Create pyproject.toml

Create file `pyproject.toml` in the project root:

```toml
[project]
name = "brads-show"
version = "1.0.0"
description = "Multi-agent sketch comedy writing system"
requires-python = ">=3.10"
dependencies = [
    "langgraph>=0.2.0",
    "langchain>=0.3.0",
    "langchain-openai>=0.2.0",
    "langchain-anthropic>=0.2.0",
    "python-dotenv>=1.0.0",
    "tenacity>=8.0.0",
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.0.0",
    "pytest-asyncio>=0.23.0",
    "black>=24.0.0",
]
monitoring = [
    "langsmith>=0.1.0",
]

[tool.black]
line-length = 100
target-version = ["py310"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

**Checkpoint:**
```bash
uv sync
uv pip list | grep langchain
```
Expected output: Multiple langchain packages listed

---

### 2.2 Create .env File for API Keys

Create file `.env` in the project root (this file contains secrets - never commit it):

```bash
# Copy the example below and fill in your actual API key
```

```
# Choose ONE LLM provider:

# Option A: OpenAI (recommended)
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL_CREATIVE=gpt-4
OPENAI_MODEL_SUPPORT=gpt-3.5-turbo

# Option B: Anthropic
# ANTHROPIC_API_KEY=sk-ant-your-key-here
# ANTHROPIC_MODEL_CREATIVE=claude-3-5-sonnet-20241022

# Project Settings
SHOW_NAME="My Sketch Show"
MAX_REVISION_CYCLES=3
TARGET_SKETCH_LENGTH=5
```

**Where to get API keys:**
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/

**Checkpoint:**
```bash
python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); print('API Key found:', 'Yes' if os.getenv('OPENAI_API_KEY') or os.getenv('ANTHROPIC_API_KEY') else 'No')"
```
Expected output: `API Key found: Yes`

---

### 2.3 Create .gitignore

Create file `.gitignore` in the project root:

```
# Environment
.env
.venv/
venv/
__pycache__/
*.pyc

# Output
output/

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db
```

**Checkpoint:**
```bash
cat .gitignore | grep ".env"
```
Expected output: `.env`

---

## Phase 3: Creative Configuration

These steps involve both **Reed** (engineer) and **Brad** (creative partner).

### 3.1 Create a New Show (Reed)

Run the new-show script to create a show folder:

```bash
./new-show.sh "Your Show Name"
```

This creates `Shows/your_show_name/` with:
- `show_bible.md` - Template for show's creative guidelines
- `creative_prompt.md` - Template for sketch ideas
- `write.sh` - Script to run the writing system (stub for now)
- `output/` - Folder for finished scripts

**Checkpoint:**
```bash
ls Shows/your_show_name/
```
Expected output: `creative_prompt.md  output  show_bible.md  write.sh`

---

### 3.2 Customize the Show Bible (Brad)

Open `Shows/your_show_name/show_bible.md` in any text editor (VS Code, Notepad, TextEdit, etc.)

The template has `[BRACKETED TEXT]` placeholders. Replace each with your content:
- [ ] Update "Show Identity" with your show's name and description
- [ ] List comedy styles you want (and don't want)
- [ ] Define content boundaries (what's off-limits)
- [ ] Add 2-3 reference sketches you admire
- [ ] Describe character types that work for your show

Save the file when done.

**Checkpoint:**

Read through your edited `show_bible.md` and verify:
- [ ] Your show has a clear name and identity
- [ ] At least 3 comedy styles are listed as "embrace"
- [ ] At least 2 comedy styles are listed as "avoid"
- [ ] Content guidelines section is filled out
- [ ] At least 1 reference sketch is included

---

### 3.3 Prepare Your First Creative Prompt (Brad)

Open `Shows/your_show_name/creative_prompt.md` in any text editor.

The template has `[BRACKETED TEXT]` placeholders. For your first test, keep it simple. Fill in:
- [ ] A clear theme or inspiration (1-2 sentences) - **Required**
- [ ] 2-3 specific requirements (must-include elements) - Optional
- [ ] Character types involved - Optional
- [ ] The tone/energy you want - Optional

Delete any sections you don't need. Save the file when done.

**Checkpoint:**

Read through your edited `creative_prompt.md` and verify:
- [ ] The core idea is clear in one sentence
- [ ] At least 2 "must include" elements are listed (if you have specific requirements)
- [ ] You've described the tone (silly, dark, absurd, etc.)

---

## Phase 4: Implementation

### 4.1 Create Project Directory Structure

```bash
mkdir -p src/agents src/workflow src/utils src/cli tests output
touch src/__init__.py src/agents/__init__.py src/workflow/__init__.py src/utils/__init__.py src/cli/__init__.py
```

**Checkpoint:**
```bash
ls -la src/
```
Expected output: Shows `agents/`, `workflow/`, `utils/`, `cli/` directories

---

### 4.2 Implement Configuration Loader

- [ ] Create `src/utils/config.py`
  - Load `.env` file
  - Read `SHOW_FOLDER` from env to determine which show to load
  - Load `Shows/<SHOW_FOLDER>/show_bible.md`
  - Load `Shows/<SHOW_FOLDER>/creative_prompt.md`
  - Validate all required values exist
  - Support CLI override: `load_config(show_folder="other_show")`

**Checkpoint:**
```bash
source .venv/bin/activate && python3 -c "from src.utils.config import load_config; cfg = load_config(); print('Config loaded:', 'show_bible' in cfg and 'creative_prompt' in cfg)"
```
Expected output: `Config loaded: True`

---

### 4.3 Implement LLM Interface

- [ ] Create `src/utils/llm.py`
  - Initialize OpenAI or Anthropic client based on env vars
  - Add retry logic with tenacity
  - Track token usage

**Checkpoint:**
```bash
python3 -c "from src.utils.llm import get_llm; llm = get_llm(); print('LLM initialized:', llm is not None)"
```
Expected output: `LLM initialized: True`

---

### 4.4 Implement Base Agent Class

- [ ] Create `src/agents/base.py`
  - Abstract base class for all agents
  - System prompt loading
  - Task prompt building
  - LLM call execution

**Checkpoint:**
```bash
python3 -c "from src.agents.base import BaseAgent; print('BaseAgent importable: True')"
```
Expected output: `BaseAgent importable: True`

---

### 4.5 Implement All 10 Agents

Create each agent file using prompts from `agent-prompts.md`:

- [ ] `src/agents/showrunner.py` - Final creative authority
- [ ] `src/agents/head_writer.py` - Process manager
- [ ] `src/agents/senior_writer_a.py` - Premise & character specialist
- [ ] `src/agents/senior_writer_b.py` - Dialogue & punch-up specialist
- [ ] `src/agents/staff_writer_a.py` - High-volume pitch generator
- [ ] `src/agents/staff_writer_b.py` - Structure & callback specialist
- [ ] `src/agents/story_editor.py` - Continuity & quality control
- [ ] `src/agents/research.py` - Facts & references
- [ ] `src/agents/script_coordinator.py` - Formatting
- [ ] `src/agents/qa.py` - Final validation

**Checkpoint:**
```bash
python3 -c "
from src.agents.showrunner import ShowrunnerAgent
from src.agents.head_writer import HeadWriterAgent
from src.agents.senior_writer_a import SeniorWriterA
from src.agents.senior_writer_b import SeniorWriterB
from src.agents.staff_writer_a import StaffWriterA
from src.agents.staff_writer_b import StaffWriterB
from src.agents.story_editor import StoryEditorAgent
from src.agents.research import ResearchAgent
from src.agents.script_coordinator import ScriptCoordinatorAgent
from src.agents.qa import QAAgent
print('All 10 agents importable: True')
"
```
Expected output: `All 10 agents importable: True`

---

### 4.6 Implement Workflow State

- [ ] Create `src/workflow/state.py`
  - Define `SketchState` TypedDict
  - Include all fields from `langgraph-workflow.md`

**Checkpoint:**
```bash
python3 -c "from src.workflow.state import SketchState; print('SketchState fields:', len(SketchState.__annotations__))"
```
Expected output: `SketchState fields: 25` (approximately)

---

### 4.7 Implement Workflow Nodes

- [ ] Create `src/workflow/nodes.py`
  - `pitch_session_node` - Parallel pitch generation
  - `human_pitch_review_node` - Checkpoint #1
  - `showrunner_select_node` - Pitch selection
  - `story_breaking_node` - Beat sheet creation
  - `human_beat_review_node` - Checkpoint #2
  - `drafting_node` - Script writing
  - `table_read_node` - Parallel review
  - `revision_node` - Fix issues
  - `polish_node` - Format and validate
  - `human_final_review_node` - Checkpoint #3

**Checkpoint:**
```bash
python3 -c "
from src.workflow.nodes import (
    pitch_session_node, human_pitch_review_node, showrunner_select_node,
    story_breaking_node, human_beat_review_node, drafting_node,
    table_read_node, revision_node, polish_node, human_final_review_node
)
print('All 10 nodes importable: True')
"
```
Expected output: `All 10 nodes importable: True`

---

### 4.8 Implement Workflow Edges

- [ ] Create `src/workflow/edges.py`
  - `should_revise_beat_sheet` - Route after human beat review
  - `should_continue_revision` - Route after revision cycle
  - `should_approve_final` - Route after human final review

**Checkpoint:**
```bash
python3 -c "from src.workflow.edges import should_revise_beat_sheet, should_continue_revision, should_approve_final; print('All edge functions importable: True')"
```
Expected output: `All edge functions importable: True`

---

### 4.9 Implement Workflow Graph

- [ ] Create `src/workflow/graph.py`
  - `build_workflow_graph()` - Construct the LangGraph
  - `compile_app()` - Compile with checkpointer

**Checkpoint:**
```bash
python3 -c "from src.workflow.graph import compile_app; app = compile_app(); print('Workflow graph compiled: True')"
```
Expected output: `Workflow graph compiled: True`

---

### 4.10 Implement CLI Interface

- [ ] Create `src/cli/interface.py`
  - Terminal display functions
  - Progress indicators
  - Human checkpoint prompts

- [ ] Create `src/cli/checkpoints.py`
  - `handle_pitch_review()` - Display pitches, get selection
  - `handle_beat_review()` - Display beat sheet, get approval
  - `handle_final_review()` - Display script, get approval

**Checkpoint:**
```bash
python3 -c "from src.cli.interface import display_header; display_header('Test'); print('CLI interface works: True')"
```
Expected output: A header displayed, then `CLI interface works: True`

---

### 4.11 Create Main Entry Point

- [ ] Create `run_sketch.py`
  - Parse command line arguments
  - Load configuration
  - Initialize and run workflow
  - Handle human checkpoints
  - Save output files

**Checkpoint:**
```bash
python3 run_sketch.py --help
```
Expected output: Help text showing available options (`--session`, `--debug`, etc.)

---

## Phase 5: Testing

### 5.1 Create Unit Tests

- [ ] Create `tests/test_config.py` - Test configuration loading
- [ ] Create `tests/test_agents.py` - Test agent initialization and prompts
- [ ] Create `tests/test_workflow.py` - Test workflow graph construction
- [ ] Create `tests/test_edges.py` - Test conditional edge logic

**Checkpoint:**
```bash
uv run pytest tests/ -v
```
Expected output: All tests pass (green)

---

### 5.2 Create Integration Test

- [ ] Create `tests/test_integration.py`
  - Test full workflow with mocked LLM responses
  - Verify state transitions
  - Verify output generation

**Checkpoint:**
```bash
uv run pytest tests/test_integration.py -v
```
Expected output: Integration tests pass

---

### 5.3 Test with Real LLM (Small Scale)

Run a single stage to verify LLM connectivity:

```bash
python3 run_sketch.py --stage pitch_session --mock-checkpoints --debug
```

**Checkpoint:**
- [ ] No API errors
- [ ] Pitches are generated and displayed
- [ ] Token usage is logged

---

## Phase 6: First Full Run

### 6.1 Run Complete Workflow

```bash
python3 run_sketch.py --session "first_test"
```

**Checkpoint at Human Review #1 (Pitches):**
- [ ] 8-12 pitches displayed
- [ ] Each pitch has title, logline, and game
- [ ] You can select a pitch by number

**Checkpoint at Human Review #2 (Beat Sheet):**
- [ ] Beat sheet shows clear structure
- [ ] Beginning, middle, end are defined
- [ ] You can approve or request changes

**Checkpoint at Human Review #3 (Final Script):**
- [ ] Complete script displayed
- [ ] QA score shown (aim for 80%+)
- [ ] Script saved to `output/` folder

---

### 6.2 Verify Output Files

```bash
ls -la output/
```

**Checkpoint:**
- [ ] `script.txt` exists (the script)
- [ ] `beat_sheet.txt` exists (structure)
- [ ] `qa_report.txt` exists (quality assessment)

---

## Phase 7: Commit and Share

### 7.1 Commit Implementation

```bash
git add -A
git status  # Review what will be committed
git commit -m "Implement complete workflow system"
git push
```

**Checkpoint:**
```bash
git log --oneline -3
```
Expected output: Shows your implementation commit

---

## Quick Reference: Verification Commands

Run these anytime to check system health:

```bash
# Check Python and uv
python3 --version && uv --version

# Check dependencies installed
uv pip list | grep -E "langgraph|langchain"

# Check API key configured
python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); print('OpenAI:', bool(os.getenv('OPENAI_API_KEY'))); print('Anthropic:', bool(os.getenv('ANTHROPIC_API_KEY')))"

# Check all imports work
python3 -c "from src.workflow.graph import compile_app; print('System ready:', compile_app() is not None)"

# Run tests
uv run pytest tests/ -v

# Check output folder
ls -la output/
```

---

## Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| `command not found: uv` | Restart terminal after installing uv |
| `No module named 'langgraph'` | Run `source .venv/bin/activate` then `uv sync` |
| `API key not found` | Check `.env` file exists and has correct key |
| `Import error` | Check you're in the project root directory |
| `Tests fail` | Run `uv sync` to ensure all dependencies installed |

---

## Status Tracker

Use this to track your progress:

- [ ] **Phase 1: Environment Setup** - Python, uv, venv
- [ ] **Phase 2: Project Configuration** - pyproject.toml, .env, .gitignore
- [ ] **Phase 3: Creative Configuration** - show_bible.md, creative_prompt.md
- [ ] **Phase 4: Implementation** - All code files
- [ ] **Phase 5: Testing** - Unit and integration tests
- [ ] **Phase 6: First Full Run** - End-to-end verification
- [ ] **Phase 7: Commit and Share** - Push to GitHub
