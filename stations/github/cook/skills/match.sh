#!/usr/bin/env bash
# Opposite of repo.sh: instead of pushing what's here up as a new repo,
# look for an existing repo (under your own GitHub account) named exactly
# like this folder, and pull it down into it.
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

PROJECT_ROOT=$(find_project_root) || { SAY "No .makery found. Are you inside a makery project?"; exit 1; }
PROJECT_NAME=$(basename "$PROJECT_ROOT")

gh auth status &>/dev/null || { SAY "Not logged in to GitHub. Run: gh auth login"; exit 1; }

# --- already set up? ---
if git -C "$PROJECT_ROOT" rev-parse --show-toplevel &>/dev/null; then
    EXISTING_ORIGIN=$(git -C "$PROJECT_ROOT" remote get-url origin 2>/dev/null || echo "")
    if [ -n "$EXISTING_ORIGIN" ]; then
        SAY "Already set up: $EXISTING_ORIGIN"
        exit 0
    fi
fi

CURRENT_USER=$(gh api user --jq '.login')

REPO_URL=$(gh repo view "$CURRENT_USER/$PROJECT_NAME" --json url -q .url 2>/dev/null || echo "")
[ -n "$REPO_URL" ] || { SAY "No repo named '$PROJECT_NAME' found under $CURRENT_USER"; exit 1; }

DEFAULT_BRANCH=$(gh repo view "$CURRENT_USER/$PROJECT_NAME" --json defaultBranchRef -q .defaultBranchRef.name)

SAY "Found $CURRENT_USER/$PROJECT_NAME - pulling it into this folder..."

cd "$PROJECT_ROOT" || exit 1

git rev-parse --show-toplevel &>/dev/null || git init --quiet
git remote add origin "$REPO_URL" 2>/dev/null || git remote set-url origin "$REPO_URL"
git fetch origin --quiet
git checkout -b "$DEFAULT_BRANCH" "origin/$DEFAULT_BRANCH" 2>/dev/null || git checkout "$DEFAULT_BRANCH"

SAY "Done: $REPO_URL ($DEFAULT_BRANCH)"
