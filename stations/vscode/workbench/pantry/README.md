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

## Shell

The cluster shell config (lsd-style `ls`, Powerlevel10k-style prompt) is its own station now: `bake first shell`. It needs the MesloLGM Nerd Font from `fonts/` for its icons.

## Notes

- `makery-kitchen-explorer-<version>.vsix` in this folder is the makery-kitchen-explorer extension, for a machine without a marketplace. After `bake first vscode`, right-click it in `.makery/stations/vscode/workbench/pantry/` and choose "Install Extension VSIX".
- Flow Icons is paid. The license key is deliberately not in here. Put `flow-icons.licenseKey` in your own user settings.
- `community.notebook-minimap` is my own extension (github.com/salomepoulain/vscode-notebook-minimap). If it's not in the marketplace of a locked-down environment, install it as a `.vsix`.
- Without Jupyter from `addons/`, the notebook settings in `style/` do nothing. Everything else still works.
