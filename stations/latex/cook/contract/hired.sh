#!/bin/bash
# ============================================================================
#  LINE COOK CONTRACT: HIRED (Setup Script)
# ============================================================================
# This script is executed exactly once when the Head Chef hires this Line Cook
# using `bake first <this_cook>`.
#
# Use this script to set up local environments, download dependencies, etc.
# You can SAY during setup using SAY (shown with the cook's identity):
#   SAY "Setting up station"

source "$(dirname "${BASH_SOURCE[0]}")/../personality.sh"

# Core directories
PROJECT_ROOT="${PWD}"
STATION_DIR="$(dirname "${BASH_SOURCE[0]}")/../.."
PANTRY_DIR="$STATION_DIR/workbench/pantry"
REPORT_DIR="$PROJECT_ROOT/report"

SAY "Setting up $COOK_NAME station"

# Create the report/ directory if missing
if [ ! -d "$REPORT_DIR" ]; then
	mkdir -p "$REPORT_DIR"
	SAY "Created report/ directory"
else
	SAY "report/ directory already exists, skipping"
fi

# Move writing_guides from the pantry into report/
if [ -d "$PANTRY_DIR/writing_guides" ]; then
	if [ -d "$REPORT_DIR/writing_guides" ]; then
		SAY "writing_guides already exists in report/, skipping"
	else
		mv "$PANTRY_DIR/writing_guides" "$REPORT_DIR/"
		SAY "Moved writing_guides into report/"
	fi
fi
