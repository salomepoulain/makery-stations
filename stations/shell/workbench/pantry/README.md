# Shell pantry

A small shell config for a server without internet: `bashrc_cluster`, `zshrc_cluster`, `lsd.sh` and `prompt.sh`, all in this folder. They only use what bash, zsh, git, GNU find and awk already have, so there's nothing to install and nothing reaches the network. Both configs give the same things:

- `ls` that looks like `lsd --blocks permission,size,date,name --icon=always`: colored permissions, sizes and dates, folders first, an icon per file type and hidden files left out. `ls -a` (or `la`) adds the hidden files under a dotted line. Other flags, like `ls -l` or `ls *.py`, go to the normal `ls`. The icons need a Nerd Font in the terminal; the vscode station has MesloLGM Nerd Font Mono in its `fonts/`, and its `style/` settings already fall back to it.
- big shared history, and up/down arrows that search it for what you've typed so far
- `ll` (normal long listing), `lt`, `c` (clear) and `pip` as `pip3`
- a prompt that looks like Powerlevel10k lean, without Powerlevel10k: a blank line between commands, then system icon, folder, git branch with p10k's marks (`⇣` behind, `⇡` ahead, `~` conflict, `+` staged, `!` changed, `?` new) and `❯`, red after a failed command. On the right: the exit code, how long the last command took (from 3 seconds; in bash from version 4.4) and the Python env.
- case-insensitive tab completion (zsh also gets a menu and `cd` by typing a folder name)

They do nothing in a non-interactive shell, so `scp` and VS Code's Remote-SSH server keep working.

Run `bake first shell` in a project, then copy this folder to your home as `~/.shell`:

```bash
cp -r .makery/stations/shell/workbench/pantry ~/.shell
```

Or drag this folder to your home on the server and rename it to `.shell`. Then check in a Remote-SSH terminal whether the server has zsh:

```bash
command -v zsh
```

**No zsh** (nothing printed): run once

```bash
echo '[ -f ~/.shell/bashrc_cluster ] && . ~/.shell/bashrc_cluster' >> ~/.bashrc
```

**zsh is there:** run once

```bash
echo '[ -f ~/.shell/zshrc_cluster ] && . ~/.shell/zshrc_cluster' >> ~/.zshrc
```

You can't change your login shell with `chsh` there, and you don't need to. Let VS Code open zsh in its terminal by adding this to your user settings:

```jsonc
"terminal.integrated.defaultProfile.linux": "zsh"
```

Open a new terminal to see it. Oh-my-zsh, Powerlevel10k, lsd and zoxide from a Mac setup don't belong on the server: they're software you'd have to install, and oh-my-zsh updates itself over the internet.
