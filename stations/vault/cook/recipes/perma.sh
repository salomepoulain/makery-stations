#!/usr/bin/env bash
# ============================================================================
#  RECIPE: PERMA (Merge .vault into the permanent cross-project vault)
# ============================================================================
# Copies this project's .vault content into ~/.shadow/.vault, leaving this
# project's own .vault untouched. Usage: bake call s=vault d=perma

source "$(dirname "${BASH_SOURCE[0]}")/../personality.sh"
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

PROJECT_ROOT=$(find_project_root) || { SAY "Error: .makery folder not found"; exit 1; }
VAULT_DIR="$PROJECT_ROOT/.vault"

if [ ! -e "$VAULT_DIR" ]; then
	SAY "No .vault here, nothing to merge. Run 'bake first vault' first."
	exit 1
fi

REAL_VAULT_DIR="$(cd "$VAULT_DIR" && pwd -P)"

init_permavault
PERMA_REAL="$(cd "$PERMA_DIR" && pwd -P)"

if [ "$REAL_VAULT_DIR" = "$PERMA_REAL" ]; then
	SAY "This project's .vault already IS the permavault, nothing to merge."
	exit 0
fi

merge_vault_into_perma "$REAL_VAULT_DIR" "$(basename "$PROJECT_ROOT")"
