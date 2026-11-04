#!/bin/bash
# ============================================================================
#  LINE COOK CONTRACT: HIRED (Setup Script)
# ============================================================================
# Copies the station's skills into .agents/skills/, where GitHub Copilot in
# VS Code (agent mode) picks them up. Only local-only skills ship here: none of
# them download, install or post anything, so the station works without
# internet. Hiring again refreshes them; skills of your own in .agents/skills/
# with other names are left alone.

source "$(dirname "${BASH_SOURCE[0]}")/../personality.sh"

PROJECT_ROOT="${PWD}"
STATION_DIR="$(dirname "${BASH_SOURCE[0]}")/../.."
SKILLS_SRC="$STATION_DIR/workbench/pantry/skills"
SKILLS_DST="$PROJECT_ROOT/.agents/skills"

SAY "Putting Copilot skills in .agents/skills"
mkdir -p "$SKILLS_DST"

count=0
for skill in "$SKILLS_SRC"/*/; do
    name=$(basename "$skill")
    rm -rf "${SKILLS_DST:?}/$name"
    cp -R "$skill" "$SKILLS_DST/$name"
    count=$((count + 1))
done
cp "$SKILLS_SRC/THIRD_PARTY_NOTICES.md" "$SKILLS_DST/"

SAY "$count skills ready. Use them in Copilot Chat in agent mode, or type / to call one by name."
