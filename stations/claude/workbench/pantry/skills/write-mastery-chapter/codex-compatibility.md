# Codex compatibility layer

This file is an adapter for running `write-mastery-chapter` with Codex. It does not replace or
weaken `SKILL.md` or anything in `reference/`. Treat the original skill as the canonical
pedagogical and LaTeX specification; use this file only to translate Claude-specific execution
language into Codex's tools and operating habits.

## Scope of this layer

- Preserve the real chapter rules exactly as written in `SKILL.md`, `reference/pedagogy-cycle.md`,
  `reference/design-system.md`, `reference/latex-scaffolding.md`, and
  `reference/visual-intuition.md`.
- Do not rewrite the skill's pedagogy, LaTeX house style, coverage rules, or verification gates
  just because Codex has different agent names.
- When a conflict appears, the original skill wins for content and quality requirements; this
  file wins only for how Codex should dispatch, supervise, and report work.

## Agent translation

The skill uses Claude-oriented language such as `general-purpose agent` and "dispatch". In
Codex, translate that as follows:

| Skill wording | Codex behavior |
| --- | --- |
| `general-purpose agent` for grounding | Spawn an `explorer` subagent. The task is read-only and narrowly scoped. |
| Quick fact-check dispatch | Spawn or reuse an `explorer` with the exact factual question and required sources. |
| Authoring agent | Spawn a `worker` only after the Mode A plan gate has been approved. |
| Dispatch one stage at a time | Send one bounded task at a time to the worker: opening, then one paragraph, then closing material. |
| Orchestrator | The main Codex agent in the user conversation. It owns gates, checks, integration, and final reporting. |

Whenever a subagent touches code or files, give it an explicit ownership boundary and remind it
that it is not alone in the codebase: it must not revert or overwrite unrelated edits, and it
must adapt to changes made by others.

## Grounding dispatch template

For grounding or fact-checking, Codex should use an `explorer` with a prompt like this:

```text
Read-only grounding pass for the write-mastery-chapter skill.

Question:
<specific subject or fact-check question>

Sources to inspect:
<vault/schema path, input folders, earlier chapters, or named files>

This pass is read-only. The agent must never write, move, or delete anything in the vault or
in any project file. If it finds something worth permanently recording, it reports that as a
gap for a separate, deliberate follow-up. It does not act on it itself.

Return:
- findings with source paths/pages/sections
- contradictions or uncertainty
- gaps where no source was found
- suggested implications for the chapter plan
```

Use web search only when the project sources and vault do not answer the question, or when the
user explicitly asks for outside sources. Prefer primary or authoritative sources for technical
facts.

## Supervised authoring in Codex

The anti-drift rule in `SKILL.md` is mandatory. Codex should not ask one worker to write a whole
chapter unattended.

After the user approves the Mode A plan:

1. Spawn or resume one `worker` for the opening stage only.
2. Review the changed files yourself.
3. Run the chapter checker yourself.
4. Build the PDFs when the stage is buildable.
5. Render and inspect the required pages yourself.
6. Send corrections for that same stage until it passes.
7. Only then dispatch the next paragraph stage.

The worker's report is useful context, not proof. The main Codex agent must run and read the
checks directly, including:

- `reference/check-chapter.py`
- LaTeX build logs
- Contents page fit
- Legend page rendering
- one Theory box, one exercise run, and one V exercise per paragraph stage
- source coverage rows in `<name>-coverage.md`

If any stage fails, do not treat it as a later cleanup item. Fix that stage before moving on.

## Mode A gates

The Mode A plan gate remains a hard stop. Codex may do inventory, grounding, source reading,
and plan drafting before the gate. It must not start authoring the chapter source until the user
explicitly approves the plan.

If the user says "run straight through", interpret that as waiving repeated user approvals after
the plan, not as permission to skip orchestrator review between stages.

## Mode B gates

For confusion-driven updates:

- Small in-place repairs can be edited directly.
- Structural changes still need a brief plan and explicit user approval before editing.
- Rebuild and run the relevant checks after editing.
- Apply the same humanize requirement to new or changed prose.

## Humanize requirement

`SKILL.md` requires a `humanize` sub-skill. If Codex has a `humanize` skill installed, use it
after the content is technically correct.

If no `humanize` skill is available, Codex should do a manual humanize pass instead:

- remove em dashes
- remove AI-tell phrasing such as "it is important to note"
- keep meaning, math, labels, references, and exercise intent unchanged
- prefer direct, natural sentences
- preserve the chapter's language choice

Do not run this pass before the math and structure are correct.

## Codex-specific operational notes

- Use `rg` where available; if it is not installed, use `grep` or `find`.
- Use `apply_patch` for manual edits.
- Do not modify files outside the intended chapter folder, coverage file, or this skill's
  explicitly copied support files unless the user asks.
- Keep generated chapters in `lessons/` unless the user names another location.
- Respect existing uncommitted user changes. Never revert unrelated edits.
- If a command fails because a dependency is missing, report the missing dependency and, when
  appropriate, request permission before installing anything.

## Minimal invocation reminder for Codex

When asked to use this skill, Codex should first read:

1. `SKILL.md`
2. this `codex-compatibility.md`
3. the reference files named by `SKILL.md` for the selected mode

Then proceed according to Mode A or Mode B. This compatibility layer is only a bridge between
agent systems; it is not a shortcut around the chapter specification.
