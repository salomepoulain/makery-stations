# VS Code pantry

My VS Code setup in three packs. There are no keys, SSH hosts or machine paths in here, so you can use it anywhere.

| Folder | When | What |
|---|---|---|
| `style/` | always | theme, icons, colors, fonts, layout, Error Lens, file nesting |
| `functionality/` | always | autosave, editor behavior, tabs, git, terminal, privacy, Todo+, Remote SSH |
| `addons/` | per project | Python, Pylance, Ruff, Jupyter, Data Wrangler, TOML |

Each pack has a `settings.json` and an `extensions.json`. Inside each file, every extension has its own `// MARK:` section. Copy `functionality/.editorconfig` to the root of a project and the EditorConfig extension reads it.

Want everything? `settings.json` and `extensions.json` in this folder are the three packs in one file. There's no install script: you copy and paste, so nothing runs and nothing gets downloaded behind your back.

## Install

It takes a few minutes.

### 1. Fonts

Do this first, so VS Code picks them up on the next start.

- **macOS:** select all `.ttf` files in `fonts/`, double-click and choose "Install". Or drag them to `~/Library/Fonts`.
- **Windows:** select all `.ttf` files in `fonts/`, right-click and choose "Install". Don't choose "Install for all users", that needs admin rights.
- **Linux:** copy them to `~/.local/share/fonts` and run `fc-cache -f`.

### 2. Extensions

Open the Extensions sidebar in VS Code, search for each name in `extensions.json` and click "Install". Or put `extensions.json` in a project as `.vscode/extensions.json`: VS Code then shows them all under "Recommended".

No marketplace, like on a locked-down machine? Install a `.vsix` file with right-click, "Install Extension VSIX" in the Explorer.

### 3. Settings

1. In VS Code, open the Command Palette (`Cmd+Shift+P` or `Ctrl+Shift+P`) and choose "Preferences: Open User Settings (JSON)".
2. Copy what's in there somewhere safe, as a backup.
3. Replace it with the contents of `settings.json` from this folder. Without addons? Take `style/settings.json` and paste only what's between the outer `{` and `}` of `functionality/settings.json` after it, with a comma in between.
4. Had your own settings? Paste them back at the bottom, before the last `}`, and remove keys that now appear twice. VS Code underlines duplicate keys.
5. Save and restart VS Code.

Extensions for just one project? Put `addons/extensions.json` in that project as `.vscode/extensions.json`.

## Fonts

The fonts are in `fonts/`, as `.ttf` for macOS, Windows and Linux. Installing them as above needs no admin rights. Restart VS Code afterwards. Licenses are in `fonts/LICENSES.md`.

Install them on the machine where VS Code runs, not on a remote server.

- Fira Code: editor, terminal, debug console
- Cascadia Code: Error Lens messages
- CMU Serif or STIX Two Text: markdown cells in notebooks
- MesloLGM Nerd Font Mono: terminal fallback for prompt icons

## Shell on the cluster

`shell/` has a small config for a server without internet: `bashrc_cluster`, `zshrc_cluster`, `lsd.sh` and `prompt.sh`. They only use what bash, zsh, git, GNU find and awk already have, so there's nothing to install and nothing reaches the network. Both configs give the same things:

- `ls` that looks like `lsd --blocks permission,size,date,name --icon=always`: colored permissions, sizes and dates, folders first, an icon per file type and hidden files left out. `ls -a` (or `la`) adds the hidden files under a dotted line. Other flags, like `ls -l` or `ls *.py`, go to the normal `ls`. The icons need a Nerd Font in the terminal; the `style/` settings already fall back to MesloLGM Nerd Font Mono.
- big shared history, and up/down arrows that search it for what you've typed so far
- `ll` (normal long listing), `lt`, `c` (clear) and `pip` as `pip3`
- a prompt that looks like Powerlevel10k lean, without Powerlevel10k: a blank line between commands, then system icon, folder, git branch with p10k's marks (`⇣` behind, `⇡` ahead, `~` conflict, `+` staged, `!` changed, `?` new) and `❯`, red after a failed command. On the right: the exit code, how long the last command took (from 3 seconds; in bash from version 4.4) and the Python env.
- case-insensitive tab completion (zsh also gets a menu and `cd` by typing a folder name)

They do nothing in a non-interactive shell, so `scp` and VS Code's Remote-SSH server keep working.

Drag the whole `shell/` folder to your home on the server and rename it to `.shell`. Then check in a Remote-SSH terminal whether the server has zsh:

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

## Notes

- In the offline package (`makery-bakery-offline.zip`) this folder also has `makery-kitchen-explorer-<version>.vsix`. After `bake first vscode`, right-click it in `.makery/stations/vscode/workbench/pantry/` and choose "Install Extension VSIX".
- Flow Icons is paid. The license key is deliberately not in here. Put `flow-icons.licenseKey` in your own user settings.
- `community.notebook-minimap` is my own extension (github.com/salomepoulain/vscode-notebook-minimap). If it's not in the marketplace of a locked-down environment, install it as a `.vsix`.
- Without Jupyter from `addons/`, the notebook settings in `style/` do nothing. Everything else still works.
