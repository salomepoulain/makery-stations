# A lean prompt in the style of Powerlevel10k, in plain bash or zsh.
# Nothing to install; git is read with a normal `git status`.
#
#    ~/project  main ⇡1 +2 !1 ?3 ❯                  ✘1   12s   venv
#
# Left: system icon, folder, git branch and changes, then ❯ (red after a
# failed command). Right: exit code, how long the last command took (bash 4.4+ or zsh)
# and the Python env. A blank line between commands. Icons need a Nerd Font.
# Git marks like p10k: ⇣ behind, ⇡ ahead, ~ conflict, + staged, ! changed, ? new.

if [ "$(uname -s)" = Darwin ]; then _p_os=''; else _p_os=''; fi

# The env names go on the right, so activate scripts shouldn't add them on the left.
export VIRTUAL_ENV_DISABLE_PROMPT=1 CONDA_CHANGEPS1=false

if [ -n "$ZSH_VERSION" ]; then
    _P_RED='%F{1}' _P_GREEN='%F{2}' _P_YELLOW='%F{3}' _P_BLUE='%F{4}' _P_CYAN='%F{6}' _P_OFF='%f'
else
    # \001 and \002 tell bash these bytes take no room on the line.
    _P_RED=$'\001\e[38;5;1m\002' _P_GREEN=$'\001\e[38;5;2m\002' _P_YELLOW=$'\001\e[38;5;3m\002'
    _P_BLUE=$'\001\e[38;5;4m\002' _P_CYAN=$'\001\e[38;5;6m\002' _P_OFF=$'\001\e[0m\002'
fi

_p_git() {
    _p_gitseg=
    local s
    s=$(GIT_OPTIONAL_LOCKS=0 git status --porcelain=v2 --branch 2>/dev/null) || return
    _p_gitseg=$(printf '%s\n' "$s" | awk -v G="$_P_GREEN" -v Y="$_P_YELLOW" -v B="$_P_BLUE" \
        -v R="$_P_RED" -v O="$_P_OFF" -v Z="${ZSH_VERSION:+1}" '
        /^# branch\.oid/  { oid = substr($3, 1, 8) }
        /^# branch\.head/ { b = $3 }
        /^# branch\.ab/   { a = substr($3, 2) + 0; d = substr($4, 2) + 0 }
        /^[12] /          { if (substr($2, 1, 1) != ".") s++; if (substr($2, 2, 1) != ".") m++ }
        /^u /             { c++ }
        /^\? /            { u++ }
        END {
            if (b == "(detached)") b = "@" oid
            if (Z) gsub(/%/, "%%", b)
            out = " " G " " b
            if (d) out = out " ⇣" d
            if (a) out = out " ⇡" a
            if (c) out = out " " R "~" c
            if (s) out = out " " Y "+" s
            if (m) out = out " " Y "!" m
            if (u) out = out " " B "?" u
            print out O
        }')
}

_p_add() {  # color, text: one item on the right
    _p_right="${_p_right:+$_p_right  }$1$2$_P_OFF"
    _p_plain="${_p_plain:+$_p_plain  }$2"
}

_p_precmd() {
    local st=$? dt env
    [ -n "$_p_seen" ] && echo
    _p_seen=1
    _p_right= _p_plain=
    _p_git
    if [ "$st" = 0 ]; then _p_char="${_P_GREEN}❯${_P_OFF}"; else _p_char="${_P_RED}❯${_P_OFF}"; fi
    [ "$st" != 0 ] && _p_add "$_P_RED" "✘$st"
    if [ -n "$_p_t0" ]; then
        dt=$((SECONDS - _p_t0)); unset _p_t0
        if [ "$dt" -ge 3600 ]; then _p_add "$_P_YELLOW" " $((dt / 3600))h $((dt % 3600 / 60))m"
        elif [ "$dt" -ge 60 ]; then _p_add "$_P_YELLOW" " $((dt / 60))m $((dt % 60))s"
        elif [ "$dt" -ge 3 ]; then _p_add "$_P_YELLOW" " ${dt}s"
        fi
    fi
    env=${VIRTUAL_ENV##*/}
    [ -z "$env" ] && env=$CONDA_DEFAULT_ENV
    [ -n "$env" ] && _p_add "$_P_CYAN" " $env"
    if [ -n "$ZSH_VERSION" ]; then
        RPROMPT=$_p_right
    elif [ -n "$_p_plain" ]; then
        # bash has no right prompt: print it at the far right, then go back to the start.
        printf '%*s%s\r' $((${COLUMNS:-80} - ${#_p_plain} - 1)) '' "${_p_right//[$'\001\002']/}"
    fi
    return $st
}

if [ -n "$ZSH_VERSION" ]; then
    _p_preexec() { _p_t0=$SECONDS; }
    setopt prompt_subst
    autoload -Uz add-zsh-hook
    add-zsh-hook precmd _p_precmd
    add-zsh-hook preexec _p_preexec
    PROMPT='%F{7}'"$_p_os"' %F{4}%~%f${_p_gitseg} ${_p_char} '
else
    PROMPT_COMMAND="_p_precmd${PROMPT_COMMAND:+; $PROMPT_COMMAND}"
    # PS0 is shown right before a command runs (bash 4.4+). This one prints
    # nothing; it only notes the start time, for "took 5s" on the right.
    PS0='${_p_os:$((_p_t0 = SECONDS, 0)):0}'"$PS0"
    PS1='\[\e[38;5;7m\]'"$_p_os"' \[\e[38;5;4m\]\w\[\e[0m\]${_p_gitseg} ${_p_char} '
fi
