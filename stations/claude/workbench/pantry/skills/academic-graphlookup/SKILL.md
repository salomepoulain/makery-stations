---
name: academic-graphlookup
description: Recursively crawl the real citation graph (OpenAlex + Semantic Scholar) outward from a project's academic-research corpus, classify each discovered paper's relevance with a free OpenRouter model, and export the growing graph for citegraph.html. Use when the user wants to expand a literature-review corpus beyond its seed papers, find related work by following citations, or "go deeper" on an existing citation map.
---

# academic-graphlookup

Grows `docs/academic-research/corpus/` outward from its seed papers by
following real citation edges (not co-occurrence placeholders), and tells
you which of what it finds is actually worth reading.

## When to use this skill

Use after `academic-deep-research` has produced a seed corpus
(`passport.yaml` + `graph_data.json`/`citegraph.html`) and the user wants
more: "find related papers," "expand the citation graph," "look deeper,"
or similar. Not for the initial literature search itself — that's
`academic-deep-research`'s job. This skill only crawls citations of papers
already in the corpus (and whatever it discovers along the way).

## What it does

1. **`crawl.py`** — starting from the 7(+) seed papers, follows backward
   references and forward citations via OpenAlex (falling back to
   Semantic Scholar for works OpenAlex doesn't index, mainly brand-new
   arXiv preprints). Bounded by `config.json`: `max_hops` (default 2),
   `fanout_top_n` (default 15 — an *ordering* heuristic for which nodes
   get expanded first, never an exclusion filter), `node_budget` (default
   300), `date_floor` (default 2018, backward traversal only). Persists
   everything to `docs/academic-research/corpus/citegraph.sqlite`.
2. **`classify_relevance.py`** — for every paper without a verdict yet,
   one OpenRouter call (rotating across the two free models listed in
   `config.json` on rate-limit) does two things at once: (a) scores
   relevance to the project's research question + scope boundaries (read
   from `phase1_revised_v2.md`) on a 5-point scale — `highly_relevant` /
   `relevant` / `uncertain` / `probably_not` / `not_relevant`, deliberately
   more granular than a 3-way split so "uncertain" doesn't become the
   model's default whenever it's even slightly unsure — and (b) tags the
   paper with a strategy family, reusing the existing vocabulary (seeded
   from the 9 families in `phase1_revised_v2.md`) wherever it fits.
   `_db.resolve_family` fuzzy-matches a proposed new tag against the
   current list first, so "rug-pull detection" snaps onto the existing
   "Rug-pull / fraud prediction" instead of forking a near-duplicate — only
   a proposal that resembles nothing existing gets created. New families
   are auto-accepted (same "first pass, not ground truth" trust level as
   the relevance verdict) and show up in `families.md` after the next
   export. Requires `OPENROUTER_API_KEY` in the environment; fails loudly,
   not silently, if it's missing.
3. **`export_graph_data.py`** — writes `graph_data.json` (for
   `citegraph.html`), `candidates_for_review.md` (papers not yet in the
   seed corpus, ranked by citation count, for you to manually promote into
   `phase2_bibliography.md`), and `families.md` (the current tag
   vocabulary, paper counts per family, and which ones were discovered via
   crawl vs. original phase1 families — the source of truth `citegraph.html`'s
   by-tag layout mode clusters against).
4. **`record_citation_count.py`** — a manual patch for the rare case where
   neither OpenAlex nor Semantic Scholar has a citation count. Google
   Scholar has no API; checking it is a `/browse` step a human (or the
   orchestrating session) does by hand, then records here. Not
   auto-invoked — Scholar aggressively blocks automated querying, so this
   stays deliberately manual rather than retried.

## Running it

```bash
python .claude/skills/academic-graphlookup/scripts/crawl.py
python .claude/skills/academic-graphlookup/scripts/classify_relevance.py
python .claude/skills/academic-graphlookup/scripts/export_graph_data.py
```

Override bounds per run without touching `config.json`:

```bash
python .claude/skills/academic-graphlookup/scripts/crawl.py --max-hops 1 --node-budget 30
```

**Rerunning is the "go deeper" workflow.** `crawl.py` only expands papers
still marked `expanded=0` in the db — nothing is redone, and nothing found
in a prior run is ever discarded, so widening the bounds and rerunning
picks up exactly where the last run left off.

The resolved config for each run (defaults + any CLI overrides) is written
to `docs/academic-research/corpus/academic-graphlookup_config.effective.json` for
auditability.

## Data model

SQLite at `docs/academic-research/corpus/citegraph.sqlite`, three tables:
`papers` (id, doi, arxiv_id, title, abstract, venue, year, citation_count
+ source, is_seed, hop_distance, discovered_via, expanded,
crawl_priority_score, relevance_verdict, relevance_reasoning, family),
`edges` (citing_id, cited_id, source), and `families` (name, description,
is_original, created_from_paper_id, created_at). Schema + migrations live
in `scripts/_db.py` — `connect()` runs both idempotently, so pulling this
skill into a project with an older `citegraph.sqlite` (pre-`family` column,
pre-`families` table) upgrades it in place on the next run.

`citegraph.html`'s node encoding: size = citation count (never displayed
lower than what the crawl has structurally verified via in-degree, even
when no API resolved a global count — see `export_graph_data.py`), fill
color = publication year, ring color = relevance verdict. Three layout
modes (toggle buttons, top-left): free force layout, sorted by year
(older at top), and clustered by family.

## Relationship to academic-deep-research

This supersedes `academic-deep-research/scripts/adapters/ars_pipeline_citegraph.py --with-live-citations`
— that flag did a single, non-recursive hop of Semantic Scholar
citations/references for the seed papers only. This skill's crawl covers
that same ground as hop 1 and keeps going, so don't run both; use
`academic-graphlookup` for anything beyond a one-off static export.

It does not (yet) auto-promote discovered papers into
`phase2_bibliography.md` — `candidates_for_review.md` is the current
hand-off point, reviewed and merged in manually. Fully automatic
promotion into the deep-research pipeline is a plausible future
extension, not built yet.

Untouched by this skill: `passport.yaml`, `bib.csl.json`, `bib.bib` (the
existing `ars_pipeline.py` outputs) and everything under `corpus/raw/`.

## Limitations

- OpenRouter's free-tier models carry their own rate limits; expect
  `classify_relevance.py` to slow down or fall back between the two
  configured models on a busy run, not fail outright.
- A paper resolvable by neither OpenAlex nor Semantic Scholar (no DOI, no
  arXiv ID, e.g. some SSRN working papers) gets no automatic citation
  count or edges — it can still be a node (if reachable as a seed or via
  another paper's metadata) but stays a citation dead-end until
  `record_citation_count.py` is used.
