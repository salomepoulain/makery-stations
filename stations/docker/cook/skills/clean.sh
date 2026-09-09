#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/../personality.sh"

PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
DOCKER_DIR="$PROJECT_ROOT/.docker"
COMPOSE_FILE="$DOCKER_DIR/compose.yaml"

if [ ! -f "$COMPOSE_FILE" ]; then
	SAY "No .docker/compose.yaml found. Nothing to clean."
	exit 0
fi

SAY "Stopping compose services and removing local image"
docker compose -f "$COMPOSE_FILE" down --remove-orphans --rmi local
SAY "Docker compose artifacts cleaned"
