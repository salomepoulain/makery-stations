# VS Code pantry

My VS Code setup in three packs. There are no keys, SSH hosts or machine paths in here, so you can use it anywhere.

| Folder | When | What |
|---|---|---|
| `style/` | always | theme, icons, colors, fonts, layout, Error Lens, file nesting |
| `functionality/` | always | autosave, editor behavior, tabs, git, terminal, privacy, Todo+, Remote SSH |
| `addons/` | per project | Python, Pylance, Ruff, Jupyter, Data Wrangler, TOML |

Each pack has a `settings.json` and an `extensions.json`. Copy `functionality/.editorconfig` to the root of a project and the EditorConfig extension reads it. Inside each file, every extension has its own `// MARK:` section.

## Install with the script

If you have Python 3, run this in this folder:

```bash
python3 install.py                      # all three
python3 install.py style functionality  # without addons
```

On Windows the command is often `python` instead of `python3`. The script:

1. backs up your user `settings.json` (`settings.json.bak-<date>`),
2. writes the packs into it, keeping their MARK sections. Existing keys that are also in the pantry get overwritten. Your other settings go at the bottom under `your own settings`. Comments from your old file are lost, but they are still in the backup.
3. installs the fonts from `fonts/` (only with `style`),
4. installs the extensions with `code --install-extension`.

## Install by hand

No Python? Then do the same three steps yourself. It takes a few minutes.

### 1. Fonts

Do this first, so VS Code picks them up on the next start.

- **macOS:** select all `.ttf` files in `fonts/`, double-click and choose "Install". Or drag them to `~/Library/Fonts`.
- **Windows:** select all `.ttf` files in `fonts/`, right-click and choose "Install". Don't choose "Install for all users", that needs admin rights.
- **Linux:** copy them to `~/.local/share/fonts` and run `fc-cache -f`.

### 2. Extensions

Open a terminal in this folder.

macOS and Linux:

```bash
grep -hoE '"[a-z0-9-]+\.[a-z0-9-]+"' */extensions.json | tr -d '"' | xargs -n1 code --install-extension
```

Windows (PowerShell):

```powershell
Select-String -Path */extensions.json -Pattern '"([a-z0-9-]+\.[a-z0-9-]+)"' -AllMatches | % { $_.Matches } | % { code --install-extension $_.Groups[1].Value }
```

To skip `addons`, replace `*/extensions.json` with `style/extensions.json, functionality/extensions.json` (PowerShell) or `style/extensions.json functionality/extensions.json` (bash).

Does `code` not work in your terminal? Then open the Extensions sidebar in VS Code, search for each name in the `extensions.json` files and click "Install".

### 3. Settings

1. In VS Code, open the Command Palette (`Cmd+Shift+P` or `Ctrl+Shift+P`) and choose "Preferences: Open User Settings (JSON)".
2. Copy what's in there somewhere safe, as a backup.
3. Paste the contents of `style/settings.json`. Then copy only what's between the outer `{` and `}` of `functionality/settings.json` and `addons/settings.json`, and paste it after that. Put a comma between the blocks.
4. Already had settings? Keep them, but remove keys that now appear twice. VS Code underlines duplicate keys.
5. Save and restart VS Code.

Extensions for just one project? Put `addons/extensions.json` in that project as `.vscode/extensions.json`. VS Code will then recommend the extensions itself.

## Fonts

The fonts are in `fonts/`, as `.ttf` for macOS, Windows and Linux. `install.py` installs them for your own user when you include the `style` pack; by hand it works as described above. Neither needs admin rights. Restart VS Code afterwards. Licenses are in `fonts/LICENSES.md`.

Install them on the machine where VS Code runs, not on a remote server.

- Fira Code: editor, terminal, debug console
- Cascadia Code: Error Lens messages
- CMU Serif or STIX Two Text: markdown cells in notebooks
- MesloLGM Nerd Font Mono: terminal fallback for prompt icons

## Notes

- Flow Icons is paid. The license key is deliberately not in here. Put `flow-icons.licenseKey` in your own user settings.
- `community.notebook-minimap` is my own extension (github.com/salomepoulain/vscode-notebook-minimap). If it's not in the marketplace of a locked-down environment, install it as a `.vsix`.
- Without Jupyter from `addons/`, the notebook settings in `style/` do nothing. Everything else still works.
