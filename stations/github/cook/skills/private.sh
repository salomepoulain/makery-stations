#!/usr/bin/env bash
set -e

source "$(dirname "${BASH_SOURCE[0]}")/../personality.sh"

# This pushes or publishes, so it needs a person at a real terminal: never an
# agent's command or a script piping in answers (see the makery-bakery README).
if [ ! -t 0 ] || [ ! -t 1 ]; then
    SAY "This needs a person at a real terminal. Nothing was changed."
    exit 1
fi

find_project_root() {
    local current="$PWD"
    while [[ "$current" != "/" ]]; do
        [[ -d "$current/.makery" ]] && echo "$current" && return
        current=$(dirname "$current")
    done
    return 1
}

PROJECT_ROOT=$(find_project_root) || { SAY "No .makery found. Are you inside a makery project?"; exit 1; }

git -C "$PROJECT_ROOT" remote get-url origin &>/dev/null || { SAY "No remote 'origin' set. Run: bake call s=github d=repo"; exit 1; }

REMOTE_URL=$(git -C "$PROJECT_ROOT" remote get-url origin)
REPO_NAME=$(basename "$REMOTE_URL" .git)

echo ""
echo -e "  Repo      : ${BOLD}$REPO_NAME${NC}"
echo -e "  New state : ${BOLD}private${NC}"
echo ""
read -rp "  Make private? [y/N]: " confirm
[[ "$confirm" =~ ^[Yy]$ ]] || { SAY "Aborted"; exit 0; }

gh repo edit --visibility private
SAY "$REPO_NAME is now private"
