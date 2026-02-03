#!/bin/bash
#
# new-show.sh - Create a new show folder with all required files
#
# Usage: ./new-show.sh "Show Name"
#
# This script creates a new show folder under ./Shows with:
#   - show_bible.md (template for show's creative guidelines)
#   - creative_prompt.md (template for sketch ideas)
#   - write.sh (script to run the writing system)
#   - output/ (folder for finished scripts)
#

set -e

# Check for required argument
if [ -z "$1" ]; then
    echo "Error: Show name is required"
    echo ""
    echo "Usage: ./new-show.sh \"Show Name\""
    echo ""
    echo "Example: ./new-show.sh \"Office Chaos\""
    exit 1
fi

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Sanitize the show name: lowercase and replace spaces with underscores
SHOW_NAME="$1"
SANITIZED_NAME=$(echo "$SHOW_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '_' | tr -cd '[:alnum:]_')

# Define paths
SHOWS_DIR="$SCRIPT_DIR/Shows"
SHOW_DIR="$SHOWS_DIR/$SANITIZED_NAME"
TEMPLATES_DIR="$SCRIPT_DIR/templates"

# Check if show already exists
if [ -d "$SHOW_DIR" ]; then
    echo "Error: Show '$SANITIZED_NAME' already exists at $SHOW_DIR"
    exit 1
fi

# Create the show directory structure
echo "Creating show: $SHOW_NAME"
echo "Folder name: $SANITIZED_NAME"
echo ""

mkdir -p "$SHOW_DIR/output"

# Copy template files
cp "$TEMPLATES_DIR/show_bible_template.md" "$SHOW_DIR/show_bible.md"
cp "$TEMPLATES_DIR/creative_prompt_template.md" "$SHOW_DIR/creative_prompt.md"
cp "$TEMPLATES_DIR/write_template.sh" "$SHOW_DIR/write.sh"

# Make write.sh executable
chmod +x "$SHOW_DIR/write.sh"

# Replace placeholder in files with actual show name
# Use portable sed syntax that works on both macOS and Linux
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS requires empty string argument for in-place edit
    sed -i "" "s/{{SHOW_NAME}}/$SHOW_NAME/g" "$SHOW_DIR/show_bible.md"
    sed -i "" "s/{{SHOW_NAME}}/$SHOW_NAME/g" "$SHOW_DIR/write.sh"
    sed -i "" "s/{{SANITIZED_NAME}}/$SANITIZED_NAME/g" "$SHOW_DIR/write.sh"
else
    # Linux uses -i without argument
    sed -i "s/{{SHOW_NAME}}/$SHOW_NAME/g" "$SHOW_DIR/show_bible.md"
    sed -i "s/{{SHOW_NAME}}/$SHOW_NAME/g" "$SHOW_DIR/write.sh"
    sed -i "s/{{SANITIZED_NAME}}/$SANITIZED_NAME/g" "$SHOW_DIR/write.sh"
fi

echo "Show created successfully!"
echo ""
echo "Your show folder: $SHOW_DIR"
echo ""
echo "Next steps:"
echo "  1. Edit show_bible.md to define your show's style and guidelines"
echo "  2. Edit creative_prompt.md with your first sketch idea"
echo "  3. Run ./write.sh to start the AI writing process"
echo ""
echo "For help with write.sh options: ./write.sh --help"
echo ""
