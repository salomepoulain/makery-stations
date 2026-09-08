#!/usr/bin/env bash
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
KITCHEN_DIR="$(dirname "${BASH_SOURCE[0]}")/../../../.."
GITIGNORE="$PROJECT_ROOT/.gitignore"

> "$GITIGNORE"

collect_contraband() {
    local file="$1"
    [[ -f "$file" ]] || return
    while IFS= read -r line || [[ -n "$line" ]]; do
        [[ -z "$line" || "$line" == "#"* ]] && continue
        grep -Fxq "$line" "$GITIGNORE" || echo "$line" >> "$GITIGNORE"
    done < "$file"
}

collect_contraband "$KITCHEN_DIR/headchef/pockets/.contraband"
for contraband in "$KITCHEN_DIR/stations"/*/workbench/.contraband; do
    collect_contraband "$contraband"
done

SAY "Refreshed .gitignore"
