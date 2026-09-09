# Makery-Stations: Knowledge Base for Claude

> **Purpose**: This document provides comprehensive context about the makery-stations project so Claude can understand the architecture, conventions, and purpose of this codebase.

## What is Makery?

**Makery** is a station-based build and configuration system built on top of `make`. It's designed to organize complex projects into modular, reusable "stations" — each station is a self-contained component with its own configuration, recipes (tasks), and workbench (execution environment).

**Key Repository**: [multi-makery](https://github.com/salomepoulain/multi-makery) — the core system that makery-stations is built upon.

## Project Structure: Makery-Stations

This project (`makery-stations`) is a **collection of stations** that extend the makery system. Each station represents a distinct tool, service, or integration point.

### Directory Layout

```
makery-stations/
├── stations/                    # Active stations in this project
│   └── claude/                  # Claude AI integration station
│       ├── menu.mk              # Main menu/entry point
│       ├── cook/                # Station recipes and configuration
│       │   ├── personality.sh   # Station personality/metadata
│       │   ├── contract/        # Lifecycle hooks (hired/fired)
│       │   └── skills/          # Executable skills (tasks)
│       └── workbench/           # Execution environment
│           ├── .contraband      # Shady-stash list (moved into __stash__, symlinked back)
│           ├── .countertop      # Gitignore-only list (stays local, never stashed)
│           ├── .dishsoap        # Files/dirs to clean up after tasks (bake germs)
│           ├── .tools           # System-tool dependencies checked before hiring
│           └── pantry/          # Shared configurations & knowledge
│               ├── settings/    # Configuration files (JSON, merged into settings.local.json)
│               ├── prompts/     # CLAUDE.md modular sections
│               ├── docs/        # Claude-specific knowledge (this folder)
│               ├── skills/      # SKILL.md dirs, deployed to .claude/skills/
│               ├── commands/    # Slash-command .md files, deployed to .claude/commands/
│               └── statusline.sh # Deployed to .claude/statusline.sh
├── .makery/                     # Makery kitchen (system files)
└── CLAUDE.md                    # Generated Claude instructions
```

## The Claude Station

The **claude station** is a station that integrates Claude Code (Claude's CLI environment) into the makery system. It handles:

- **Personality**: Defines how the station behaves and what it's for
- **Recipes**: Executable tasks (scripts, shell commands, operations)
- **Contract**: Lifecycle events (what runs when the station is "hired" or "fired")
- **Workbench**: The environment where recipes execute
- **Pantry**: Shared knowledge, settings, and configurations

### Key Files in Claude Station

| File | Purpose |
|------|---------|
| `menu.mk` | Main entry point; defines available commands |
| `cook/personality.sh` | Station metadata (name, description, version) |
| `cook/contract/hired.sh` | Runs when station is initialized |
| `cook/contract/fired.sh` | Runs when station is torn down |
| `cook/skills/*.sh` | Individual task scripts |
| `workbench/pantry/settings/` | Persistent configuration (permissions, sandbox, statusline, mcp) |
| `workbench/pantry/prompts/` | CLAUDE.md sections (modular instructions) |
| `workbench/pantry/docs/` | Knowledge base for Claude (this folder) |
| `workbench/pantry/skills/` | Project-local skills (deployed to `.claude/skills/`) |
| `workbench/pantry/commands/` | Project-local slash commands (deployed to `.claude/commands/`) |
| `workbench/pantry/statusline.sh` | Statusline script (deployed to `.claude/statusline.sh`) |

## The Workbench & Pantry

### Workbench
The **workbench** is the execution environment for the station. It's where recipes run and where temporary files live.

- `.contraband` — Files/patterns that get moved into `__stash__` and symlinked back when the project "goes shady" (e.g. `CLAUDE.local.md`)
- `.countertop` — Files/patterns that just get gitignored, never stashed (e.g. local backups)
- `.dishsoap` — Files/directories to clean up after each task execution (`bake germs`); also unioned into `.gitignore`
- `.tools` — System-level commands that must be installed for this station to work

### Pantry
The **pantry** is the persistent knowledge store for the station. It contains:

- **settings/** — Configuration files (permissions, sandbox rules, statusline, mcp), merged into
  `.claude/settings.local.json`
- **prompts/** — Modular CLAUDE.md sections that define Claude's instructions
- **docs/** — Knowledge base and context documents for Claude
- **skills/** — Project-local `SKILL.md` directories, deployed verbatim to `.claude/skills/`
- **commands/** — Project-local slash-command `.md` files, deployed verbatim to `.claude/commands/`
- **statusline.sh** — Statusline script, deployed to `.claude/statusline.sh`

## How Claude Uses This Knowledge

When Claude executes in this workbench, it has access to:

1. **CLAUDE.md** — Generated from pantry/prompts sections; defines behavioral guidelines
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
Files matching patterns in `.contraband` get moved into `__stash__` (outside the repo) and
symlinked back when the project goes shady, so they travel with you across machines without
ever being tracked by git. Common examples:
- Personal instructions: `CLAUDE.local.md`
- Local settings: `settings.local.json`, `.claude`

Anything that should just be gitignored and left alone (build artifacts, backups) belongs in
`.countertop` instead - see below.

## Common Patterns

### Running Recipes
Recipes are typically invoked via `make` or directly:
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

### Modifying Prompts
CLAUDE.md sections in `prompts/` are modular and composable:
- `intro_arc/` — Architecture and structure
- `intro_repo/` — Repository-specific context
- `role/` — Behavioral guidance (karpathy, etc.). Tutor persona lives in `commands/tutor.md` instead — it's session-scoped, not a permanent CLAUDE.md role.

Rebuild CLAUDE.md with: `bake call s=claude d=prompts`

## Important Files to Know

| Path | Purpose |
|------|---------|
| `stations/claude/menu.mk` | Station menu and available commands |
| `CLAUDE.md` | Generated instructions for Claude (regenerate after changes) |
| `.contraband` | Shady-stash patterns (moved into `__stash__`, symlinked back) |
| `.countertop` | Gitignore-only patterns (never stashed) |
| `.dishsoap` | Cleanup patterns (also unioned into `.gitignore`) |
| `multi-makery` repo | Core makery system (referenced via sync-template.sh) |

## Common Tasks

### Add a New Skill
1. Create `stations/claude/cook/skills/my-skill.sh`
2. Make it executable: `chmod +x`
3. Add entry to `menu.mk` if needed
4. Skill is now available

### Update Claude's Instructions
1. Edit relevant file in `stations/claude/workbench/pantry/prompts/`
2. Rebuild CLAUDE.md: `bake call s=claude d=prompts`
3. Select your preferred sections (intro_arc, intro_repo, role)

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

**Last Updated**: 2026-05-07
**For**: Claude Code and Claude-based automation