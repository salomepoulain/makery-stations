---
type: schema
aliases: [SCHEMA]
title: "{{PREFIX}} Vault Schema"
description: Rules for how this vault is structured and maintained.
tags: [{{PREFIX}}, meta]
---

# {{PREFIX}} Vault Schema

This vault follows [Andrej Karpathy's llm-wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
(raw sources → wiki → schema), using
[Google's Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
frontmatter conventions for interoperability.

## Layers

- **`raw/`**: real source files (PDFs, transcripts, etc.) plus a lightweight stub note per
  file. Ground truth. Nobody edits the raw files themselves; stub notes are near-static
  (frontmatter + an embed).
- **`wiki/summaries/`**: Layer 2. **AI-written only.** Faithful, structured extraction of a
  raw source: concepts, formulas, structure. Marked `generated.by` + `verified: false`.
- **`wiki/atomic/`**: Layer 3. **Human-written only.** Your own reactions, connections,
  confusions. AI does not write here: the point of this layer only holds if it's genuinely
  your own understanding, not a reflection of AI's.
- **`wiki/maps/`**: MOCs (Maps of Content). Curated topic dashboards: what's solid, what's
  fuzzy, what's missing, and which sources cover it.
- **`inbox/`**: unsorted drop zone. Anything goes: screenshots, pasted text, half-formed
  thoughts, a link. Not a layer in its own right, just a holding pen until it's triaged into one.

## Processing the inbox

When asked to process `inbox/` (or you notice it's non-empty), go through each item one at a
time and decide where it actually belongs:

- **Genuinely a new source** (a document, transcript, something to treat as ground truth) →
  move it into `raw/` under the `{{PREFIX}}-` naming convention, with a lightweight stub note
  same as any other raw source.
- **An extraction/summary of something already in `raw/`** → write it into `wiki/summaries/`,
  following the same frontmatter and hub-linking rules as any other summary.
- **Too thin to confidently place** (a stray thought, an ambiguous screenshot, not enough
  context to tell what it's for): don't guess. Leave it in `inbox/` and ask, rather than
  filing it somewhere wrong. Same principle as the hard rule below on unconfident writeback.
- **Never wiki/atomic/**: that layer is human-written only (see above). If an inbox item reads
  like a personal reaction or half-formed idea, surface it back rather than writing an atomic
  note yourself.

Once an item is triaged (moved into `raw/` or `wiki/summaries/`, or explicitly discarded as
noise), remove it from `inbox/`: the folder should only ever reflect what's still
unprocessed, not a growing archive.

## Frontmatter (OKF-derived)

Every `.md` file except `{{PREFIX}}-index.md`/`{{PREFIX}}-log.md` needs valid YAML frontmatter
with a non-empty `type`.

```yaml
---
type: source | summary | atomic | map | schema
title: "Human-readable title"
description: "One-line summary"
resource: some-file.pdf           # only on source stubs, relative path to the real file
tags: [{{PREFIX}}, some-topic]
sources:                          # on summary/atomic notes, what this was derived from
  - id: some-source
    resource: /raw/some-source.md
generated:                        # only on AI-written notes
  by: claude-sonnet-5
  date: YYYY-MM-DD
verified: false                   # AI-written notes start false; flip it after you review
---
```

### Tags vs. aliases (findability)

- **`tags:`** on summary/map notes should include the *named concepts covered*, not just
  source/type/chapter labels. This is what makes a specific concept filterable/clickable
  across every note that touches it, via Obsidian's tag search and graph filtering.
- **`aliases:`** (Obsidian-native, plain list of alternate names) is for exact synonym terms on
  a *single-concept* note, so either term resolves to it in search/links.

### Actor convention

- AI-authored content: `generated.by: claude-sonnet-5`, `verified: false` until you review it.
- User-authored or user-confirmed content: no `generated` block.

## Hard rule: no unconfident writeback

Never file synthesis into `wiki/` that isn't grounded in an actual source. If unsure, say so in
the note ("no confident answer from the sources") rather than smoothing over a gap. An
unconfident guess filed back becomes a future "fact" and compounds.

## Formulas & images

If a raw source is a PDF where formulas/diagrams don't extract as text (common with slide
decks), render the specific page to an image and transcribe rather than trusting raw text/XObject
extraction; it can come out silently wrong or mirrored. Keep the rendered image alongside the
transcription (e.g. a collapsed `<details>` block) so it stays verifiable against the original.

## Table of contents (on raw stubs)

Every raw stub also carries a `## Contents` section, appended after the source embed, listing
the source's real chapter/section structure with page numbers, built from actually reading the
front matter/structure, not guessed from filename or metadata:

```markdown
## Contents

Page numbers are the source's own printed page numbers (note any PDF-page offset if the PDF's
page index differs from the printed numbering, e.g. "PDF page = book page + 27").

- Ch 1: Chapter Title (p. X)
  - 1.1 Section Title (p. X)
  - 1.2 Section Title (p. X)
- Ch 2: Chapter Title (p. X)
```

This is what makes the vault fast to navigate on a real question: check the stub's Contents
first and jump straight to the relevant page range, instead of re-deriving structure from
scratch or re-reading the whole source every time.

## Hub-linking convention

Every summary and atomic note links back to the raw stub(s) it draws from:

```markdown
Source: [[{{PREFIX}}-some-source]]
```

Because many notes point at the same stub, that stub accumulates backlinks and surfaces as a hub
node in Obsidian's graph view. No manual graph wiring needed beyond this link discipline.

## Reserved files (OKF)

- `{{PREFIX}}-index.md`: flat catalog of every page in the vault, one-line description each.
  Updated on every ingest.
- `{{PREFIX}}-log.md`: append-only, chronological. One entry per ingest/query/lint, using
  `## [YYYY-MM-DD] ingest | <source>` style headings.

## Naming

kebab-case filenames throughout. **Every note filename is prefixed `{{PREFIX}}-`** (root meta
files, raw stubs, summaries; everything except `wiki/atomic/` notes, whose naming is your own
call since AI doesn't write there). This isn't required by OKF or Obsidian. It's
collision-proofing: Obsidian's `[[wikilink]]` resolution matches by bare filename across the
*entire* vault regardless of folder nesting, so if this vault ever merges with another
project's vault, generic names like `index`, `log`, or `chapter1` would silently collide.

## Lint (periodic, manual)

Occasionally sweep the vault for:
- Contradictions between notes
- Orphan notes (nothing links to them, they link to nothing)
- Stale claims (source material changed since a summary was written)
- Broken `[[links]]`
