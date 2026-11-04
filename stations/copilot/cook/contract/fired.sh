#!/bin/bash
# ============================================================================
#  LINE COOK CONTRACT: FIRED (Teardown Script)
# ============================================================================
# Nothing outside the project to undo. `bake burnt copilot` clears
# .agents/skills itself, because the countertop lists it.

source "$(dirname "${BASH_SOURCE[0]}")/../personality.sh"

SAY "Taking the Copilot skills out of .agents/skills"
