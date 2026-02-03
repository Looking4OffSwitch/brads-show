# Deployment Guide

**Version:** 1.0
**Last Updated:** 2026-02-03
**System:** Sketch Comedy LLM Agent System

---

## Overview

This guide provides step-by-step instructions for deploying the Sketch Comedy Writing System from a fresh clone to a production-ready state.

## Prerequisites

### Required Software

| Software | Minimum Version | Installation |
|----------|----------------|--------------|
| Python | 3.10+ | https://www.python.org/downloads/ |
| uv | Latest | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Git | 2.x+ | https://git-scm.com/downloads |

### Required Accounts & API Keys

- **Anthropic API Key** (required) - Get from https://console.anthropic.com
- **LangSmith API Key** (optional but recommended) - Get from https://smith.langchain.com

### System Requirements

- **OS:** macOS, Linux, or WSL2 on Windows
- **RAM:** 2GB minimum, 4GB recommended
- **Disk:** 500MB for dependencies + storage for output files

---

## Installation Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd brads-show
```

### 2. Install Dependencies

The project uses `uv` for fast, reliable dependency management:

```bash
# Install all dependencies including dev tools
uv sync --extra dev
```

This will:
- Create a virtual environment in `.venv/`
- Install all production dependencies (LangChain, LangGraph, etc.)
- Install dev dependencies (pytest, black, pytest-cov)

**Expected output:**
```
Using CPython 3.X.X
Creating virtual environment at: .venv
Resolved 62 packages in XXXms
Installed 57 packages in XXXms
```

### 3. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your actual values
# Required:
#   ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
#
# Optional:
#   LANGCHAIN_TRACING_V2=true
#   LANGCHAIN_API_KEY=your-langsmith-key
```

**Minimal .env file:**
```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
SHOW_FOLDER=test_show
MAX_REVISION_CYCLES=3
TARGET_SKETCH_LENGTH=5
```

**With LangSmith tracing (recommended):**
```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
SHOW_FOLDER=test_show
MAX_REVISION_CYCLES=3
TARGET_SKETCH_LENGTH=5

# Observability
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langsmith-key
LANGCHAIN_PROJECT=sketch-comedy-agents
```

### 4. Verify Installation

```bash
# Activate virtual environment
source .venv/bin/activate  # On macOS/Linux
# .venv\Scripts\activate   # On Windows

# Run tests to verify everything works
pytest

# Check dry run
./Shows/test_show/write.sh --dry-run
```

**Expected output:**
```
===== 221 passed in X.XXs =====
Dry run successful - configuration is valid
```

---

## Creating Your First Show

### Option A: Use the Test Show

The repository includes `Shows/test_show/` which is ready to use:

```bash
cd Shows/test_show

# Edit creative_prompt.md with your sketch idea
nano creative_prompt.md  # or use any editor

# Run the writers
./write.sh
```

### Option B: Create a New Show

```bash
# From project root
./new-show.sh "My Show Name"

# This creates Shows/my_show_name/ with:
#   - show_bible.md (edit this to define your show's style)
#   - creative_prompt.md (edit this with your sketch idea)
#   - write.sh (run this to start writing)
#   - output/ (finished scripts appear here)

cd Shows/my_show_name

# 1. Edit show_bible.md
nano show_bible.md

# 2. Edit creative_prompt.md
nano creative_prompt.md

# 3. Run the writers
./write.sh
```

---

## Production Deployment Considerations

### Environment Setup

For production environments, consider:

1. **API Key Management**
   - Use secrets management (AWS Secrets Manager, HashiCorp Vault, etc.)
   - Never commit .env files to version control
   - Rotate keys periodically

2. **State Persistence**
   - Default: MemorySaver (in-memory, development only)
   - Production: PostgresSaver (requires PostgreSQL)
   - Configure in `src/workflow/graph.py` if needed

3. **Logging Configuration**
   - Default: INFO level to console
   - Production: Consider structured logging (JSON)
   - Ship logs to aggregation service (CloudWatch, Datadog, etc.)

### Monitoring & Observability

**LangSmith Tracing (Recommended):**
```bash
# In .env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=<your-key>
LANGCHAIN_PROJECT=sketch-comedy-agents
```

View traces at: https://smith.langchain.com

**What you'll see:**
- Every LLM call with token usage
- Agent identification and task type
- Session grouping for full sketch workflows
- Performance metrics and error tracking

### Performance & Cost

**Token Usage Estimates (per sketch):**
- Pitch Session: ~50K tokens
- Story Breaking: ~40K tokens
- Drafting: ~80K tokens
- Table Read: ~60K tokens
- Revision (per cycle): ~50K tokens
- Polish: ~30K tokens

**Total:** ~310K tokens per sketch (~3 revision cycles)

**Cost estimate (Anthropic Claude):**
- Sonnet (creative roles): ~60% of calls
- Haiku (support roles): ~40% of calls
- Approximate cost: $2-4 per sketch (varies by API pricing)

### Scaling Considerations

1. **Parallelization**
   - Pitch generation: 4 agents run in parallel
   - Table read: 6 agents run in parallel
   - Script drafting: Sections written in parallel

2. **Rate Limiting**
   - Tenacity retry logic built-in (3 attempts with exponential backoff)
   - Consider API provider rate limits
   - Anthropic: generous limits on paid tiers

3. **Caching**
   - No caching currently implemented
   - Consider caching show_bible.md content if running multiple sessions

---

## Troubleshooting

### Common Issues

**Issue: "No module named 'langchain_anthropic'"**
```bash
# Solution: Dependencies not installed
uv sync --extra dev
```

**Issue: "No LLM provider configured"**
```bash
# Solution: Missing API key
# 1. Check .env file exists
# 2. Verify ANTHROPIC_API_KEY is set correctly
# 3. Restart shell if you just set the variable
```

**Issue: "Show folder not found"**
```bash
# Solution: SHOW_FOLDER env var or --show parameter incorrect
# Check available shows:
ls Shows/

# Use specific show:
./Shows/test_show/write.sh
# or
python src/run_sketch.py --show test_show
```

**Issue: Tests failing with "ModuleNotFoundError"**
```bash
# Solution: Virtual environment not activated
source .venv/bin/activate
pytest
```

**Issue: "sed: invalid command" on new-show.sh (macOS)**
```bash
# This should be fixed in the latest version
# If you see this, update your repository
git pull origin main
```

---

## Running Tests

### Full Test Suite

```bash
source .venv/bin/activate
pytest
```

### With Coverage Report

```bash
pytest --cov=src tests/
```

### Specific Test File

```bash
pytest tests/test_agents.py -v
```

### Integration Test

```bash
# Run a full workflow with mocked checkpoints
./Shows/test_show/write.sh --mock-checkpoints
```

---

## Maintenance

### Updating Dependencies

```bash
# Update all dependencies to latest compatible versions
uv sync --upgrade

# Run tests after updating
pytest
```

### Code Formatting

```bash
# Check formatting
black --check src/ tests/

# Auto-format all code
black src/ tests/
```

### Log Rotation

Output files are timestamped: `{session_id}_{timestamp}_FINAL.txt`

Consider implementing cleanup:
```bash
# Example: Delete output files older than 30 days
find Shows/*/output -name "*.txt" -mtime +30 -delete
```

---

## Security Considerations

1. **API Keys**
   - Store in environment variables or secrets manager
   - Never log or print API keys
   - Rotate regularly

2. **Input Validation**
   - show_bible.md and creative_prompt.md are user-provided
   - Content is passed to LLM (no code execution risk)
   - Consider content filtering for production public-facing deployments

3. **Output Files**
   - Scripts written to Shows/{show}/output/
   - Review before sharing publicly
   - May contain user-provided sensitive information

4. **Dependencies**
   - Regularly update dependencies for security patches
   - Run security audits: `pip-audit` (install separately if needed)

---

## Support

- **Documentation:** See README.md, QUICK_START.md, and Docs/
- **Issues:** Report bugs via GitHub issues
- **Architecture:** See Docs/langgraph-workflow.md and Docs/agent-prompts.md

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `uv sync --extra dev` | Install dependencies |
| `pytest` | Run test suite |
| `black src/ tests/` | Format code |
| `./new-show.sh "Name"` | Create new show |
| `./Shows/{show}/write.sh` | Write a sketch |
| `--mock-checkpoints` | Auto-approve (testing) |
| `--dry-run` | Validate config only |
| `--debug` | Verbose logging |

---

## Deployment Checklist

- [ ] Python 3.10+ installed
- [ ] uv installed
- [ ] Repository cloned
- [ ] Dependencies installed (`uv sync --extra dev`)
- [ ] .env file created with ANTHROPIC_API_KEY
- [ ] Tests passing (`pytest`)
- [ ] Test show works (`./Shows/test_show/write.sh --dry-run`)
- [ ] LangSmith tracing configured (optional)
- [ ] Documentation reviewed (README.md, QUICK_START.md)
- [ ] Show created (`./new-show.sh "My Show"`)
- [ ] show_bible.md edited
- [ ] creative_prompt.md edited
- [ ] First sketch completed successfully

**Status:** ✅ DEPLOYMENT READY

