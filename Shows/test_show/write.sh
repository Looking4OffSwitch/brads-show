#!/bin/bash
#
# write.sh - Run the AI writing system for Test Show
#
# Usage:
#   ./write.sh                    Run the full writing workflow
#   ./write.sh --debug            Run with debug logging
#   ./write.sh --mock-checkpoints Run with auto-approved checkpoints (testing)
#   ./write.sh --dry-run          Validate configuration only
#   ./write.sh --help             Show all options
#
# This script:
#   1. Reads your show_bible.md and creative_prompt.md
#   2. Generates sketch pitches using 10 AI agents
#   3. Guides you through the 6-stage writing process
#   4. Saves finished scripts to the output/ folder
#

set -e

# Get paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SHOW_NAME="test_show"

# Display header
echo ""
echo "=========================================="
echo "  Test Show"
echo "  AI Writers' Room"
echo "=========================================="
echo ""

# Check that show_bible.md and creative_prompt.md have been edited
if grep -q "\[BRACKETED TEXT\]" "$SCRIPT_DIR/show_bible.md" 2>/dev/null; then
    echo "WARNING: show_bible.md still contains template placeholders."
    echo "Please edit show_bible.md before running the workflow."
    echo ""
    read -p "Continue anyway? (y/N): " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        echo "Exiting. Edit show_bible.md and try again."
        exit 1
    fi
fi

if grep -q "\[BRACKETED TEXT\]" "$SCRIPT_DIR/creative_prompt.md" 2>/dev/null; then
    echo "WARNING: creative_prompt.md still contains template placeholders."
    echo "Please edit creative_prompt.md with your sketch idea."
    echo ""
    read -p "Continue anyway? (y/N): " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        echo "Exiting. Edit creative_prompt.md and try again."
        exit 1
    fi
fi

# Change to project root for imports to work
cd "$PROJECT_ROOT"

# Activate virtual environment if it exists
if [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
fi

# Run the writing system with the show folder set
echo "Starting AI Writers' Room..."
echo "Show: Test Show"
echo "Files: show_bible.md, creative_prompt.md"
echo "Output: $SCRIPT_DIR/output/"
echo ""
echo "The workflow has 3 checkpoints where you'll review and approve:"
echo "  1. Pitch Selection - Choose which sketch idea to develop"
echo "  2. Beat Sheet Approval - Approve the sketch structure"
echo "  3. Final Script Approval - Approve the finished script"
echo ""
echo "Press Ctrl+C at any time to interrupt."
echo ""
echo "------------------------------------------"
echo ""

# Run the main script with show folder override
exec python3 "$PROJECT_ROOT/run_sketch.py" --show "$SHOW_NAME" "$@"
