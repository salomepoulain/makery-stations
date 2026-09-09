#!/usr/bin/env bash
# Toggle permissions.blockReadsOutsideWorkingDirectories in settings.local.json
# Usage: bake call s=claude d=auto

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
CLAUDE_DIR="${CLAUDE_DIR:-${PROJECT_ROOT}/.claude}"
SETTINGS_FILE="$CLAUDE_DIR/settings.local.json"

command -v jq &>/dev/null || { SAY "jq not installed"; exit 1; }

if [ ! -f "$SETTINGS_FILE" ]; then
  SAY "No settings.local.json found at $SETTINGS_FILE"
  exit 1
fi

current=$(jq -r '.permissions.blockReadsOutsideWorkingDirectories // false' "$SETTINGS_FILE")

if [ "$current" = "true" ]; then
  new_value=false
  label="OFF"
else
  new_value=true
  label="ON"
fi

tmp_file=$(mktemp)
jq --argjson v "$new_value" '.permissions.blockReadsOutsideWorkingDirectories = $v' "$SETTINGS_FILE" > "$tmp_file" && mv "$tmp_file" "$SETTINGS_FILE"

SAY "blockReadsOutsideWorkingDirectories is now $label"
if [ "$new_value" = false ]; then
  SAY "Any command can now read files outside the project and additionalDirectories without a proceed prompt. Reload (/hooks or restart) to pick it up."
else
  SAY "Read protection restored. Reload (/hooks or restart) to pick it up."
fi
