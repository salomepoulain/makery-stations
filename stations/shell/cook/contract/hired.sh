#!/bin/bash
# ============================================================================
#  LINE COOK CONTRACT: HIRED (Setup Script)
# ============================================================================
# The shell config belongs in your home, not in the project, so hiring only
# shows where the files are and how to turn them on. Nothing is installed.

source "$(dirname "${BASH_SOURCE[0]}")/../personality.sh"

PANTRY=".makery/stations/shell/workbench/pantry"

SAY "Shell config (lsd-style ls, Powerlevel10k-style prompt) is in $PANTRY"
SAY "To use it, run these two lines once, then open a new terminal:"
echo ""
echo "    cp -r $PANTRY ~/.shell"
echo "    echo '[ -f ~/.shell/bashrc_cluster ] && . ~/.shell/bashrc_cluster' >> ~/.bashrc"
echo ""
SAY "With zsh, use zshrc_cluster and ~/.zshrc instead."
