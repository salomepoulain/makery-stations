# makery-stations

The Stations I use with [makery-bakery](https://github.com/salomepoulain/makery-bakery). Hire one
into a project with `bake first <name>`, and run its commands with `bake <name> <command>`.

| Station | What I use it for | Commands |
|---|---|---|
| `claude` | Sets up Claude Code in a project: `CLAUDE.local.md`, plus a `.claude/` folder with docs, skills and settings | `models`, `prompts`, `skills`, `commit-duo`, `commit-yolo`, `auto` |
| `cluster` | Working on a remote cluster: dotfiles and shell, and keeping folders in sync with a host through Mutagen | `shell`, `sync`, `shady-sync` |
| `docker` | A dev container for the project in `.docker/` | `build`, `rebuild`, `run`, `clean` |
| `github` | Creates the project's GitHub repo and its `.gitignore` | `repo`, `match`, `public`, `private`, `gitignore` |
| `latex` | A `report/` folder with writing guides, and compiling `main.tex` to a PDF | `report` |
| `python` | Python with uv: ignores and cleans up caches like `__pycache__` and `.ruff_cache` | none yet |
| `vault` | A knowledge vault in `.vault/` (sources, summaries, notes and maps), which can also be shared between projects | `shady`, `perma`, `permanent`, `decouple`, `undo` |
| `vscode` | Templates for a VS Code dev container and settings, kept for reference | `container-style` |

Plain `bake` lists every hired Station's commands with a short description.

Commands that push or publish (`claude commit-yolo`, `claude commit-duo`, `github repo`,
`github public` and `github private`) only run from a real terminal, so an agent can't run them
for you. Hiring `github` without a terminal sets up git but leaves creating the GitHub repo to you.

## Adding or changing a Station

Make it in your own project with `bake station <name>`, try it with `bake first <name>`, and send
it here with `bake request`. If you can't write to this repo, `bake request` forks it for you and
opens a pull request from your fork.
