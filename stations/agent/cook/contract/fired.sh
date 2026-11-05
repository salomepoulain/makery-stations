#!/bin/bash
# ============================================================================
#  LINE COOK CONTRACT: FIRED (Teardown Script)
# ============================================================================
# `bake burnt agent` clears .agents/skills itself, because the countertop
# lists it. AGENTS.md isn't on the countertop (a team's own AGENTS.md must
# never be deleted), so it's removed here, and only if it's the station's.

source "$(dirname "${BASH_SOURCE[0]}")/../personality.sh"

AGENTS_DST="${PWD}/AGENTS.md"
AGENTS_MARK="<!-- agent-station: AGENTS.md -->"
OLD_MARK="<!-- copilot-station: AGENTS.md -->"

SAY "Taking the agent skills out of .agents/skills"
if [ -f "$AGENTS_DST" ] && head -1 "$AGENTS_DST" | grep -qF -e "$AGENTS_MARK" -e "$OLD_MARK"; then
    rm -f "$AGENTS_DST"
    SAY "Removed the station's AGENTS.md"
fi
