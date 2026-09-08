#!/usr/bin/env bash
# ============================================================================
#  RECIPE: PERMANENT (Live-link .vault straight to the permanent vault)
# ============================================================================
# Replaces this project's .vault with a symlink directly into ~/.shadow/.vault
# (merging any existing local content in first). After this, working inside
# <project>/.vault IS working inside the permavault.
# Usage: bake call s=vault d=permanent

source "$(dirname "${BASH_SOURCE[0]}")/../personality.sh"
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

PROJECT_ROOT=$(find_project_root) || { SAY "Error: .makery folder not found"; exit 1; }
VAULT_DIR="$PROJECT_ROOT/.vault"

init_permavault
PERMA_REAL="$(cd "$PERMA_DIR" && pwd -P)"

if [ -L "$VAULT_DIR" ]; then
	TARGET_REAL="$(cd "$VAULT_DIR" 2>/dev/null && pwd -P)"
	if [ "$TARGET_REAL" = "$PERMA_REAL" ]; then
		SAY ".vault is already permanently linked to $PERMA_DIR"
		exit 0
	fi

	SAY "Merging existing stashed .vault before permanently linking..."
	merge_vault_into_perma "$TARGET_REAL" "$(basename "$PROJECT_ROOT")"
	rm "$VAULT_DIR"

elif [ -d "$VAULT_DIR" ]; then
	echo -ne "  ${YELLOW}⚠${NC} .vault has real content here. Merge it into the permavault and replace it with a live link? (y/N): "
	read -r response
	if [[ ! "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
		SAY "Left untouched."
		exit 0
	fi
	merge_vault_into_perma "$VAULT_DIR" "$(basename "$PROJECT_ROOT")"
	rm -rf "$VAULT_DIR"
fi

ln -s "$PERMA_DIR" "$VAULT_DIR"
SAY "+ .vault now permanently linked to $PERMA_DIR"
