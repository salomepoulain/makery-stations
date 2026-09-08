# Academic Deep Research

The upstream research engine of the suite.

A 13-agent team that runs the full investigation pipeline: scoping, literature search, source verification, synthesis, and APA 7.0 report compilation.

## When to use this skill

Use when the work is upstream of writing a paper: framing a research question, running a literature review, performing a systematic review or meta-analysis, fact-checking claims, or scanning papers in a topic area. The user has research intent, not "I need a finished manuscript."

## Modes

| Mode | Purpose |
|---|---|
| `full` | Complete pipeline from RQ to final report. Default for clear research questions. |
| `quick` | 30-minute brief. Use for fast orientation. |
| `socratic` | Guided dialogue that helps the user clarify their RQ before research starts. Use when intent is ambiguous. |
| `review` | Evaluate a specific paper before citing it. |
| `lit-review` | Literature review for a topic. |
| `three-way-scan` | Fast comparison of a small set of papers (WHY / HOW / WHAT framing). |
| `fact-check` | Verify specific factual claims. |
| `systematic-review` | PRISMA-aligned review with optional meta-analysis. |

When in doubt between `socratic` and `full`, prefer `socratic`. The user can switch to `full` after the RQ is settled.

## Key rules

- All claims carry citations; evidence hierarchy respected (meta-analyses > RCTs > cohort > case reports > expert opinion).
- Contradictions are disclosed with evidence quality comparison, not papered over.
- AI disclosure is included in the final report.
- Output language matches the user input (English, 繁體中文, 한국어).
- Mode is selected before the pipeline runs. If intent is unclear, ask via `socratic` first.

## Inputs and outputs

**Expects**: a research question, a topic, a paper to review, or claims to fact-check. The `socratic` mode accepts a vague interest and helps shape it.

**Produces** (handoff to `academic-paper`):
- RQ Brief
- Methodology Blueprint
- Annotated Bibliography
- Synthesis Report
- INSIGHT collection

## Output file location

All phase artifacts go to `docs/academic-research/` in the project root. The skill directory itself never holds user-project files.

| Phase | File |
|---|---|
| 1 — Scoping | `docs/academic-research/phase1_<descriptor>.md` (e.g., `phase1_revised_v2.md`) |
| 2 — Investigation | `docs/academic-research/phase2_bibliography.md` and `docs/academic-research/phase2_verification.md` |
| 3 — Analysis | `docs/academic-research/phase3_synthesis.md` |
| 4 — Composition | `docs/academic-research/phase4_report.md` |
| 5–6 — Review & Revision | edits to `phase4_report.md`; no separate artifact |

Subagents spawned by the orchestrator (or by phase agents) must write to these exact paths, not to the skill's own working directory. The skill's working directory is `.claude/skills/academic-deep-research/`, which is shared with the 3 other academic skills and should stay clean of project artifacts. If a phase subagent doesn't get an explicit output path, it defaults to its working directory — which is wrong. Always pass the full `docs/academic-research/phaseN_*.md` path in the subagent's invocation.

## Corpus export (after Phase 2)

Once Phase 2 is complete, run the `ars_pipeline` adapter to convert the human-written bibliography into a literature corpus in machine-readable form:

```bash
python .claude/skills/academic-deep-research/scripts/adapters/ars_pipeline.py \
    --bibliography docs/academic-research/phase2_bibliography.md \
    --verification docs/academic-research/phase2_verification.md \
    --synthesis    docs/academic-research/phase3_synthesis.md \
    --output-dir   docs/academic-research/corpus/
```

Output (5 files in `--output-dir`):

| File | Consumer |
|---|---|
| `passport.yaml` | ARS literature corpus, conforms to `shared/contracts/passport/literature_corpus_entry.schema.json` |
| `rejection_log.yaml` | Gated-out / excluded sources with categorical reasons |
| `bib.csl.json` | Zotero / Paperpile / Pandoc "Import..." |
| `bib.bib` | BibTeX for LaTeX workflows |
| `bib.citegraph.json` | Citation graph (edges, co-citations, unresolved[]) for a Consensus-style viewer |

The expected markdown structure is documented in `scripts/adapters/README.md` "ars_pipeline" and in the adapter's docstring. §3 source entries are `### 3.N` headings; §5 gated-out entries are bullet items under `### 5.N` category headings. §1, §2, §4, §6–9 are metadata and are skipped by the parser.

Pass `--with-live-citations` to add Semantic Scholar `/citations` and `/references` edges to the citation graph. Failures are recorded in the graph's `unresolved[]` array; the run does not abort.

## Fetching full-text PDFs (after corpus export)

`ars_pipeline.py` only writes bibliographic metadata (author, DOI, venue, `source_pointer`) — no full text. To pull down a legal, open-access copy of each source into `docs/academic-research/corpus/raw/`, run:

```bash
python .claude/skills/academic-deep-research/scripts/adapters/fetch_oa_pdfs.py \
    --passport docs/academic-research/corpus/passport.yaml \
    --raw-dir  docs/academic-research/corpus/raw/ \
    --email    <your-email>
```

It resolves each entry through, in order: arXiv (direct PDF URL from `arxiv_id`), OpenAlex `best_oa_location`, then Unpaywall as a fallback (both by `doi`). It writes `<citation_key>.pdf` per hit and a `raw_manifest.yaml` recording what happened to every entry — `downloaded`, `already_present`, `no_oa_copy`, `no_doi`, or `error`.

This only ever fetches copies a publisher or repository has already made open access. It will not use Sci-Hub or any other unauthorized mirror, and a source with no open-access copy (e.g. behind a publisher paywall, or blocked by anti-scraping measures even when the license is technically OA) is recorded as a miss, not silently skipped or worked around.

## Routing

Routing across the 4 academic skills is documented in `academic-pipeline/docs/SKILL_GUIDE.md` "Routing Discipline." This skill assumes routing has already settled on `academic-deep-research`.

## Related skills

- `academic-paper` — downstream paper writing; consumes this skill's outputs.
- `academic-paper-reviewer` — multi-perspective review of a completed paper.
- `academic-pipeline` — full orchestrator that chains all three.
- `graphlookup` — run manually after Phase 2 to expand the corpus beyond its seed bibliography, by recursively crawling real citation edges (OpenAlex + Semantic Scholar) outward and classifying what it finds for relevance. Writes `candidates_for_review.md` next to `phase2_bibliography.md` for manual promotion; not part of the automatic 6-phase pipeline.
