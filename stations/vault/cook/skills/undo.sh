#!/usr/bin/env bash
# ============================================================================
#  RECIPE: UNDO (Undo the most recent perma merge)
# ============================================================================
# Deletes exactly the files the last merge added, per ~/.shadow/.vault's own
# _merges.md log. Usage: bake call s=vault d=undo

source "$(dirname "${BASH_SOURCE[0]}")/../personality.sh"
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

find_project_root >/dev/null || { SAY "Error: .makery folder not found"; exit 1; }

undo_last_merge
