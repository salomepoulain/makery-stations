#!/bin/bash
# ============================================================================
#  LINE COOK CONTRACT: HIRED (Setup Script)
# ============================================================================
# Copies the station's skills into .agents/skills/, where GitHub Copilot in
# VS Code (agent mode) picks them up. Only local-only skills ship here: none of
# them download, install or post anything, so the station works without
# internet. Hiring again refreshes them; skills of your own in .agents/skills/
# with other names are left alone.
#
# It also writes AGENTS.md in the project root, which Copilot reads on every
# request: the confidential-work rules plus the writing and engineering style.
# A project's own AGENTS.md (the team's) is never touched: only a file that
# starts with the station's marker line gets written or refreshed.

source "$(dirname "${BASH_SOURCE[0]}")/../personality.sh"

PROJECT_ROOT="${PWD}"
STATION_DIR="$(dirname "${BASH_SOURCE[0]}")/../.."
SKILLS_SRC="$STATION_DIR/workbench/pantry/skills"
SKILLS_DST="$PROJECT_ROOT/.agents/skills"
AGENTS_SRC="$STATION_DIR/workbench/pantry/AGENTS.md"
AGENTS_DST="$PROJECT_ROOT/AGENTS.md"
AGENTS_MARK="<!-- copilot-station: AGENTS.md -->"

# --- Skills ---
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

# --- AGENTS.md ---
if [ -e "$AGENTS_DST" ] && ! head -1 "$AGENTS_DST" | grep -qF "$AGENTS_MARK"; then
    SAY "This project already has its own AGENTS.md, so it's left alone."
    SAY "The confidential-work rules are in .makery/stations/copilot/workbench/pantry/AGENTS.md if you want to add them yourself."
else
    cp "$AGENTS_SRC" "$AGENTS_DST"
    SAY "Wrote AGENTS.md: Copilot reads it on every request (confidential-work rules + style)."
    if [ -f "$PROJECT_ROOT/.gitignore" ]; then
        grep -qx 'AGENTS.md' "$PROJECT_ROOT/.gitignore" || echo 'AGENTS.md' >> "$PROJECT_ROOT/.gitignore"
    else
        SAY "No .gitignore here, so AGENTS.md isn't ignored by git. Don't commit it."
    fi
fi
