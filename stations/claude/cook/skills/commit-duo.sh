#!/usr/bin/env bash
# Smart commit: you write the message, Claude reviews it.
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

# Pre-check: pull first?
if git remote | grep -q .; then
  git fetch --quiet 2>/dev/null
  LOCAL=$(git rev-parse @ 2>/dev/null)
  REMOTE=$(git rev-parse @{u} 2>/dev/null || echo "")
  if [ -n "$REMOTE" ] && [ "$LOCAL" != "$REMOTE" ]; then
    BASE=$(git merge-base @ @{u} 2>/dev/null || echo "")
    if [ "$LOCAL" = "$BASE" ]; then
      SAY "Remote has new commits. Pull first"
      exit 1
    fi
  fi
fi

# Stage
SAY "STEP 1: Stage changes"
[ -z "$(git status --porcelain)" ] && { SAY "Nothing to commit"; exit 0; }

git add -A 2>&1 | grep -v "\.makery" || true
SAY "Staged:"
git diff --cached --stat

DIFF=$(git diff --cached)
DIFF_LINES=$(echo "$DIFF" | wc -l)
[ "$DIFF_LINES" -gt 500 ] && DIFF="$(echo "$DIFF" | head -500)\n\n...(truncated)"

# Claude reviews staging
SAY "STEP 2: Claude reviews staged changes"
STAGING_REVIEW=$(claude -p "Review these staged git changes in 2-3 sentences. Do they belong together? Anything weird staged (artifacts, secrets)? If fine, say so.\n\nDiff:\n$DIFF" 2>/dev/null)
SAY "Review: $STAGING_REVIEW"

while true; do
  read -p "Continue? [y]es / [u]nstage / [q]uit: " choice
  case "$choice" in
    y|Y|"") break ;;
    u|U)
      git diff --cached --name-only
      read -p "Files to unstage (space-separated): " files
      [ -n "$files" ] && git restore --staged $files
      git diff --cached --stat
      DIFF=$(git diff --cached) ;;
    q|Q) SAY "Aborted"; exit 0 ;;
  esac
done

[ -z "$(git diff --cached --name-only)" ] && { SAY "Nothing staged"; exit 0; }

# Commit message
SAY "STEP 3: Commit message"
read -p "Message: " USER_MSG

MSG_REVIEW=$(claude -p "Review this commit message in 2-3 sentences. Message: \"$USER_MSG\"\nDiff:\n$DIFF\nDoes it accurately describe the changes? Suggest improvements if needed." 2>/dev/null)
SAY "Review: $MSG_REVIEW"

while true; do
  read -p "[a]ccept / [e]dit / [r]ewrite / [q]uit: " choice
  case "$choice" in
    a|A|"") COMMIT_MSG="$USER_MSG"; break ;;
    e|E) read -p "New message: " USER_MSG ;;
    r|R)
      COMMIT_MSG=$(claude -p "Write a git commit message. Max 72 chars, imperative mood. Output ONLY the message.\n\nDiff:\n$DIFF" 2>/dev/null)
      COMMIT_MSG=$(echo "$COMMIT_MSG" | grep -viE "^(Co-Authored-By:|Claude-Session:)")
      SAY "Claude suggests: $COMMIT_MSG"
      read -p "[a]ccept / [e]dit: " c2
      [ "$c2" = "e" ] || [ "$c2" = "E" ] && read -p "Your version: " COMMIT_MSG
      break ;;
    q|Q) SAY "Aborted"; exit 0 ;;
  esac
done

# Commit + push
SAY "STEP 4: Commit & Push"
git commit -m "$COMMIT_MSG"

if git remote | grep -q .; then
  BRANCH=$(git rev-parse --abbrev-ref HEAD)
  git push -u origin "$BRANCH"
  SAY "Done"
else
  SAY "No remote. Committed locally"
fi
