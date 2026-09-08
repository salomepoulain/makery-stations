printf '\033[6 q'
# Enable Powerlevel10k instant prompt. Should stay close to the top of ~/.zshrc.
# Initialization code that may require console input (password prompts, [y/n]
# confirmations, etc.) must go above this block; everything else may go below.
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

ZSH_THEME="powerlevel10k/powerlevel10k"
# Path to your oh-my-zsh installation.
export ZSH="$HOME/.oh-my-zsh"

# --- Custom ZLE Widgets (Functions) ---
# Ensure these are defined before any bindkey uses them.

# Define a new ZLE widget to clear the entire line buffer
zle -N clear-line-buffer
clear-line-buffer() {
  BUFFER=""
  CURSOR=0
}

zle -N copy-line-to-x-clipboard
copy-line-to-x-clipboard() {
  print -n "$BUFFER" | xclip -selection clipboard
}

# Bind Ctrl+A (prefix key)
bindkey '^A' copy-line-to-x-clipboard

# Bind Backspace after Ctrl+A to the new widget
bindkey -M emacs '^A^H' clear-line-buffer
bindkey -M viins '^A^H' clear-line-buffer
bindkey -M vicmd '^A^H' clear-line-buffer

# Your other standard bindings (ensure their functions are defined above)
bindkey '^H' backward-kill-word # Ctrl+Backspace (delete word left)
bindkey '^[[1;5D' backward-word # Ctrl+Left Arrow (move word left)
bindkey '^[[1;5C' forward-word # Ctrl+Right Arrow (move word right)

plugins=(git zsh-autosuggestions zsh-syntax-highlighting)

# User configuration

if [ -f "$ZSH/oh-my-zsh.sh" ]; then
  source "$ZSH/oh-my-zsh.sh"
fi

# To customize prompt, run `p10k configure` or edit ~/.p10k.zsh.
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh

alias ls='lsd --almost-all --blocks permission,size,date,name --icon=always --color=always 2>/dev/null \
| awk '"'"'{
    n = split($NF, a, ".");
    ext = (n > 1 ? a[n] : "");
    name = $NF;
    print ext "\t" name "\t" $0
}'"'"' \
| sort -k1,1 -k2,2 \
| awk -F'"'"'\t'"'"' '"'"'{ print $3 }'"'"''

alias lf='lsd --blocks permission,size,date,name --icon=always --color=always \
| awk '\''{
    n = split($NF, a, ".");
    ext = (n > 1 ? a[n] : "");
    name = $NF;
    print ext "\t" name "\t" $0
}'\'' \
| sort -k1,1 -k2,2 \
| awk -F'\t' '\''{ print $3 }'\'' \
| sed -E "s/^\.([rwx-]{9})/-\1/"'

alias lj='lsd --blocks permission,size,date,name --icon=always --color=always \
| awk '\''{
    n = split($NF, a, ".");
    ext = (n > 1 ? a[n] : "");
    name = $NF;
    print ext "\t" name "\t" $0
}'\'' \
| sort -k1,1 -k2,2 \
| awk -F'\t' '\''{ print $3 }'\'' \
| perl -pe '\''s/^((?:\x1b\[[0-9;]*m)*)(\.)([rwx-]{9})/${1}-${3}/'\'''

alias lk='lsd --blocks permission,size,date,name --icon=always --color=always \
| awk '\''{
    n = split($NF, a, ".");
    ext = (n > 1 ? a[n] : "");
    name = $NF;
    print ext "\t" name "\t" $0
}'\'' \
| sort -k1,1 -k2,2 \
| awk -F'\t' '\''{ print $3 }'\'' \
| perl -pe '\''s/^((?:\x1b\[[0-9;]*m)*).([rwx-]{9})/${1}-\2/'\'''

alias lz='/bin/ls'

alias lt='lsd --tree -X'

# Ensure auto-completion works
autoload -Uz compinit
compinit

if command -v zoxide >/dev/null 2>&1; then
  eval "$(zoxide init zsh)"
fi

alias cd='z'

export PATH="$HOME/.local/bin:$PATH"

alias c='printf "\x1Bc"'

alias clip='xclip -selection clipboard <'

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

LS_COLORS="$LS_COLORS:ow=0;34:tw=0;34"

alias -g zrc='~/.zshrc'

zstyle ':completion:*' list-colors

# Menu-driven completion (arrow keys to select)
zstyle ':completion:*' menu select

# Group results by type (with labeled headers)
zstyle ':completion:*' group-name ''

# Format group headers with nice dashes
zstyle ':completion:*:*:*:*:descriptions' format '%B%F{yellow}────── %d ──────%f%b'

# Show extra info if available
zstyle ':completion:*' verbose yes

# When no matches, show a friendly message
zstyle ':completion:*:warnings' format '%F{red}No matches found.%f'

# When Zsh corrects a typo, show the correction clearly
zstyle ':completion:*:corrections' format '%F{magenta}Did you mean: %d (errors: %e)%f'

# Display directory first in `cd` completion (so dirs are first in menu)
zstyle ':completion:*' list-dirs-first true

# dumb autocomplete
zstyle ':completion:*' matcher-list '' 'm:{a-zA-Z}={A-Za-z}' 'r:|[._-]=* r:|=*' 'l:|=* r:|=*'

fpath+=~/.zfunc

# Optional project-local shell add-ons copied by the docker station template.
# Put machine-specific PATH entries, toolchain installs (solana, ghcup, etc.)
# and anything else host-specific here instead of hard-coding them above.
[ -f "$HOME/.shell_env.zsh" ] && source "$HOME/.shell_env.zsh"
