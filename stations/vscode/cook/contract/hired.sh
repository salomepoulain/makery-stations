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

set -euo pipefail

PROJECT_ROOT="${PWD}"
STATION_DIR="$(dirname "${BASH_SOURCE[0]}")/../.."


SAY "Setting up $COOK_NAME station"
SAY "I dont do anything tho. Pantry files here are for manual reference, not auto-deployed"
