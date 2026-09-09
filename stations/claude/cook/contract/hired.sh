#!/usr/bin/env bash
# ============================================================================
#  LINE COOK CONTRACT: HIRED (Setup Script)
# ============================================================================
# This script is executed exactly once when the Head Chef hires this Line Cook
# using `bake first <this_cook>`.
# shellcheck disable=SC2034

source "$(dirname "${BASH_SOURCE[0]}")/../personality.sh"

# Core directories
PROJECT_ROOT="${PWD}"
STATION_DIR="$(dirname "${BASH_SOURCE[0]}")/../.."
PANTRY_DIR="$STATION_DIR/workbench/pantry"


SAY "Setting up $COOK_NAME station"

SAY "Adding CLAUDE.local.md and creating .claude folder at $PROJECT_ROOT"

CLAUDE_MD_PATH="$PROJECT_ROOT/CLAUDE.local.md"
CLAUDE_DIR_PATH="$PROJECT_ROOT/.claude"

# Create the .claude directory if missing
if [ ! -d "$CLAUDE_DIR_PATH" ]; then
	mkdir -p "$CLAUDE_DIR_PATH"
	SAY "Created .claude directory"
else
	SAY ".claude directory already exists, skipping"
fi


# Add docs to .claude
SAY "Adding docs to .claude"
cp -r "$PANTRY_DIR/docs" "$CLAUDE_DIR_PATH"

# Deploy skills, commands, and the statusline script (same logic as
# `bake call s=claude d=skills`, callable again standalone later)
"$STATION_DIR/cook/skills/skills.sh"


# Merge JSON plugins from pantry/settings into settings.local.json
SETTINGS_FILE="$CLAUDE_DIR_PATH/settings.local.json"

# List of plugin files to include (order matters for merging)
# Add plugin settings here to include them in settings.local.json
SETTINGS_PLUGINS=("permissions" "statusline" "mcp" "skilloverrides" "automode")

if [ ${#SETTINGS_PLUGINS[@]} -gt 0 ]; then
	SAY "Merging settings..."

	# Start with empty JSON object only if nothing's there yet. This file may
	# already carry keys set outside this merge (e.g. illegal.sh's
	# autoMemoryDirectory, a hand-added statusLine); don't clobber them on a
	# re-run.
	[ -f "$SETTINGS_FILE" ] || echo '{}' > "$SETTINGS_FILE"

	# Process each plugin in the list
	for plugin_name in "${SETTINGS_PLUGINS[@]}"; do
		plugin="$PANTRY_DIR/settings/${plugin_name}.json"
		if [ -f "$plugin" ]; then
			SAY "  Injecting: $plugin_name"
			if command -v jq &> /dev/null; then
				jq -s '.[0] * .[1]' "$SETTINGS_FILE" "$plugin" > "$SETTINGS_FILE.tmp" && mv "$SETTINGS_FILE.tmp" "$SETTINGS_FILE"
			else
				cp "$plugin" "$SETTINGS_FILE"
			fi
		else
			SAY "  Warning: Plugin not found: $plugin_name"
		fi
	done
fi

SAY "Setup additions complete"


# Add CLAUDE.local.md
if [ ! -f "$CLAUDE_MD_PATH" ]; then
	SAY "Adding CLAUDE.local.md"
	cp -r "$PANTRY_DIR/CLAUDE.local.md" "$CLAUDE_MD_PATH"
else
	SAY "CLAUDE.local.md already exists, skipping"
fi
