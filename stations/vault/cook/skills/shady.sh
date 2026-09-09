#!/usr/bin/env bash
# ============================================================================
#  RECIPE: SHADY (Stash .vault into this project's own __stash__)
# ============================================================================
# Standalone, scoped version of the headchef's generic `bake shady`. Moves
# just .vault into ~/.shadow/projects/<project>/ and leaves a symlink
# behind. Usage: bake call s=vault d=shady

source "$(dirname "${BASH_SOURCE[0]}")/../personality.sh"

find_project_root() {
	local current="$PWD"
	while [[ "$current" != "/" ]]; do
		[[ -d "$current/.makery" ]] && { echo "$current"; return 0; }
		current=$(dirname "$current")
	done
	return 1
}

PROJECT_ROOT=$(find_project_root) || { SAY "Error: .makery folder not found"; exit 1; }
cd "$PROJECT_ROOT" || exit 1

TARGET=".vault"
SHADOW_DIR="${MAKERY_SHADOW_DIR:-$HOME/.shadow/projects}/$(basename "$PROJECT_ROOT")"

if [ ! -e "$TARGET" ]; then
	SAY "No .vault here yet, nothing to stash. Run 'bake first vault' first."
	exit 0
fi

if [ -L "$TARGET" ]; then
	SAY ".vault is already stashed (or permanently linked)."
	exit 0
fi

mkdir -p "$SHADOW_DIR"

if [ -e "$SHADOW_DIR/$TARGET" ]; then
	SAY "Both local and .shadow/ already have .vault, skipping, resolve by hand."
	exit 0
fi

if [ ! -e "__stash__" ]; then
	ln -s "$SHADOW_DIR" "__stash__"
	SAY "+ __stash__ now lives in .shadow/"
fi

mv "$TARGET" "$SHADOW_DIR/$TARGET"
ln -s "$SHADOW_DIR/$TARGET" "$TARGET"
SAY "+ Stashed: .vault -> __stash__/.vault"
