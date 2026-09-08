#!/usr/bin/env bash
# Yolo commit: writes the message, then commits and pushes under your own
# git/gh credentials. Never attributes the commit to Claude.
set -e

source "$(dirname "${BASH_SOURCE[0]}")/../personality.sh"

find_project_root() {
    local current="$PWD"
    while [[ "$current" != "/" ]]; do
        if [[ -d "$current/.makery" ]]; then
            echo "$current"
            return 0
        fi
        current=$(dirname "$current")
    done
    return 1
}

command -v git    &>/dev/null || { SAY "git not installed"; exit 1; }
command -v claude &>/dev/null || { SAY "claude not installed: https://claude.ai/code"; exit 1; }
export GIT_PAGER=cat

PAID_MODE=false
[ "$1" = "paid" ] && PAID_MODE=true

SAY "Lemme just duplicate real quick"

if [ "$PAID_MODE" = false ]; then
  [ -z "${OPENROUTER_API_KEY:-}" ] && { SAY "OPENROUTER_API_KEY not set"; exit 1; }

  PROJECT_ROOT=$(find_project_root)
  TEMP_CLAUDE_DIR="$PROJECT_ROOT/.claude-free/.claude"
  mkdir -p "$TEMP_CLAUDE_DIR"

  jq -n \
    --arg key "$OPENROUTER_API_KEY" \
    '{
      "model": "openrouter/owl-alpha",
      "env": {
        "ANTHROPIC_BASE_URL": "https://openrouter.ai/api/v1",
        "ANTHROPIC_AUTH_TOKEN": $key
      }
    }' > "$TEMP_CLAUDE_DIR/settings.local.json"

  export CLAUDE_DIR="$TEMP_CLAUDE_DIR"
  CLEANUP_NEEDED=true
else
  CLEANUP_NEEDED=false
fi

cleanup() {
  if [ "$CLEANUP_NEEDED" = true ] && [ -n "${TEMP_CLAUDE_DIR:-}" ]; then
    rm -rf "$(dirname "$TEMP_CLAUDE_DIR")" 2>/dev/null || true
  fi
}
trap cleanup EXIT

[ -z "$(git status --porcelain)" ] && { SAY "Nothing to commit"; exit 0; }

git add -A 2>&1 | grep -v "\.makery" || true
DIFF=$(git diff --cached)
DIFF_LINES=$(echo "$DIFF" | wc -l)
[ "$DIFF_LINES" -gt 500 ] && DIFF="$(echo "$DIFF" | head -500)\n\n...(truncated)"


SAY "Asking the other agent to write the message"

COMMIT_MSG=$(claude -p "Write a git commit message for the following diff.

Format EXACTLY like this. No extra text, no markdown fences:

<subject line: max 72 chars, imperative mood, e.g. 'Add exploratory analysis for task 1a'>

- <change 1: one concrete thing that changed>
- <change 2: one concrete thing that changed>
- <change 3: ...>

Rules:
- Subject line on the first line, then a blank line, then bullet points.
- Each bullet describes ONE concrete change (file added/removed, function changed, behaviour fixed, config updated).
- Group related bullets together if there are many changes.
- Be specific. Name files, functions, or settings where relevant.
- No vague bullets like 'various improvements' or 'minor fixes'.
- Output ONLY the commit message. No quotes, no backticks, no commentary.

Diff:
$DIFF" 2>/dev/null)

# Strip any attribution trailers the subprocess may have added on its own -
# this recipe never commits as Claude, only the human does.
COMMIT_MSG=$(echo "$COMMIT_MSG" | grep -viE "^(Co-Authored-By:|Claude-Session:)")

SAY "This is the message"
echo "$COMMIT_MSG"

echo ""

git commit -m "$COMMIT_MSG"

if git remote | grep -q .; then
  BRANCH=$(git rev-parse --abbrev-ref HEAD)
  git push -u origin "$BRANCH"
  SAY "Done"
else
  SAY "No remote. Committed locally"
fi
