---
name: vault-summarize
description: Deep-extract one or more .vault/raw/ sources into concept-level wiki/summaries/ notes via parallel subagents, richly tagged for fast lookup. Run after /vault-inbox has created the raw stubs.
metadata:
  author: salomepoulain
  source: makery-bakery
---

# /vault-summarize: deep-extract raw sources into wiki/summaries/

## Preflight: confirm the vault (do this before anything else)

1. Look for `.vault/` at the repo root (it may be a symlink into a shadow dir, that's fine,
   follow it). If the user names a specific vault/path, use that instead.
2. **If no `.vault/` exists, stop here.** Don't create one, don't guess a structure, don't treat
   some other folder as a vault; scaffolding a vault is a separate concern (the `vault`
   makery station's job, not this skill's). Tell the user there's no vault and ask how they want
   to proceed.
3. Read `<vault>/<PREFIX>-schema.md`; every vault has exactly one, and it's the concrete source
   of truth for that specific vault. The prefix is whatever that file uses (e.g. `sol-`); don't
   assume it.
4. From the schema, actually understand what the vault is composed of before touching anything:
   its layers (`raw/` ground-truth sources + stubs, `wiki/summaries/` AI-written extractions,
   `wiki/atomic/` human-only notes, `wiki/maps/` MOCs/mastery dashboards, `wiki/lessons/`
   teaching transcripts where present, `inbox/` the unsorted drop zone), which of those this
   skill may touch, and its hard rules (no unconfident writeback, no AI writes to
   `wiki/atomic/`, etc.), not just enough to satisfy a frontmatter format.

Figure out which raw source(s) to summarize from the args: a specific `raw/<PREFIX>-*.md` stub
name or two, or "all" / no args meaning every raw source that doesn't yet have any
`wiki/summaries/<PREFIX>-<code>-*.md` notes.

For each source, assign it a short lowercase code for filenames (initials of the title/author are
fine, e.g. a book called "Advances in Financial Machine Learning" → `afml`), keeping codes short
and collision-free across the batch.

## Dispatch one subagent per source, in parallel

Don't do the deep reading yourself; spawn a `general-purpose` agent per source (one message,
multiple parallel Agent calls). Each is a fresh agent with no context, so brief it fully:

- Point it at the schema file (must read first), the source's raw stub + PDF/file path, and its
  short code.
- Task 1 (if the raw stub doesn't already have one): add a `## Contents` section: real
  chapter/section titles + page numbers, from actually reading the front matter.
- Task 2: read the ENTIRE source (large PDFs: `Read` with `pages`, max 20/call; it renders
  pages visually, trust it for formulas/diagrams, no separate screenshot step needed). Cover
  every substantive chapter (the user wants full coverage including niche/edge-case material,
  not just headline ideas), but it's fine to move quickly through boilerplate (front matter,
  bibliography, index, repetitive exercises).
- For each distinct concept/technique (not one giant note per chapter; split a dense chapter
  into several notes; merge only genuinely inseparable ideas), write one note into
  `wiki/summaries/<PREFIX>-<code>-<topic-slug>.md` with the schema's exact frontmatter
  (`type: summary`, `sources:` back to the raw stub id/resource, `generated: {by: claude-sonnet-5,
  date: <today>}`, `verified: false`).
- **Tags are the whole point: be generous and specific.** The actual named technique/formula/
  term from the source, not generic category labels, so a specific future question resolves
  straight to the right note. Add 1-2 broader category tags too, for cross-cutting search.
- Every note body ends with the hub-link: `Source: [[<raw-stub-name>]] (p. X–Y)`.
- Hard rule: if a passage is unclear/OCR-garbled/uncertain, say so explicitly in the note rather
  than smoothing over it; an unconfident guess filed as fact becomes a future false "source of
  truth."
- **Folder guardrail (hard constraint, state it verbatim in every dispatch prompt: learned the
  hard way):** the agent may ONLY read/write inside: its one assigned `raw/<PREFIX>-<slug>.pdf`
  (or other source file), its one assigned `raw/<PREFIX>-<slug>.md` stub, and
  `wiki/summaries/<PREFIX>-<code>-*.md`. It must NEVER browse, search, or read/write ANY other
  path: not other folders in the vault, not Downloads, not other drives, not the web, not other
  raw sources. It must NOT delete, move, or replace the raw stub or source file. If it decides
  mid-task that its assigned source is inadequate (wrong edition, condensed notes instead of the
  real text, corrupted, etc.), it must say so clearly in its final report and STOP; never go
  looking for a "better" file itself. A subagent went hunting on local disk, swapped in a
  different book, and deleted the original source + 13 already-written notes without asking;
  don't let that happen again.
- Tell it NOT to touch `<PREFIX>-index.md` or `<PREFIX>-log.md`; that's done centrally after all
  subagents finish, to avoid concurrent-write conflicts.
- Ask for a final report under 300 words: every note filename created, whether the source is
  fully covered or what remains (large sources: a partial pass with a clearly flagged remainder
  is fine, better than rushing or fabricating completeness), and any confidence caveats.

For a very large source (~500+ pages), consider having that one subagent split ITS OWN reading
into several of its own child agents by chapter range, but if it does, tell it to verify full
coverage and fill any gaps itself afterward rather than just idly polling/waiting on children
(polling in a loop burns a large amount of budget for no progress; seen this happen).

## Handling failures (rate limits happen)

If a subagent's task notification comes back `failed` (commonly an API rate-limit / spend-limit
error), don't just leave it; once the limit resets:

1. Try `SendMessage` to its `agentId` telling it to resume exactly where it left off (its own
   last status usually says what it was about to do). This works if its transcript is still
   live.
2. If that comes back "No transcript found" (transcript expired/GC'd), relaunch a **fresh**
   agent for that source instead. Brief it that a previous agent already made real progress:
   have it `ls wiki/summaries/<PREFIX>-<code>-*.md` itself first to see what's already on disk,
   and continue from there; never restart a source from scratch if notes already exist for it.

## Bookkeeping (do this yourself, once, after subagents finish)

- Update `<PREFIX>-index.md` under `## wiki/summaries/` with the new notes (or just point at the
  count/topics if there are many).
- Append one `<PREFIX>-log.md` entry: `## [YYYY-MM-DD] ingest | summarize <source(s)>` noting
  what was extracted and any gaps/caveats subagents flagged (including the scope-guardrail kind:
  if an agent reports a source is inadequate, that's a decision for the user, not something to
  resolve silently).

## Report back

Per source: note count, full/partial coverage, and anything flagged (uncertain transcriptions,
inadequate source material, gaps still open).
