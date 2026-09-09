# Makery-Stations: Knowledge Base for Claude

> **Purpose**: This document provides comprehensive context about the makery-stations project so Claude can understand the architecture, conventions, and purpose of this codebase.

## What is Makery?

**Makery** is a station-based build and configuration system built on top of `make`. It's designed to organize complex projects into modular, reusable "stations" — each station is a self-contained component with its own configuration, skills (tasks), and workbench (execution environment).

**Key Repository**: [makery-bakery](https://github.com/salomepoulain/makery-bakery) — the core system (Head Chef + Station templates) that makery-stations is built upon.

## Project Structure: Makery-Stations

This project (`makery-stations`) is a **collection of stations** that extend the makery system. Each station represents a distinct tool, service, or integration point.

### Directory Layout

```
makery-stations/
├── stations/                    # Active stations in this project
│   └── claude/                  # Claude AI integration station
│       ├── menu.mk              # Main menu/entry point
│       ├── cook/                # Station skills and configuration
│       │   ├── personality.sh   # Station personality/metadata
│       │   ├── contract/        # Lifecycle hooks (hired/fired/illegal)
│       │   └── skills/          # Executable skills (tasks)
│       └── workbench/           # Execution environment
│           ├── .contraband      # Shady-stash list (moved into ~/.shadow/, symlinked back as __stash__)
│           ├── .countertop      # Gitignore-only list (stays local, never stashed)
│           ├── .dishsoap        # Files/dirs to clean up after tasks (bake germs)
│           ├── .tools           # System-tool dependencies checked before hiring
│           └── pantry/          # Shared configurations & knowledge, unpacked by hired.sh
│               ├── settings/    # Configuration files (JSON, merged into settings.local.json)
│               ├── CLAUDE.local.md # Behavioral instructions, copied verbatim to the project root
│               ├── docs/        # Claude-specific knowledge (this folder), copied to .claude/docs/
│               ├── skills/      # SKILL.md dirs, deployed to .claude/skills/
│               ├── commands/    # Slash-command .md files, deployed to .claude/commands/
│               └── statusline.sh # Deployed to .claude/statusline.sh
└── .gitignore
```

## The Claude Station

The **claude station** is a station that integrates Claude Code (Claude's CLI environment) into the makery system. It handles:

- **Personality**: Defines how the station behaves and what it's for
- **Skills**: Executable tasks (scripts, shell commands, operations)
- **Contract**: Lifecycle events (what runs when the station is "hired", "fired", or when the project goes shady)
- **Workbench**: The environment where skills execute
- **Pantry**: Shared knowledge, settings, and configurations

### Key Files in Claude Station

| File | Purpose |
|------|---------|
| `menu.mk` | Main entry point; defines available commands |
| `cook/personality.sh` | Station metadata (name, description, version) |
| `cook/contract/hired.sh` | Runs when station is initialized |
| `cook/contract/fired.sh` | Runs when station is torn down |
| `cook/contract/illegal.sh` | Runs when the project goes shady (optional) |
| `cook/skills/*.sh` | Individual task scripts |
| `workbench/pantry/settings/` | Persistent configuration (permissions, sandbox, statusline, mcp), merged into `.claude/settings.local.json` |
| `workbench/pantry/CLAUDE.local.md` | Behavioral instructions, copied once to the project root as `CLAUDE.local.md` |
| `workbench/pantry/docs/` | Knowledge base for Claude (this folder) |
| `workbench/pantry/skills/` | Project-local skills (deployed to `.claude/skills/`) |
| `workbench/pantry/commands/` | Project-local slash commands (deployed to `.claude/commands/`) |
| `workbench/pantry/statusline.sh` | Statusline script (deployed to `.claude/statusline.sh`) |

## The Workbench & Pantry

### Workbench
The **workbench** is the execution environment for the station. It's where skills run and where temporary files live.

- `.contraband` — Files/patterns that get moved into `~/.shadow/` and symlinked back (as `__stash__`) when the project "goes shady" (e.g. `CLAUDE.local.md`). Everything here must also be listed in `.countertop`.
- `.countertop` — The sole source of truth for `.gitignore`, written by hand. Duplicate in anything from `.contraband` or `.dishsoap` that also needs gitignoring - no automatic union, on purpose.
- `.dishsoap` — Files/directories to clean up after each task execution (`bake germs`)
- `.tools` — System-level commands that must be installed for this station to work

### Pantry
The **pantry** is the persistent knowledge store for the station. It contains:

- **settings/** — Configuration files (permissions, sandbox rules, statusline, mcp), merged into
  `.claude/settings.local.json`
- **CLAUDE.local.md** — A single file holding Claude's behavioral instructions, split into `## SECTION: <name>` blocks (e.g. `intro_arc`, `role`). `hired.sh` copies it verbatim to the project root the first time the station is hired, if it already exists there it's left alone.
- **docs/** — Knowledge base and context documents for Claude
- **skills/** — Project-local `SKILL.md` directories, deployed verbatim to `.claude/skills/`
- **commands/** — Project-local slash-command `.md` files, deployed verbatim to `.claude/commands/`
- **statusline.sh** — Statusline script, deployed to `.claude/statusline.sh`

## How Claude Uses This Knowledge

When Claude executes in this workbench, it has access to:

1. **CLAUDE.local.md** — Deployed from `pantry/CLAUDE.local.md`; defines behavioral guidelines
2. **Docs folder** — This knowledge base; provides context about the makery system
3. **Project files** — All files in the workbench

The docs folder is designed to be **copied and pasted** into Claude prompts so Claude always understands the full architectural context of the project.

## Key Conventions

### Station Names
Stations follow the pattern of simple, lowercase names: `claude`, `git`, etc.

### Skills (Tasks)
Each skill is a shell script in `cook/skills/` that:
- Is executable (`chmod +x`)
- Starts with a shebang (`#!/usr/bin/env bash`)
- Can accept arguments
- Should log its progress to stdout

### Contraband (shady-stash)
Files matching patterns in `.contraband` get moved into `~/.shadow/` (outside the repo) and
symlinked back locally as `__stash__` when the project goes shady, so they travel with you across
machines without ever being tracked by git. Common examples:
- Personal instructions: `CLAUDE.local.md`
- Local settings: `settings.local.json`, `.claude`

Anything that should just be gitignored and left alone (build artifacts, backups) belongs in
`.countertop` instead - see below.

## Common Patterns

### Running Skills
Skills are typically invoked via `make` or directly:
```bash
bake call s=claude d=skills   # List available skills
./stations/claude/cook/skills/skills.sh  # Run a specific skill
```

### Adding Knowledge
New knowledge documents should:
- Be placed in `stations/claude/workbench/pantry/docs/`
- Be well-organized with clear sections
- Include examples and cross-references
- Be written for **Claude's understanding**, not human documentation

### Updating behavioral instructions
`CLAUDE.local.md` is one file, not a build step. There's no `prompts/` directory and no rebuild
command:
- `intro_arc` — Architecture and structure
- `role` — Behavioral guidance
- Tutor persona lives in `commands/tutor.md` instead — it's session-scoped, not a permanent
  `CLAUDE.local.md` section.

Edit `stations/claude/workbench/pantry/CLAUDE.local.md` directly, then, since `hired.sh` only
copies it to the project root the first time (it won't overwrite an existing one), copy your
edited version over the project's `CLAUDE.local.md` by hand to pick up the change there.

## Important Files to Know

| Path | Purpose |
|------|---------|
| `stations/claude/menu.mk` | Station menu and available commands |
| `CLAUDE.local.md` (project root) | Deployed instructions for Claude, edit the pantry copy and re-deploy to change it |
| `.contraband` | Shady-stash patterns (moved into `~/.shadow/`, symlinked back as `__stash__`) |
| `.countertop` | Gitignore-only patterns (never stashed) |
| `.dishsoap` | Cleanup patterns |
| `makery-bakery` repo | Core makery system (Head Chef, Station templates) |

## Common Tasks

### Add a New Skill
1. Create `stations/claude/cook/skills/my-skill.sh`
2. Make it executable: `chmod +x`
3. Add entry to `menu.mk` if needed
4. Skill is now available

### Update Claude's Instructions
1. Edit `stations/claude/workbench/pantry/CLAUDE.local.md` directly (it's the single source, organized by `## SECTION:` blocks)
2. Copy it over the project's `CLAUDE.local.md` by hand, `hired.sh` won't overwrite an existing one

### Add Knowledge for Claude
1. Create new `.md` file in `stations/claude/workbench/pantry/docs/`
2. Claude will reference it in future context
3. Restart or paste explicitly to activate

## Quick Reference

- **What is this?** A makery-based project with modular stations, currently featuring Claude integration
- **Where is Claude?** `stations/claude/`
- **Where are skills?** `stations/claude/cook/skills/`
- **Where is configuration?** `stations/claude/workbench/pantry/settings/`
- **Where is knowledge?** `stations/claude/workbench/pantry/docs/`
- **What's the entry point?** `stations/claude/menu.mk`

---

**Last Updated**: 2026-09-09
**For**: Claude Code and Claude-based automation
