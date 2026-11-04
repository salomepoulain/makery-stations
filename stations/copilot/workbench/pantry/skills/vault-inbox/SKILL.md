---
name: vault-inbox
description: Triage a .vault/inbox/ drop zone into raw/ stubs or wiki/summaries links, per that vault's own schema. Creates stubs only; never spawns deep-extraction subagents (that's /vault-summarize's job).
metadata:
  author: salomepoulain
  source: makery-bakery
---

# /vault-inbox: triage the vault inbox

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

For each item currently in `<vault>/inbox/` (skip `.keep`), decide where it belongs, per the
schema's "Processing the inbox" section:

1. **Genuinely a new source** (a document/transcript/book to treat as ground truth) →
   - Move the file into `raw/`, renamed to `<PREFIX>-<kebab-case-title>.<ext>` (strip junk like
     download-site hashes/suffixes from the original filename).
   - Write a lightweight stub note `raw/<PREFIX>-<slug>.md`:
     ```yaml
     ---
     type: source
     title: "Human-readable title"
     description: "One-line description of what this source covers and why it's here"
     resource: <PREFIX>-<slug>.<ext>
     tags: [<PREFIX>, <a few topic tags>]
     ---

     Source: ![[<PREFIX>-<slug>.<ext>]]
     ```
   - Also add a `## Contents` section (see the schema's "Table of contents" section for the
     exact format); read enough of the source's front matter to get its real chapter/section
     structure with page numbers. This is cheap (a handful of pages) and doesn't require the
     full deep read that `/vault-summarize` does, so do it inline yourself, no subagent.
   - If the source is clearly **assessment material** (a past exam, problem set, homework, quiz)
     rather than expository/conceptual reading, tag it distinctly (add an `exam` tag alongside
     the topic tags). It's still filed in `raw/` like any other source; the tag is just so
     `vault-teach` can find and calibrate lessons against it specifically.
   - Do NOT read the rest of the source and do NOT write anything into `wiki/summaries/`;
     that's `/vault-summarize`'s job, on purpose, so a big inbox drop doesn't silently trigger a
     huge background read.

2. **An extraction/summary of something already in `raw/`** → write it into `wiki/summaries/`
   directly (it's already synthesized, no need to defer), following the schema's frontmatter and
   hub-linking rules.

3. **Too thin to confidently place** (a stray thought, ambiguous screenshot, not enough context)
   → leave it in `inbox/`, don't guess, and ask the user about it in your final report.

4. **Never `wiki/atomic/`**: human-written only. Surface it back instead.

Once an item is triaged (moved, or explicitly discarded as noise with the user's OK), remove it
from `inbox/`.

## Bookkeeping (do this yourself, no subagents needed for triage)

- Update `<PREFIX>-index.md`: add one line per new `raw/` and `wiki/summaries/` entry under the
  right heading.
- Append one entry to `<PREFIX>-log.md`: `## [YYYY-MM-DD] ingest | inbox batch (N items)` with a
  short list of what got filed where.

## Folder guardrail

If any of this triage work is ever delegated to a subagent, it must be scoped to ONLY
`inbox/`, the one raw file/stub it's placing, and `wiki/summaries/` for direct-summary items;
never allowed to browse Downloads, other drives, the web, or other vault folders looking for
"better" material on its own initiative. See `/vault-summarize`'s guardrail for why this is a
hard rule, not a suggestion.

## Report back

List what got filed where (new raw sources with their tags, any direct-summary items), and flag
anything left in `inbox/` because it was too thin; ask the user about those explicitly. Mention
that `wiki/summaries/` deep-extraction hasn't run yet and point at `/vault-summarize` for that.
