#!/usr/bin/env bash
set -e

source "$(dirname "${BASH_SOURCE[0]}")/../personality.sh"
source "$(dirname "${BASH_SOURCE[0]}")/../topics.sh"

find_project_root() {
    local current="$PWD"
    while [[ "$current" != "/" ]]; do
        [[ -d "$current/.makery" ]] && echo "$current" && return
        current=$(dirname "$current")
    done
    return 1
}

PROJECT_ROOT=$(find_project_root) || { SAY "No .makery found. Are you inside a makery project?"; exit 1; }

# Check PROJECT_ROOT is a repo's *top level*, not just nested inside some
# ancestor repo (e.g. a loose parent directory that is itself a git repo).
PROJECT_ROOT_REAL=$(cd "$PROJECT_ROOT" && pwd -P)
if [[ "$(git -C "$PROJECT_ROOT" rev-parse --show-toplevel 2>/dev/null)" != "$PROJECT_ROOT_REAL" ]]; then
    git -C "$PROJECT_ROOT" init --quiet
    SAY "Initialized git repo"
fi

if ! git -C "$PROJECT_ROOT" rev-parse HEAD &>/dev/null; then
    git -C "$PROJECT_ROOT" add -A
    git -C "$PROJECT_ROOT" commit -m "initial commit" --quiet
    SAY "Initial commit created"
fi

gh auth status &>/dev/null || { SAY "Not logged in to GitHub. Run: gh auth login"; exit 1; }

if git -C "$PROJECT_ROOT" remote get-url origin &>/dev/null; then
    SAY "Remote already set: $(git -C "$PROJECT_ROOT" remote get-url origin)"
    exit 0
fi

REPO_NAME=$(basename "$PROJECT_ROOT")

echo ""
echo -e "  Repo name : ${BOLD}$REPO_NAME${NC}"
echo -e "  Visibility: ${BOLD}private${NC}"
echo ""

gh repo create "$REPO_NAME" --private --source="$PROJECT_ROOT" --remote=origin --push

REPO_URL=$(gh repo view "$REPO_NAME" --json url -q .url 2>/dev/null || echo "")
SAY "Done: $REPO_URL"

prompt_github_topics
