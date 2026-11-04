# VS Code pantry

Mijn VS Code-setup in drie pakketten. Er staan geen keys, SSH-hosts of machinepaden in, dus je kunt het overal gebruiken.

| Map | Wanneer | Wat |
|---|---|---|
| `style/` | altijd | thema, iconen, kleuren, fonts, layout, Error Lens, file nesting |
| `functionality/` | altijd | autosave, editor-gedrag, tabs, git, terminal, privacy, Todo+, Remote SSH |
| `addons/` | per project | Python, Pylance, Ruff, Jupyter, Data Wrangler, TOML |

Elk pakket heeft een `settings.json` en een `extensions.json`. `functionality/.editorconfig` kopieer je naar de root van een project, de EditorConfig-extensie leest hem dan. Binnen een bestand heeft elke extensie een eigen `// MARK:`-sectie.

## Installeren met het script

Heb je Python 3, draai dan in deze map:

```bash
python3 install.py                      # alle drie
python3 install.py style functionality  # zonder addons
```

Op Windows heet het vaak `python` in plaats van `python3`. Het script:

1. maakt een backup van je user `settings.json` (`settings.json.bak-<datum>`),
2. zet de pakketten erin, met hun MARK-secties. Bestaande keys die ook in de pantry staan worden overschreven. Je andere instellingen komen onderaan onder `eigen instellingen`. Commentaar uit je oude bestand gaat verloren, dat staat nog in de backup.
3. installeert de fonts uit `fonts/` (alleen met `style`),
4. installeert de extensies met `code --install-extension`.

## Installeren met de hand

Geen Python? Dan doe je dezelfde drie stappen zelf. Het kost een paar minuten.

### 1. Fonts

Doe dit eerst, dan ziet VS Code ze meteen bij de volgende start.

- **macOS:** selecteer alle `.ttf`-bestanden in `fonts/`, dubbelklik en kies "Installeer". Of sleep ze naar `~/Library/Fonts`.
- **Windows:** selecteer alle `.ttf`-bestanden in `fonts/`, rechtsklik en kies "Installeren". Kies niet "Installeren voor alle gebruikers", daar heb je adminrechten voor.
- **Linux:** kopieer ze naar `~/.local/share/fonts` en draai `fc-cache -f`.

### 2. Extensies

Open een terminal in deze map.

macOS en Linux:

```bash
grep -hoE '"[a-z0-9-]+\.[a-z0-9-]+"' */extensions.json | tr -d '"' | xargs -n1 code --install-extension
```

Windows (PowerShell):

```powershell
Select-String -Path */extensions.json -Pattern '"([a-z0-9-]+\.[a-z0-9-]+)"' -AllMatches | % { $_.Matches } | % { code --install-extension $_.Groups[1].Value }
```

Zonder `addons` vervang je `*/extensions.json` door `style/extensions.json, functionality/extensions.json` (PowerShell) of `style/extensions.json functionality/extensions.json` (bash).

Werkt `code` niet in je terminal? Open dan in VS Code de Extensions-zijbalk, zoek elke naam uit de `extensions.json`-bestanden op en klik "Install".

### 3. Settings

1. Open in VS Code het Command Palette (`Cmd+Shift+P` of `Ctrl+Shift+P`) en kies "Preferences: Open User Settings (JSON)".
2. Maak een kopie van wat erin staat, als backup.
3. Plak de inhoud van `style/settings.json` erin. Kopieer daarna van `functionality/settings.json` en `addons/settings.json` alleen wat tussen de buitenste `{` en `}` staat, en plak dat erachter. Zet een komma tussen de blokken.
4. Stonden er al instellingen in? Laat die staan, maar haal keys weg die nu dubbel voorkomen. VS Code onderstreept dubbele keys.
5. Sla op en herstart VS Code.

Alleen extensies voor één project? Zet `addons/extensions.json` in dat project als `.vscode/extensions.json`. VS Code stelt de extensies dan zelf voor.

## Fonts

De fonts staan in `fonts/`, als `.ttf` voor macOS, Windows en Linux. `install.py` installeert ze voor je eigen gebruiker als je het `style`-pakket meeneemt, met de hand gaat het zoals hierboven. Daar zijn geen adminrechten voor nodig. Herstart VS Code daarna. Licenties staan in `fonts/LICENSES.md`.

Installeer ze op de machine waar VS Code draait, niet op een remote server.

- Fira Code: editor, terminal, debug console
- Cascadia Code: Error Lens-berichten
- CMU Serif of STIX Two Text: markdown-cellen in notebooks
- MesloLGM Nerd Font Mono: terminal-fallback voor iconen in de prompt

## Let op

- Flow Icons is betaald. De license key staat hier bewust niet in. Zet `flow-icons.licenseKey` zelf in je user settings.
- `community.notebook-minimap` is een eigen extensie (github.com/salomepoulain/vscode-notebook-minimap). Staat hij niet in de marketplace van een afgeschermde omgeving, installeer hem dan als `.vsix`.
- Zonder Jupyter uit `addons/` doen de notebook-regels in `style/` niks. De rest blijft werken.
