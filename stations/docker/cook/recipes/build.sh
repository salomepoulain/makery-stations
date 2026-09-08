#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/../personality.sh"

PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
DOCKER_DIR="$PROJECT_ROOT/.docker"
COMPOSE_FILE="$DOCKER_DIR/compose.yaml"
IMAGE_TAG="makery-dev-shell:local"

if [ ! -f "$DOCKER_DIR/Dockerfile" ] || [ ! -f "$COMPOSE_FILE" ]; then
	SAY "Docker config missing. Run: bake first docker"
	exit 1
fi

SAY "Building dev image with classic docker build"
docker build -f "$DOCKER_DIR/Dockerfile" -t "$IMAGE_TAG" "$PROJECT_ROOT"
SAY "Build complete"
