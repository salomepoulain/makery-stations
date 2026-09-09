#!/usr/bin/env bash
# ============================================================================
#  CLUSTER: SHADY-SYNC (continuous __stash__/.shadow sync to a remote host)
# ============================================================================
# Keeps this project's .shadow/projects/<name>/ folder (everything `bake
# shady` stashed - gitignored/contraband files, symlinked back locally as
# __stash__) in continuous two-way sync with the same path on a remote
# host, via Mutagen. Syncs the real .shadow path directly, not through
# the __stash__ symlink. Mutagen self-deploys its own agent on the
# remote on first sync, and creates missing directories on both ends.
#
# This can pull in a lot more than __sync__/ does - whatever `bake shady`
# has stashed for this project, including any bulk data that ended up
# there. Use `bake call s=cluster d=sync` instead if you just want a
# small, deliberate, drag-and-drop folder synced.
#
# Usage: bake call s=cluster d=shady-sync [ssh-host-alias]
# With no host given, picks interactively from ~/.ssh/config Host entries.

set -e

source "$(dirname "${BASH_SOURCE[0]}")/../personality.sh"

find_project_root() {
    local current="$PWD"
    while [[ "$current" != "/" ]]; do
        [[ -d "$current/.makery" ]] && echo "$current" && return
        current=$(dirname "$current")
    done
    return 1
}

HOST="$1"

# --- pick a host interactively if none given ---
if [ -z "$HOST" ]; then
    HOSTS=()
    if [ -f "$HOME/.ssh/config" ]; then
        while IFS= read -r h || [ -n "$h" ]; do
            HOSTS+=("$h")
        done < <(grep -i "^Host " "$HOME/.ssh/config" | awk '{print $2}' | grep -v '\*' | sort -u)
    fi
    if [ ${#HOSTS[@]} -eq 0 ]; then
        SAY "No Host entries found in ~/.ssh/config - pass one directly: bake call s=cluster d=shady-sync <host>"
        exit 1
    fi
    SAY "Pick a cluster to sync with:"
    i=1
    for h in "${HOSTS[@]}"; do
        echo "  $i) $h"
        i=$((i + 1))
    done
    echo -ne "  > "
    read -r choice
    if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le "${#HOSTS[@]}" ]; then
        HOST="${HOSTS[$((choice - 1))]}"
    fi
    [ -z "$HOST" ] && { SAY "No host chosen, nothing to do."; exit 0; }
fi

PROJECT_ROOT=$(find_project_root) || { SAY "Error: .makery folder not found"; exit 1; }
PROJECT_NAME=$(basename "$PROJECT_ROOT")
SHADOW_DIR="${MAKERY_SHADOW_DIR:-$HOME/.shadow/projects}/$PROJECT_NAME"

[ -d "$SHADOW_DIR" ] || { SAY "No .shadow content yet for this project - run 'bake shady' first."; exit 1; }

BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"

# --- mutagen (no sudo) ---
if ! command -v mutagen >/dev/null 2>&1; then
    SAY "Installing mutagen..."
    ASSET_URL=$(curl -sL https://api.github.com/repos/mutagen-io/mutagen/releases/latest \
        | grep "browser_download_url.*linux_amd64.tar.gz" \
        | cut -d '"' -f 4)
    curl -sL -o /tmp/mutagen.tar.gz "$ASSET_URL"
    tar -xzf /tmp/mutagen.tar.gz -C "$BIN_DIR" mutagen
    rm -f /tmp/mutagen.tar.gz
else
    SAY "mutagen already installed"
fi

if command -v mutagen >/dev/null 2>&1; then
    MUTAGEN="mutagen"
else
    MUTAGEN="$BIN_DIR/mutagen"
fi

"$MUTAGEN" daemon start >/dev/null 2>&1 || true

SESSION_NAME="${PROJECT_NAME}-shady-${HOST}"
REMOTE_PATH="~/.shadow/projects/$PROJECT_NAME"

if "$MUTAGEN" sync list "$SESSION_NAME" >/dev/null 2>&1; then
    SAY "Already syncing '$PROJECT_NAME' shadow with $HOST (session: $SESSION_NAME)"
else
    SAY "Creating sync session $SESSION_NAME: $SHADOW_DIR <-> $HOST:$REMOTE_PATH"
    "$MUTAGEN" sync create --name="$SESSION_NAME" "$SHADOW_DIR" "$HOST:$REMOTE_PATH"
    SAY "Sync running in the background. Once the initial pass finishes, run 'bake shady' on $HOST to reconnect symlinks there."
fi
