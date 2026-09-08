#!/bin/bash
# ============================================================================
#  LINE COOK CONTRACT: HIRED (Setup Script)
# ============================================================================
# This script is executed exactly once when the Head Chef hires this Line Cook
# using `bake first <this_cook>`. It's also safe to re-run directly
# (bake call s=cluster d=setup) - every step checks before it acts, so a
# second run never reinstalls tools or silently rewrites your dotfiles.
#
# Bootstraps a per-user Linuxbrew (no sudo) to provide zsh/less/vim/make/
# zoxide/lsd, installs chezmoi, oh-my-zsh, powerlevel10k and the zsh
# plugins referenced in the dotfiles, then applies the dotfiles via
# chezmoi (asking for confirmation the first time, since that step can
# overwrite existing files; every later run pulls latest and re-applies
# automatically). Also drops a .vscode/settings.json at the project root
# so VS Code's integrated terminal defaults to zsh here too.

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

DOTFILES_REPO="https://github.com/salomepoulain/dotfiles.git"
BIN_DIR="$HOME/.local/bin"
LINUXBREW_PREFIX="$HOME/.linuxbrew"
mkdir -p "$BIN_DIR"

SAY "Setting up shell environment (Linuxbrew, chezmoi, oh-my-zsh, powerlevel10k)"

case ":$PATH:" in
    *":$BIN_DIR:"*) ;;
    *) SAY "Note: $BIN_DIR isn't on your \$PATH yet - add 'export PATH=\"\$PATH:$BIN_DIR\"' to your shell rc and re-login" ;;
esac

# --- Linuxbrew (per-user, no sudo) ---
if command -v brew >/dev/null 2>&1; then
    SAY "brew already on \$PATH"
elif [ -x "$LINUXBREW_PREFIX/bin/brew" ]; then
    eval "$("$LINUXBREW_PREFIX/bin/brew" shellenv)"
else
    SAY "Bootstrapping Linuxbrew into $LINUXBREW_PREFIX (no sudo)..."
    git clone --depth=1 https://github.com/Homebrew/brew "$LINUXBREW_PREFIX/Homebrew"
    mkdir -p "$LINUXBREW_PREFIX/bin"
    ln -sf "$LINUXBREW_PREFIX/Homebrew/bin/brew" "$LINUXBREW_PREFIX/bin/brew"
    eval "$("$LINUXBREW_PREFIX/bin/brew" shellenv)"
    brew update --force --quiet
fi

if command -v brew >/dev/null 2>&1; then
    BREW_WANT=()
    for tool in zsh less vim make zoxide lsd; do
        command -v "$tool" >/dev/null 2>&1 || BREW_WANT+=("$tool")
    done
    if [ "${#BREW_WANT[@]}" -gt 0 ]; then
        SAY "Installing via brew: ${BREW_WANT[*]}"
        brew install "${BREW_WANT[@]}"
    else
        SAY "zsh, less, vim, make, zoxide, lsd already present"
    fi
else
    SAY "Warning: brew unavailable, skipping zsh/less/vim/make/zoxide/lsd install"
fi

# --- chezmoi ---
if ! command -v chezmoi >/dev/null 2>&1; then
    SAY "Installing chezmoi..."
    sh -c "$(curl -fsLS get.chezmoi.io)" -- -b "$BIN_DIR"
else
    SAY "chezmoi already installed"
fi

if command -v chezmoi >/dev/null 2>&1; then
    CHEZMOI="chezmoi"
else
    CHEZMOI="$BIN_DIR/chezmoi"
fi

# --- oh-my-zsh ---
if [ ! -d "$HOME/.oh-my-zsh" ]; then
    SAY "Cloning oh-my-zsh..."
    git clone --depth=1 https://github.com/ohmyzsh/ohmyzsh.git "$HOME/.oh-my-zsh"
else
    SAY "oh-my-zsh already present"
fi

ZSH_CUSTOM="${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}"

# --- powerlevel10k theme ---
if [ ! -d "$ZSH_CUSTOM/themes/powerlevel10k" ]; then
    SAY "Cloning powerlevel10k..."
    git clone --depth=1 https://github.com/romkatv/powerlevel10k.git "$ZSH_CUSTOM/themes/powerlevel10k"
else
    SAY "powerlevel10k already present"
fi

# --- zsh plugins used by .zshrc ---
if [ ! -d "$ZSH_CUSTOM/plugins/zsh-autosuggestions" ]; then
    SAY "Cloning zsh-autosuggestions..."
    git clone --depth=1 https://github.com/zsh-users/zsh-autosuggestions "$ZSH_CUSTOM/plugins/zsh-autosuggestions"
fi
if [ ! -d "$ZSH_CUSTOM/plugins/zsh-syntax-highlighting" ]; then
    SAY "Cloning zsh-syntax-highlighting..."
    git clone --depth=1 https://github.com/zsh-users/zsh-syntax-highlighting "$ZSH_CUSTOM/plugins/zsh-syntax-highlighting"
fi

# --- apply dotfiles (confirm only the first time; reruns are pure chezmoi diffs) ---
CHEZMOI_SOURCE_DIR="$HOME/.local/share/chezmoi"
if [ -d "$CHEZMOI_SOURCE_DIR" ]; then
    SAY "Dotfiles already managed by chezmoi, pulling latest and re-applying..."
    "$CHEZMOI" update
    APPLIED=true
else
    SAY "Initializing chezmoi from $DOTFILES_REPO..."
    "$CHEZMOI" init "$DOTFILES_REPO"
    echo ""
    "$CHEZMOI" diff || true
    echo ""
    read -rp "  Apply these dotfiles? This may overwrite existing files shown above. [y/N] " confirm
    if [[ "$confirm" =~ ^[Yy]$ ]]; then
        "$CHEZMOI" apply
        SAY "Dotfiles applied"
        APPLIED=true
    else
        SAY "Skipped applying dotfiles. Re-run this recipe, or 'chezmoi apply' manually, when ready."
        APPLIED=false
    fi
fi

# --- make zsh your shell without needing sudo/chsh permission ---
# Only once dotfiles are actually in place - otherwise you'd get dropped
# into a zsh session with no .zshrc/.p10k.zsh and a confusing p10k warning.
if [ "$APPLIED" = true ] && command -v zsh >/dev/null 2>&1; then
    ZSH_BIN="$(command -v zsh)"
    if ! chsh -s "$ZSH_BIN" >/dev/null 2>&1; then
        MARKER="# cluster station: auto-exec zsh (chsh unavailable, no sudo)"
        if ! grep -Fq "$MARKER" "$HOME/.bashrc" 2>/dev/null; then
            SAY "chsh not permitted here; falling back to auto-exec zsh from .bashrc"
            {
                echo ""
                echo "$MARKER"
                echo "[ -t 1 ] && [ -z \"\$ZSH_VERSION\" ] && exec \"$ZSH_BIN\" -l"
            } >> "$HOME/.bashrc"
        fi
    fi
    SAY "Done. Run 'exec zsh' (or start a new session) to pick up the new shell."
else
    SAY "Not switching your default shell yet - re-run this once dotfiles are applied."
fi

# --- VS Code: default this project's integrated terminal to zsh too ---
# (separate from chsh/.bashrc above - VS Code's Remote-SSH terminal doesn't
# always go through a login shell, so it can still land on bash otherwise)
if command -v zsh >/dev/null 2>&1; then
    ZSH_BIN="$(command -v zsh)"
    PROJECT_ROOT=$(find_project_root) || PROJECT_ROOT=""
    if [ -n "$PROJECT_ROOT" ]; then
        VSCODE_DIR="$PROJECT_ROOT/.vscode"
        SETTINGS_FILE="$VSCODE_DIR/settings.json"
        mkdir -p "$VSCODE_DIR"
        if command -v python3 >/dev/null 2>&1; then
            python3 - "$SETTINGS_FILE" "$ZSH_BIN" <<'PYEOF'
import json, sys, os

path, zsh_bin = sys.argv[1], sys.argv[2]
data = {}
if os.path.isfile(path):
    try:
        with open(path) as f:
            data = json.load(f)
    except Exception:
        data = {}

data["terminal.integrated.defaultProfile.linux"] = "zsh"
profiles = data.get("terminal.integrated.profiles.linux", {})
profiles["zsh"] = {"path": zsh_bin, "args": ["-l"]}
data["terminal.integrated.profiles.linux"] = profiles

with open(path, "w") as f:
    json.dump(data, f, indent=2)
    f.write("\n")
PYEOF
            SAY "Wrote $SETTINGS_FILE (VS Code will default to zsh here)"
        elif [ ! -f "$SETTINGS_FILE" ]; then
            cat > "$SETTINGS_FILE" <<EOF2
{
  "terminal.integrated.defaultProfile.linux": "zsh",
  "terminal.integrated.profiles.linux": {
    "zsh": {
      "path": "$ZSH_BIN",
      "args": ["-l"]
    }
  }
}
EOF2
            SAY "Wrote $SETTINGS_FILE (VS Code will default to zsh here)"
        else
            SAY "python3 not found and $SETTINGS_FILE already exists - add the zsh terminal profile there manually"
        fi
    fi
fi
