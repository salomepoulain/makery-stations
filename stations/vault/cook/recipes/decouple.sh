#!/usr/bin/env bash
# ============================================================================
#  RECIPE: DECOUPLE (Undo `permanent`: relink .vault to this project's own stash)
# ============================================================================
# Points this project's .vault back at its own stashed copy in .shadow/projects/
# instead of the shared permavault. Only ever repoints the symlink, never
# touches files, so it can't lose content or create permavault collisions.
# Usage: bake call s=vault d=decouple

source "$(dirname "${BASH_SOURCE[0]}")/../personality.sh"
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

PROJECT_ROOT=$(find_project_root) || { SAY "Error: .makery folder not found"; exit 1; }
VAULT_DIR="$PROJECT_ROOT/.vault"
STASH_DIR="${MAKERY_SHADOW_DIR:-$HOME/.shadow/projects}/$(basename "$PROJECT_ROOT")/.vault"

if [ ! -L "$VAULT_DIR" ]; then
	SAY ".vault isn't a symlink here, nothing to decouple."
	exit 0
fi

TARGET_REAL="$(cd "$VAULT_DIR" 2>/dev/null && pwd -P)"
PERMA_REAL="$(cd "$PERMA_DIR" 2>/dev/null && pwd -P)"

if [ "$TARGET_REAL" != "$PERMA_REAL" ]; then
	SAY ".vault isn't linked to the permavault, nothing to decouple."
	exit 0
fi

if [ ! -d "$STASH_DIR" ]; then
	SAY "! No stashed copy at $STASH_DIR to relink to."
	SAY "This project's .vault was likely merged straight from a real local directory"
	SAY "(not a stash) when 'permanent' ran, so its original content only survives"
	SAY "inside the permavault (prefixed, under raw/ and wiki/), nothing to relink here."
	exit 1
fi

rm "$VAULT_DIR"
ln -s "$STASH_DIR" "$VAULT_DIR"
SAY "+ .vault decoupled: now linked to this project's own stash: $STASH_DIR"
