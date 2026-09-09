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
PANTRY_DIR="$STATION_DIR/workbench/pantry"
DOCKER_COPY_DIR="$PANTRY_DIR/docker-copy"
DOCKER_DIR="$PROJECT_ROOT/.docker"

SAY "Setting up $COOK_NAME station"

if [ ! -d "$DOCKER_COPY_DIR" ]; then
	SAY "Missing pantry template directory: $DOCKER_COPY_DIR"
	exit 1
fi

mkdir -p "$PROJECT_ROOT/.docker"

copy_if_missing() {
	local src="$1"
	local dst="$2"
	if [ -f "$dst" ]; then
		SAY "$(basename "$dst") already exists, skipping"
		return 0
	fi
	cp "$src" "$dst"
	SAY "Created ${dst#$PROJECT_ROOT/}"
}

copy_if_missing "$DOCKER_COPY_DIR/.docker/Dockerfile" "$PROJECT_ROOT/.docker/Dockerfile"
copy_if_missing "$DOCKER_COPY_DIR/.docker/apt-packages.txt" "$PROJECT_ROOT/.docker/apt-packages.txt"
copy_if_missing "$DOCKER_COPY_DIR/.docker/install-omz-extensions.sh" "$PROJECT_ROOT/.docker/install-omz-extensions.sh"
copy_if_missing "$DOCKER_COPY_DIR/.docker/compose.yaml" "$PROJECT_ROOT/.docker/compose.yaml"
copy_if_missing "$DOCKER_COPY_DIR/.docker/entrypoint.sh" "$PROJECT_ROOT/.docker/entrypoint.sh"
copy_if_missing "$DOCKER_COPY_DIR/.docker/required-env.example" "$PROJECT_ROOT/.docker/required-env.example"
copy_if_missing "$DOCKER_COPY_DIR/.dockerignore" "$PROJECT_ROOT/.dockerignore"
chmod +x "$PROJECT_ROOT/.docker/entrypoint.sh"
chmod +x "$PROJECT_ROOT/.docker/install-omz-extensions.sh" 2>/dev/null || true

if [ -d "$DOCKER_COPY_DIR/.docker/shell" ]; then
	mkdir -p "$DOCKER_DIR/shell"
	while IFS= read -r -d '' src; do
		rel="${src#$DOCKER_COPY_DIR/.docker/shell/}"
		dst="$DOCKER_DIR/shell/$rel"
		dst_dir="$(dirname "$dst")"
		mkdir -p "$dst_dir"
		if [ -f "$dst" ]; then
			continue
		fi
		cp "$src" "$dst"
		SAY "Added shell template file .docker/shell/$rel"
	done < <(find "$DOCKER_COPY_DIR/.docker/shell" -type f -print0)
else
	SAY "No docker template shell folder found, skipping shell config seed"
fi

SAY "Docker station init complete"

# Automatically open the configured shell on first hire when interactive.
if [ -t 0 ] && [ -t 1 ] && [ "${BAKE_DOCKER_NO_AUTO_SHELL:-0}" != "1" ]; then
	SAY "Launching docker shell with your .docker/shell config"
	exec "$STATION_DIR/cook/skills/shell.sh"
fi

SAY "Auto-shell skipped (non-interactive or BAKE_DOCKER_NO_AUTO_SHELL=1)"
SAY "Run: bake docker run"
