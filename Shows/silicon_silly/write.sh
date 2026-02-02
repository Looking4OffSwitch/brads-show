#!/bin/bash
#
# write.sh - AI Writers' Room for Silicon Silly
#
# Usage:
#   ./write.sh                    Start the writing process
#   ./write.sh --mock-checkpoints Auto-approve all checkpoints (for testing)
#   ./write.sh --dry-run          Check setup without running
#   ./write.sh --debug            Show detailed logs
#

set -e

# Get paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SHOW_NAME="silicon_silly"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}══════════════════════════════════════════${NC}"
echo -e "${BLUE}  Silicon Silly${NC}"
echo -e "${BLUE}  AI Writers' Room${NC}"
echo -e "${BLUE}══════════════════════════════════════════${NC}"
echo ""

# Check that show_bible.md exists and has been edited
if [ ! -f "$SCRIPT_DIR/show_bible.md" ]; then
    echo -e "${RED}ERROR: show_bible.md not found${NC}"
    echo "This file should define your show's style. Please create it."
    exit 1
fi

if grep -q "\[BRACKETED TEXT\]" "$SCRIPT_DIR/show_bible.md" 2>/dev/null; then
    echo -e "${YELLOW}WARNING: show_bible.md still has template placeholders${NC}"
    echo "Edit the file to replace [BRACKETED TEXT] with your content."
    echo ""
    read -p "Continue anyway? (y/N): " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check creative_prompt.md
if [ ! -f "$SCRIPT_DIR/creative_prompt.md" ]; then
    echo -e "${RED}ERROR: creative_prompt.md not found${NC}"
    echo "This file should contain your sketch idea. Please create it."
    exit 1
fi

if grep -q "\[BRACKETED TEXT\]" "$SCRIPT_DIR/creative_prompt.md" 2>/dev/null; then
    echo -e "${YELLOW}WARNING: creative_prompt.md still has template placeholders${NC}"
    echo "Edit the file to add your sketch idea."
    echo ""
    read -p "Continue anyway? (y/N): " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Change to project root for Python imports
cd "$PROJECT_ROOT"

# Activate virtual environment
if [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
else
    echo -e "${RED}ERROR: Virtual environment not found${NC}"
    echo "Ask Reed to run: uv sync"
    exit 1
fi

# Show what we're working with
echo -e "${GREEN}Show:${NC}   Silicon Silly"
echo -e "${GREEN}Input:${NC}  show_bible.md, creative_prompt.md"
echo -e "${GREEN}Output:${NC} $SCRIPT_DIR/output/"
echo ""

# Check for LangSmith tracing
if [ "$LANGCHAIN_TRACING_V2" = "true" ]; then
    echo -e "${BLUE}📊 LangSmith tracing enabled${NC}"
    echo ""
fi

echo "The AI will pause at 3 checkpoints for your review:"
echo "  1. Pitch Selection    - Pick which idea to develop"
echo "  2. Beat Sheet Review  - Approve the sketch structure"
echo "  3. Final Review       - Approve the finished script"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop at any time${NC}"
echo ""
echo "──────────────────────────────────────────"
echo ""

# Run the writing system
exec python3 "$PROJECT_ROOT/src/run_sketch.py" --show "$SHOW_NAME" "$@"
