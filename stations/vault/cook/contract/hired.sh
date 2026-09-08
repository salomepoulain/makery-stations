#!/bin/bash
# ============================================================================
#  LINE COOK CONTRACT: HIRED (Setup Script)
# ============================================================================
# This script is executed exactly once when the Head Chef hires this Line Cook
# using `bake first <this_cook>`.

source "$(dirname "${BASH_SOURCE[0]}")/../personality.sh"

# Core directories
PROJECT_ROOT="${PWD}"
STATION_DIR="$(dirname "${BASH_SOURCE[0]}")/../.."
PANTRY_DIR="$STATION_DIR/workbench/pantry"
VAULT_DIR="$PROJECT_ROOT/.vault"

SAY "Setting up $COOK_NAME station"

if [ -d "$VAULT_DIR" ]; then
	SAY ".vault already exists here, skipping"
else
	# Default prefix: leading alnum run of the project folder name, lowercased
	# (e.g. "ML4QS-tentamen" -> "ml4qs"). Collision-proofing for [[wikilinks]]
	# if this vault ever merges into a larger multi-project vault.
	FOLDER_NAME="$(basename "$PROJECT_ROOT")"
	DEFAULT_PREFIX="$(echo "$FOLDER_NAME" | tr '[:upper:]' '[:lower:]' | sed -E 's/^([a-z0-9]+).*/\1/')"
	[ -z "$DEFAULT_PREFIX" ] && DEFAULT_PREFIX="vault"

	SAY "Every note gets prefixed so [[wikilinks]] never collide across projects"
	echo -ne "  Vault prefix [$DEFAULT_PREFIX]: "
	read -r PREFIX
	PREFIX="${PREFIX:-$DEFAULT_PREFIX}"
	PREFIX="$(echo "$PREFIX" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+|-+$//g')"
	[ -z "$PREFIX" ] && PREFIX="vault"

	SAY "Scaffolding .vault with prefix '$PREFIX'"
	cp -r "$PANTRY_DIR/vault" "$VAULT_DIR"

	mv "$VAULT_DIR/PREFIX-schema.md" "$VAULT_DIR/${PREFIX}-schema.md"
	mv "$VAULT_DIR/PREFIX-index.md" "$VAULT_DIR/${PREFIX}-index.md"
	mv "$VAULT_DIR/PREFIX-log.md" "$VAULT_DIR/${PREFIX}-log.md"

	find "$VAULT_DIR" -name "*.md" -exec sed -i.bak "s/{{PREFIX}}/${PREFIX}/g" {} \;
	find "$VAULT_DIR" -name "*.bak" -delete

	SAY "Done: .vault/raw, .vault/wiki/{summaries,atomic,maps}, and ${PREFIX}-{schema,index,log}.md"
fi
