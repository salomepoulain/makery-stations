#!/usr/bin/env bash
# ============================================================================
#  LINE COOK CONTRACT: FIRED (Teardown Script)
# ============================================================================
# This script is executed exactly once when the Head Chef fires this Line Cook
# using `bake burnt <this_cook>`.
#
# Use this script to unregister system-level changes (like Jupyter kernels)
# that shouldn't be left behind when the station is destroyed.
# You can speak during teardown using SAY:
#   SAY "Packing my knives and cleaning out my locker..."

source "$(dirname "${BASH_SOURCE[0]}")/../personality.sh"

# Core directories
REPOSITORY="$(git rev-parse --show-toplevel 2>/dev/null)"
STATION_DIR="$(dirname "${BASH_SOURCE[0]}")/../.."
PANTRY_DIR="$STATION_DIR/workbench/pantry"

SAY "Dang im fired... ight imma head out and pack my belongings"

# Clean up claude's workspace
rm -rf "$REPOSITORY/CLAUDE.md"
rm -rf "$REPOSITORY/.claude"
