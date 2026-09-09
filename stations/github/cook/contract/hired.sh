#!/bin/bash
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

PROJECT_ROOT=$(find_project_root) || { SAY "No .makery found"; exit 1; }
KITCHEN_DIR="$(dirname "${BASH_SOURCE[0]}")/../../../.."
GITIGNORE="$PROJECT_ROOT/.gitignore"

SAY "Setting up $COOK_NAME station"

# --- 1. Build .gitignore from all stations' countertop ---
# .countertop is the sole source of truth - station authors write it by
# hand (including duplicating anything from .contraband/.dishsoap that
# also needs gitignoring), no automatic union.
# Only fresh-write on first run; if it already exists, append to preserve custom entries
if [ ! -f "$GITIGNORE" ]; then
    > "$GITIGNORE"
fi

collect_gitignore() {
    local file="$1"
    [[ -f "$file" ]] || return
    while IFS= read -r line || [[ -n "$line" ]]; do
        [[ -z "$line" || "$line" == "#"* ]] && continue
        grep -Fxq "$line" "$GITIGNORE" || echo "$line" >> "$GITIGNORE"
    done < "$file"
}

collect_gitignore "$KITCHEN_DIR/.kitchen"
for station_dir in "$KITCHEN_DIR/stations"/*/; do
    collect_gitignore "${station_dir}workbench/.countertop"
done

SAY "Built .gitignore"

# --- 2. Git init ---
# Check PROJECT_ROOT is a repo's *top level*, not just nested inside some
# ancestor repo (e.g. a loose parent directory that is itself a git repo).
PROJECT_ROOT_REAL=$(cd "$PROJECT_ROOT" && pwd -P)
if [[ "$(git -C "$PROJECT_ROOT" rev-parse --show-toplevel 2>/dev/null)" != "$PROJECT_ROOT_REAL" ]]; then
    git -C "$PROJECT_ROOT" init --quiet
    SAY "Initialized git repo"
fi

# --- 3. Initial commit if no commits yet ---
if ! git -C "$PROJECT_ROOT" rev-parse HEAD &>/dev/null; then
    git -C "$PROJECT_ROOT" add -A
    git -C "$PROJECT_ROOT" commit -m "initial commit" --quiet
    SAY "Initial commit created"
fi

# --- 4. GitHub repo creation ---
if ! gh auth status &>/dev/null; then
    SAY "Not logged in to GitHub (run: gh auth login), skipping repo creation"
    exit 0
fi

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
