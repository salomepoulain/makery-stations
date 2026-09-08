#!/usr/bin/env bash
# ============================================================================
#  LINE COOK CONTRACT: ILLEGAL (Memory relocation)
# ============================================================================
# This script runs after this Line Cook's contraband has already been
# stashed by `bake shady` (REPO_ROOT and SHADOW_DIR are exported by the
# Head Chef). It points Claude's auto-memory storage at the stash instead
# of the global ~/.claude, so this project's memory lives with the rest of
# its contraband instead of under the global home directory. It also locks
# Claude's file-reading tools (Read/Grep/Glob/LSP) to just REPO_ROOT and
# SHADOW_DIR, so the project's own symlinked-out folders (.claude, .vault,
# __stash__) stay reachable while the rest of the filesystem doesn't.
#
# On Linux/WSL, it goes further and enables the native bwrap sandbox with a
# deny-everything-except-an-explicit-allowlist filesystem policy, so Bash
# itself (not just Claude's own Read/Grep/Glob tools) is confined. The
# allowlist was built and verified by hand on one WSL machine (checked via
# ldd against bash/git/python3, readlink -f against /bin, /lib, /lib64).
# See the ml1 session that wrote this for the reasoning. It covers exactly
# this user's real toolchain footprint (rtk, bake, Homebrew, Solana,
# Haskell, nvm, cargo); a project needing a toolchain not on this list
# (Go, Docker, Kubernetes, Ruby: all pre-approved in permissions.allow but
# not observed in use) will need its directory added by hand.
#
# macOS is deliberately NOT given the strict filesystem sandbox yet: the
# equivalent essential-path list (dyld shared cache quirks, Homebrew at
# /opt/homebrew vs /usr/local depending on Apple Silicon vs Intel) hasn't
# been verified on an actual Mac. Shipping an unverified deny-by-default
# list there risks silently breaking every Bash command on that machine.
# Darwin still gets the safer blockReadsOutsideWorkingDirectories layer
# below, same as Linux; the stricter Bash-level sandbox is a TODO for when
# this is actually tested on a Mac.

source "$(dirname "${BASH_SOURCE[0]}")/../personality.sh"

# Quiet mode: set by shady.sh when this runs as part of an automatic sweep
# triggered by hiring another station, rather than a deliberate `bake shady`.
# The actual reconciliation below still runs unconditionally either way.
# Only the announcements are suppressed.
QUIET="${MAKERY_QUIET_SHADY:-0}"
QUIET_SAY() { [ "$QUIET" = "1" ] || SAY "$1"; }

CLAUDE_DIR_PATH="$REPO_ROOT/.claude"
MEMORY_DIR="$REPO_ROOT/__stash__/.claude/memory"

# If .claude doesn't exist at all yet, there was nothing to stash above.
# Create it fresh, straight in the shadow, same as everything else here.
if [ ! -e "$CLAUDE_DIR_PATH" ]; then
	mkdir -p "$SHADOW_DIR/.claude"
	ln -s "$SHADOW_DIR/.claude" "$CLAUDE_DIR_PATH"
	QUIET_SAY "Created .claude fresh, straight in the stash"
fi

mkdir -p "$MEMORY_DIR"

SETTINGS_FILE="$CLAUDE_DIR_PATH/settings.local.json"
[ -f "$SETTINGS_FILE" ] || echo '{}' > "$SETTINGS_FILE"

if command -v jq &> /dev/null; then
	jq --arg dir "$MEMORY_DIR" '.autoMemoryDirectory = $dir' "$SETTINGS_FILE" > "$SETTINGS_FILE.tmp" && mv "$SETTINGS_FILE.tmp" "$SETTINGS_FILE"
	QUIET_SAY "Memory now lives in the stash: $MEMORY_DIR"

	jq --arg dir "$SHADOW_DIR" '
		.permissions.blockReadsOutsideWorkingDirectories = true
		| .permissions.additionalDirectories = ((.permissions.additionalDirectories // []) + [$dir] | unique)
	' "$SETTINGS_FILE" > "$SETTINGS_FILE.tmp" && mv "$SETTINGS_FILE.tmp" "$SETTINGS_FILE"
	QUIET_SAY "File-reading tools locked to $REPO_ROOT and $SHADOW_DIR"

	# Bash-level sandbox: verified on Linux/WSL only (see comment above).
	if [ "$(uname -s)" = "Linux" ]; then
		jq \
			--arg repo "$REPO_ROOT" \
			--arg shadow "$SHADOW_DIR" \
			--arg tmp "/tmp/claude-$(id -u)" \
			--arg rtk "$HOME/.local/bin/rtk" \
			--arg bake "$HOME/.local/bin/bake" \
			--arg brew "/home/linuxbrew/.linuxbrew" \
			--arg solana "$HOME/.local/share/solana" \
			--arg cabal "$HOME/.cabal" \
			--arg ghcup "$HOME/.ghcup" \
			--arg nvm "$HOME/.nvm" \
			--arg cargo "$HOME/.cargo" \
			'
			.sandbox.enabled = true
			| .sandbox.filesystem.denyRead = ["/"]
			| .sandbox.filesystem.allowRead = [
				"/usr/bin", "/usr/lib/x86_64-linux-gnu", "/usr/share/terminfo", "/lib64",
				"/etc/resolv.conf", "/etc/nsswitch.conf", "/etc/ssl/certs/ca-certificates.crt",
				"/etc/hosts", "/etc/localtime", "/etc/passwd",
				"/dev/null", "/dev/urandom", "/dev/tty", "/dev/zero",
				"/proc/self",
				$tmp, $repo, $shadow, $rtk, $bake, $brew, $solana, $cabal, $ghcup, $nvm, $cargo
			]
			' "$SETTINGS_FILE" > "$SETTINGS_FILE.tmp" && mv "$SETTINGS_FILE.tmp" "$SETTINGS_FILE"
		QUIET_SAY "Bash-level sandbox enabled: deny-all except the verified allowlist"
	else
		QUIET_SAY "Skipping Bash-level sandbox (only verified on Linux/WSL so far, not $(uname -s))"
	fi
else
	SAY "Warning: jq not found, couldn't set autoMemoryDirectory or lock file access automatically"
fi
