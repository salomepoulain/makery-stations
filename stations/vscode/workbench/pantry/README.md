# VS Code pantry

Mijn VS Code-setup in drie pakketten. Er staan geen keys, SSH-hosts of machinepaden in, dus je kunt het overal gebruiken.

| Map | Wanneer | Wat |
|---|---|---|
| `style/` | altijd | thema, iconen, kleuren, fonts, layout, Error Lens, file nesting |
| `functionality/` | altijd | autosave, editor-gedrag, tabs, git, terminal, privacy, Todo+, Remote SSH |
| `addons/` | per project | Python, Pylance, Ruff, Jupyter, Data Wrangler, TOML |

Elk pakket heeft een `settings.json` en een `extensions.json`. `functionality/.editorconfig` kopieer je naar de root van een project, de EditorConfig-extensie leest hem dan. Binnen een bestand heeft elke extensie een eigen `// MARK:`-sectie.

## Installeren

```bash
python3 install.py                      # alle drie
python3 install.py style functionality  # zonder addons
```

Het script:

1. maakt een backup van je user `settings.json` (`settings.json.bak-<datum>`),
2. zet de pakketten erin, met hun MARK-secties. Bestaande keys die ook in de pantry staan worden overschreven. Je andere instellingen komen onderaan onder `eigen instellingen`. Commentaar uit je oude bestand gaat verloren, dat staat nog in de backup.
3. installeert de fonts uit `fonts/` (alleen met `style`),
4. installeert de extensies met `code --install-extension`.

Het werkt op macOS, Linux en Windows en heeft alleen Python 3 nodig.

Liever met de hand? Plak een `settings.json` in "Preferences: Open User Settings (JSON)". Of zet een `extensions.json` in een project als `.vscode/extensions.json`, dan stelt VS Code de extensies zelf voor.

## Fonts

De fonts staan in `fonts/`, als `.ttf` voor macOS, Windows en Linux. `install.py` installeert ze voor je eigen gebruiker als je het `style`-pakket meeneemt. Daar zijn geen adminrechten voor nodig. Fonts die er al staan slaat het over. Herstart VS Code daarna. Licenties staan in `fonts/LICENSES.md`.

Installeer ze op de machine waar VS Code draait, niet op een remote server.

- Fira Code: editor, terminal, debug console
- Cascadia Code: Error Lens-berichten
- CMU Serif of STIX Two Text: markdown-cellen in notebooks
- MesloLGM Nerd Font Mono: terminal-fallback voor iconen in de prompt

## Let op

- Flow Icons is betaald. De license key staat hier bewust niet in. Zet `flow-icons.licenseKey` zelf in je user settings.
- `community.notebook-minimap` is een eigen extensie (github.com/salomepoulain/vscode-notebook-minimap). Staat hij niet in de marketplace van een afgeschermde omgeving, installeer hem dan als `.vsix`.
- Zonder Jupyter uit `addons/` doen de notebook-regels in `style/` niks. De rest blijft werken.
