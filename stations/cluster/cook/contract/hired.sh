#!/bin/bash
# ============================================================================
#  LINE COOK CONTRACT: HIRED (Setup Script)
# ============================================================================
# This script is executed exactly once when the Head Chef hires this Line Cook
# using `bake first <this_cook>`.
#
# Deliberately does nothing heavy - shell/dotfiles setup and cluster sync
# are both explicit opt-in recipes, not automatic on hire, since this
# station gets hired on machines you don't want surprise installs on.

source "$(dirname "${BASH_SOURCE[0]}")/../personality.sh"

SAY "Cluster station is ready."
SAY "  bake call s=cluster d=shell        - install dotfiles/shell (Linuxbrew, chezmoi, oh-my-zsh, powerlevel10k)"
SAY "  bake call s=cluster d=sync [host]  - sync this project's __sync__/ folder with a remote host"
