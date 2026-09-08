#!/usr/bin/env bash
set -euo pipefail

if [ -d /workspace/.docker/shell ]; then
	cp -R /workspace/.docker/shell/. "$HOME/"
fi

exec "$@"
