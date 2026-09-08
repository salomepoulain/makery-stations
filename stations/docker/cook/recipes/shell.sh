#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/../personality.sh"

PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
DOCKER_DIR="$PROJECT_ROOT/.docker"
COMPOSE_FILE="$DOCKER_DIR/compose.yaml"
STATION_DIR="$(dirname "${BASH_SOURCE[0]}")/../.."
IMAGE_TAG="makery-dev-shell:local"

if [ ! -f "$DOCKER_DIR/Dockerfile" ] || [ ! -f "$DOCKER_DIR/entrypoint.sh" ] || [ ! -f "$COMPOSE_FILE" ]; then
	SAY "Docker config missing. Run: bake first docker"
	exit 1
fi

SAY "Opening dev shell from compose service 'dev'"
if ! docker image inspect "$IMAGE_TAG" >/dev/null 2>&1; then
	SAY "Image $IMAGE_TAG not found; building first"
	bash "$STATION_DIR/cook/recipes/build.sh"
fi

exec docker compose -f "$COMPOSE_FILE" run --rm dev
