#!/usr/bin/env bash
# ============================================================================
#  SHARED HELPERS: permavault (not a bake-exposed recipe itself)
# ============================================================================
# Sourced by perma.sh and permanent.sh. Assumes personality.sh (SAY, colors)
# has already been sourced by the caller.

find_project_root() {
	local current="$PWD"
	while [[ "$current" != "/" ]]; do
		[[ -d "$current/.makery" ]] && { echo "$current"; return 0; }
		current=$(dirname "$current")
	done
	return 1
}

PERMA_DIR="${MAKERY_PERMAVAULT_DIR:-$HOME/.shadow/.vault}"

# Create the permavault's layers and meta files if they don't exist yet.
init_permavault() {
	mkdir -p "$PERMA_DIR/raw" "$PERMA_DIR/wiki/summaries" "$PERMA_DIR/wiki/atomic" "$PERMA_DIR/wiki/maps"

	if [ ! -f "$PERMA_DIR/schema.md" ]; then
		cat > "$PERMA_DIR/schema.md" <<'EOF'
---
type: schema
title: Permavault Schema
description: The permanent, cross-project vault every project's .vault can merge into.
tags: [permavault, meta]
---

# Permavault Schema

Union of every project vault merged in via `bake call s=vault d=perma` (or linked live via
`bake call s=vault d=permanent`). Every note keeps the per-project prefix it was created
with, so `[[wikilinks]]` resolve without collision even though everything lives flat in one
vault.

Layers: `raw/`, `wiki/summaries/`, `wiki/atomic/`, `wiki/maps/`, same rules as any project
vault's own `<prefix>-schema.md`.

Not git-tracked. `_merges.md` is the append-only log of exactly which files got merged in,
from where, when. That's the record to work from if something needs undoing by hand.
EOF
	fi

	[ -f "$PERMA_DIR/index.md" ] || echo "# Permavault Index" > "$PERMA_DIR/index.md"
	[ -f "$PERMA_DIR/_merges.md" ] || echo "# Permavault merge history" > "$PERMA_DIR/_merges.md"
}

# Copy source_dir's raw/ and wiki/ content into the permavault. Never
# overwrites: a pre-existing destination file is treated as a bug signal
# (prefixing is supposed to make that impossible), not something to paper
# over silently.
merge_vault_into_perma() {
	local source_dir="$1" project_name="$2"
	init_permavault

	local added=() collisions=()
	local rel dest f

	while IFS= read -r -d '' f; do
		rel="${f#"$source_dir"/}"
		dest="$PERMA_DIR/$rel"
		if [ -e "$dest" ]; then
			SAY "! Collision, skipped: $rel"
			collisions+=("$rel")
			continue
		fi
		mkdir -p "$(dirname "$dest")"
		cp "$f" "$dest"
		added+=("$rel")
	done < <(find "$source_dir/raw" "$source_dir/wiki" -type f ! -name ".keep" -print0 2>/dev/null)

	# The project's own narrative log (<prefix>-log.md) isn't wiki content and
	# isn't a one-time addition like the files above: it gets overwritten on
	# every merge so the permavault carries the latest version. Back up
	# whatever was there before overwriting (a single slot, undo only ever
	# needs to step back one merge, same as everything else here) so undo
	# can restore it instead of just deleting it.
	local proj_log log_name="" log_status=""
	proj_log=$(find "$source_dir" -maxdepth 1 -name "*-log.md" | head -1)
	if [ -n "$proj_log" ]; then
		log_name=$(basename "$proj_log")
		local dest_log="$PERMA_DIR/$log_name" backup_dir="$PERMA_DIR/.log-backups"
		mkdir -p "$backup_dir"
		if [ -f "$dest_log" ]; then
			cp "$dest_log" "$backup_dir/$log_name"
			log_status="updated"
		else
			log_status="new"
		fi
		cp "$proj_log" "$dest_log"
		SAY "Carried $log_name into the permavault ($log_status)"
	fi

	{
		echo ""
		echo "## [$(date +%Y-%m-%d)] merge from $project_name"
		for rel in "${added[@]}"; do
			echo "- added: $rel"
		done
		for rel in "${collisions[@]}"; do
			echo "- collision, skipped: $rel"
		done
		[ -n "$log_name" ] && echo "- log: $log_name ($log_status)"
	} >> "$PERMA_DIR/_merges.md"

	SAY "Merged ${#added[@]} file(s) into $PERMA_DIR (${#collisions[@]} collision(s) skipped)"
}

# Undo the most recent merge recorded in _merges.md. Merges are purely
# additive (collisions are skipped, never overwritten), so undoing one is
# just deleting the files its own entry says it added, no snapshot needed.
undo_last_merge() {
	local logfile="$PERMA_DIR/_merges.md"
	if [ ! -f "$logfile" ] || ! grep -q '^## \[' "$logfile"; then
		SAY "Nothing to undo, no merges recorded yet."
		return 0
	fi

	local block header
	block=$(awk '/^## \[/{block=""} {block = block $0 ORS} END{print block}' "$logfile")
	header=$(echo "$block" | head -1)

	local removed=()
	while IFS= read -r rel; do
		[ -n "$rel" ] && removed+=("$rel")
	done < <(echo "$block" | sed -n 's/^- added: //p')

	local log_line log_name="" log_status=""
	log_line=$(echo "$block" | grep -m1 '^- log: ')
	if [ -n "$log_line" ]; then
		log_name=$(echo "$log_line" | sed -E 's/^- log: ([^ ]+) \((new|updated)\)$/\1/')
		log_status=$(echo "$log_line" | sed -E 's/^- log: ([^ ]+) \((new|updated)\)$/\2/')
	fi

	if [ ${#removed[@]} -eq 0 ] && [ -z "$log_name" ]; then
		SAY "Last log entry ('$header') has nothing to undo (possibly already an undo)."
		return 0
	fi

	SAY "About to undo: $header"
	for rel in "${removed[@]}"; do
		echo "  - remove: $rel"
	done
	if [ -n "$log_name" ]; then
		if [ "$log_status" = "new" ]; then
			echo "  - remove: $log_name (was newly added this merge)"
		else
			echo "  - restore: $log_name (back to its pre-merge version)"
		fi
	fi
	echo -ne "  ${YELLOW}⚠${NC} Apply this undo? (y/N): "
	read -r response
	if [[ ! "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
		SAY "Left untouched."
		return 0
	fi

	for rel in "${removed[@]}"; do
		if [ -f "$PERMA_DIR/$rel" ]; then
			rm -f "$PERMA_DIR/$rel"
			SAY "- removed: $rel"
		else
			SAY "- already gone: $rel"
		fi
	done

	local log_action=""
	if [ -n "$log_name" ]; then
		if [ "$log_status" = "new" ]; then
			rm -f "$PERMA_DIR/$log_name"
			log_action="removed $log_name"
			SAY "- removed: $log_name"
		elif [ -f "$PERMA_DIR/.log-backups/$log_name" ]; then
			cp "$PERMA_DIR/.log-backups/$log_name" "$PERMA_DIR/$log_name"
			log_action="restored $log_name"
			SAY "- restored: $log_name"
		else
			SAY "! No backup found for $log_name, left as-is."
		fi
	fi

	{
		echo ""
		echo "## [$(date +%Y-%m-%d)] undo of: $header"
		for rel in "${removed[@]}"; do
			echo "- removed: $rel"
		done
		[ -n "$log_action" ] && echo "- undid-log: $log_action"
	} >> "$logfile"

	SAY "Undid ${#removed[@]} file(s)$( [ -n "$log_action" ] && echo " and $log_action" ) from $PERMA_DIR"
}
