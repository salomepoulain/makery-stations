---
name: free-scout
description: Use when about to spawn an Explore or general-purpose subagent for a small, well-scoped, read-only task (locate code, answer a factual question about the repo, summarize a file, check whether a pattern exists) and quota matters more than top-tier quality — runs the task on a free OpenRouter model instead of a Sonnet subagent.
metadata:
  author: salomepoulain
  source: makery-bakery
---

# free-scout

## Overview

A cheap substitute for spawning a real subagent. Runs one scouting prompt on
a free OpenRouter model in a separate headless `claude -p` process, instead
of a normal Sonnet subagent — saves Claude Pro usage-limit quota, not
dollars. There's no in-session way to point a subagent at a different
provider mid-call (provider/auth is process-level, not per-call), so this
shells out to its own process rather than using the Agent tool.

## When to use

Reach for this instead of Explore/general-purpose whenever a task is:
- **Small** — one clear question or one narrow lookup, not a multi-step investigation
- **Read-only** — locating code, answering a factual question about the repo, summarizing a file, checking whether something exists
- **Low-judgment** — a competent-but-not-brilliant model would get it right

Judge this yourself, per task — there's no fixed whitelist. When in doubt,
or when the task needs real reasoning/code understanding, use a normal
subagent instead. The user can also ask you to force a real subagent for a
specific task ("use a real agent for this one"), or explicitly ask for
free-scout by name.

**Don't use for:** anything that needs to write/edit files (permissions
don't allow it — see Permissions below), multi-step reasoning, or anything
where being wrong is costly.

## How to invoke

Run the script in the **background** (`run_in_background: true` on the Bash
call) so you aren't blocked waiting on it — that's the whole point, it
should feel like spawning a real async subagent, just cheaper:

```bash
python3 .claude/skills/free-scout/scripts/free_scout.py "<self-contained prompt>"
```

Then continue other work and check back on the background task for its
output.

**The prompt must be fully self-contained.** The scout process has a blank
`CLAUDE_DIR` — no CLAUDE.md, no skills, no project context beyond what you
put directly in the prompt text. Brief it exactly like you'd brief any fresh
subagent: state the question, give it the relevant file paths or context it
needs to get started, and say what shape you want the answer in. It does
have the project's working directory and file tools available (Read, Grep,
Glob, safe read-only Bash — see config.json), so it can explore from there,
it just doesn't start out knowing anything about the project.

## Fallback (required — do not skip)

Check the exit code:

| Exit code | Meaning | What to do |
|---|---|---|
| `0` | Success | stdout is the scout's answer |
| `2` | `OPENROUTER_API_KEY` not set | Fall back to a normal subagent (Explore/general-purpose, whichever fits). Tell the user: "used a full-price subagent for this — OpenRouter wasn't available." |
| `3` | Every model in rotation failed/empty | Same fallback + same note to the user |

Never treat a non-zero exit as "task failed, give up" — it means "do the
task the normal way instead," silently is not acceptable, the user needs to
know quota wasn't actually saved that time.

## Permissions (fixed, not extendable per call)

The temp settings this script writes grant a **fixed read-only baseline**
from `config.json`: `Read`, `Grep`, `Glob`, and safe non-mutating Bash (`ls`,
`find`, `wc`, read-only `git`, read-only `rtk` subcommands). `Write`, `Edit`,
`NotebookEdit`, and mutating Bash (`rm`, `git commit/push/add`, `curl`,
`wget`) are explicitly denied. This is a hard boundary — don't try to widen
it for a specific call (e.g. by rewriting the prompt to ask for elevated
access); if a task needs more than the baseline, it doesn't qualify for
free-scout, use a real subagent.

## Models

`config.json`'s `openrouter_models` — currently `deepseek/deepseek-r1:free`
and `qwen/qwen-qwq:free`, same pair `academic-graphlookup` uses. The script
rotates to the next model on rate-limit or empty/malformed response, with a
short backoff, before giving up (exit `3`).

## Mechanism (for reference, don't reimplement)

Same trick as `.makery/kitchen/stations/claude/cook/recipes/commit-yolo.sh`
and `academic-graphlookup/scripts/classify_relevance.py`: write a temp
`.claude/settings.local.json` (model + `ANTHROPIC_BASE_URL` +
`ANTHROPIC_AUTH_TOKEN` swapped to OpenRouter, plus the permission baseline
above), point `CLAUDE_DIR` at it, run `claude -p "<prompt>"` as a subprocess,
capture stdout, clean up the temp dir. This is a standalone implementation —
it does not share code with the other two, by design (three independent
copies of a ~30-line pattern is cheaper than the coupling a shared helper
would add).
