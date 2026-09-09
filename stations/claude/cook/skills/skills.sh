#!/usr/bin/env bash
# skills.sh: Deploy/sync skills, commands, and the statusline script from the
# pantry into this project's .claude/. Runs automatically on hire, but is
# also safe to re-run any time via `bake call s=claude d=skills` to pull in
# kitchen updates without a full re-hire.
# shellcheck disable=SC2034

source "$(dirname "${BASH_SOURCE[0]}")/../personality.sh"

find_project_root() {
    local current="$PWD"
    while [[ "$current" != "/" ]]; do
        if [[ -d "$current/.makery" ]]; then
            echo "$current"
            return 0
        fi
        current=$(dirname "$current")
    done
    return 1
}

PROJECT_ROOT=$(find_project_root)
STATION_DIR="$(dirname "${BASH_SOURCE[0]}")/../.."
PANTRY_DIR="$STATION_DIR/workbench/pantry"
CLAUDE_DIR_PATH="$PROJECT_ROOT/.claude"

mkdir -p "$CLAUDE_DIR_PATH"

if [ -d "$PANTRY_DIR/skills" ]; then
	SAY "Syncing skills..."
	cp -r "$PANTRY_DIR/skills" "$CLAUDE_DIR_PATH"
fi

if [ -d "$PANTRY_DIR/commands" ]; then
	SAY "Syncing commands..."
	cp -r "$PANTRY_DIR/commands" "$CLAUDE_DIR_PATH"
fi

if [ -f "$PANTRY_DIR/statusline.sh" ]; then
	SAY "Syncing statusline..."
	cp "$PANTRY_DIR/statusline.sh" "$CLAUDE_DIR_PATH/statusline.sh"
	chmod +x "$CLAUDE_DIR_PATH/statusline.sh"
fi

SAY "Skills sync complete"
