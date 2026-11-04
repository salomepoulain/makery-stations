# VS Code style

Alleen opmaak: thema, iconen, kleuren, fonts, layout, Error Lens en notebooks. Geen SSH, keys, paden of taalconfig. Je kunt het dus overal plakken.

## Gebruik

1. Installeer de extensies uit `extensions.json`. Of zet het bestand in een project als `.vscode/extensions.json`, dan stelt VS Code ze zelf voor.
2. Plak `settings.json` in je user settings (`Cmd+Shift+P` > "Preferences: Open User Settings (JSON)"). Als je al eigen settings hebt, voeg je ze samen in plaats van ze te vervangen.

Alle extensies in één keer installeren:

```bash
grep -oE '"[a-z0-9-]+\.[a-z0-9-]+"' extensions.json | tr -d '"' | xargs -n1 code --install-extension
```

## Fonts

VS Code valt terug op een standaardfont als deze ontbreken:

- Fira Code: editor, terminal, debug console
- Cascadia Code: Error Lens-berichten
- CMU Serif of STIX Two Text: markdown-cellen in notebooks
- MesloLGM Nerd Font Mono: terminal-fallback voor iconen in de prompt

## Let op

- Flow Icons is betaald. De license key staat hier bewust niet in. Zet `flow-icons.licenseKey` zelf in je user settings.
- `community.notebook-minimap` is een eigen extensie (github.com/salomepoulain/vscode-notebook-minimap). Staat hij niet in de marketplace van een afgeschermde omgeving, dan installeer je hem als `.vsix`.
- De Python- en Jupyter-extensies staan in `../functionality/extensions.json`. Zonder die extensies doen de inlay hints en notebook-regels niks. De rest blijft werken.
