# ARS Literature Corpus Adapters

Reference adapters that produce `literature_corpus[]` entries for the ARS Material Passport. Defined by the adapter contract at [`academic-pipeline/references/adapters/overview.md`](../../academic-pipeline/references/adapters/overview.md).

## What these are

Three user-source adapters and one pipeline-output adapter:

- **`folder_scan.py`** — scans a directory of files, parses citation metadata from filenames.
- **`zotero.py`** — reads a Better BibTeX JSON export.
- **`obsidian.py`** — reads an Obsidian vault (frontmatter Convention A or Karpathy-style Convention B).
- **`ars_pipeline.py`** — reads a completed Phase 2 deliverable (annotated bibliography + verification table + synthesis markdown) and emits the passport plus three derived files (CSL-JSON, BibTeX, citation graph). This is the inverse of the other three: it consumes pipeline output rather than user-owned sources.

Each writes two files: a `passport.yaml` with `literature_corpus[]` entries, and a `rejection_log.yaml` listing whatever the adapter could not map onto a valid entry. The pipeline adapter additionally writes `bib.csl.json`, `bib.bib`, and `bib.citegraph.json` for Zotero / LaTeX / graph-viewer consumption.

**These are references, not products.** If your corpus is in Zotero, Obsidian, or a plain folder, you can run these directly; if it is in Notion, Readwise, Airtable, a custom SQLite, etc., copy a reference adapter and adapt it to your source. The pipeline adapter is a fixed-shape consumer of a specific markdown structure (§3 sources as headings, §5 gated-out sources as bullets); for a different pipeline output format, fork and adapt.

## Running a reference adapter

### folder_scan

```bash
python scripts/adapters/folder_scan.py \
    --input /path/to/your/pdf/folder \
    --passport /tmp/passport.yaml \
    --rejection-log /tmp/rejection_log.yaml
```

Filenames are parsed with two conventions plus a fallback: `{Family}_{Year}_{title}.{ext}`, `{Family}{Year}{title}.{ext}`, or `... {Year} ... {Family} ...`. Files whose filename cannot yield both a family and a year are rejected. Non-ASCII filenames are rejected (Unicode support is a deferred extension). Symlinks are followed but the rejection log records the un-resolved path so collisions across subdirectories remain distinguishable.

### zotero

Export your Zotero library as **Better BibTeX JSON** (Zotero → File → Export Library → Format: Better CSL JSON, with the Better BibTeX extension installed). Then:

```bash
python scripts/adapters/zotero.py \
    --input ~/zotero_export.json \
    --passport /tmp/passport.yaml \
    --rejection-log /tmp/rejection_log.yaml
```

This adapter does NOT call the Zotero Web API. If you want live sync, write your own adapter using this file as a starting point. Items missing required fields (`title`, `authors`, parseable `year`, `source_pointer`) are rejected with a categorical reason; seasonal dates like `Spring 2024` are rejected as `year_unparseable`.

### obsidian

```bash
python scripts/adapters/obsidian.py \
    --input ~/ObsidianVault \
    --passport /tmp/passport.yaml \
    --rejection-log /tmp/rejection_log.yaml
```

Files under `_templates/` and `.obsidian/` are skipped. Wikilinks (`[[other note]]`) are NOT resolved; they appear as literal text in `user_notes`. Notes with valid YAML frontmatter use Convention A (BibTeX-style: `citekey:`, `authors:`, `year:`, `title:`); notes without frontmatter fall through to Convention B (filename stem as citation_key, body as user_notes). Notes with malformed YAML frontmatter are rejected as `invalid_field_format` rather than silently re-classified as Convention B.

### ars_pipeline

Run after a Phase 2 deliverable is complete (annotated bibliography + verification table + synthesis markdown). This adapter turns a human-written research pipeline into a passport plus three derived files you can load into Zotero, BibTeX, or a citation graph viewer.

```bash
python scripts/adapters/ars_pipeline.py \
    --bibliography docs/academic-research/phase2_bibliography.md \
    --verification docs/academic-research/phase2_verification.md \
    --synthesis    docs/academic-research/phase3_synthesis.md \
    --output-dir   docs/academic-research/corpus/
```

The output directory receives five files: `passport.yaml`, `rejection_log.yaml`, `bib.csl.json` (Zotero / Paperpile / Pandoc), `bib.bib` (LaTeX / BibTeX), and `bib.citegraph.json` (Consensus-style graph with edges, co-citations, and unresolved-citation logs).

The adapter expects a specific markdown structure: §3 of the bibliography contains source entries as `### 3.N` headings; §5 contains gated-out sources as bullet items under category headings (`### 5.1`, `### 5.2`, …). §1, §2, §4, §6–9 are metadata and are skipped. The verification table is parsed for the join key `{first family}{year}` and used to surface citation-correctness / reproducibility / conflict-of-interest notes in the rejection log.

Pass `--with-live-citations` to add Semantic Scholar `/citations` and `/references` edges to the citation graph (fail-soft: any unreachable paper is recorded in `unresolved[]` rather than aborting the run).

## Validating adapter output

Before using the passport in any ARS workflow:

```bash
python scripts/check_literature_corpus_schema.py \
    --passport /tmp/passport.yaml \
    --rejection-log /tmp/rejection_log.yaml
```

### fetch_oa_pdfs

Run after `ars_pipeline.py` (or any adapter) has produced a `passport.yaml`, to pull down full-text PDFs. This is not a corpus adapter itself — it doesn't touch `passport.yaml`'s shape — it's a downstream consumer that reads it and populates a `raw/` folder next to it.

```bash
python scripts/adapters/fetch_oa_pdfs.py \
    --passport docs/academic-research/corpus/passport.yaml \
    --raw-dir  docs/academic-research/corpus/raw/ \
    --email    you@example.com
```

Resolution order per entry: arXiv direct PDF URL (from `arxiv_id`) -> OpenAlex `best_oa_location` (by `doi`) -> Unpaywall `best_oa_location` (by `doi`, requires `--email` per its terms). Only ever fetches copies already made open access by a publisher or repository — no Sci-Hub, no paywall workarounds. A source with no open-access copy, or one blocked by a host's anti-scraping measures even when nominally OA (this happens with some ACM/Elsevier `dl.` domains), is recorded in `raw_manifest.yaml` as a miss rather than retried with spoofed headers or otherwise routed around.

## How to write your own adapter

1. Read the adapter contract at [`academic-pipeline/references/adapters/overview.md`](../../academic-pipeline/references/adapters/overview.md).
2. Read the JSON schemas:
   - [`shared/contracts/passport/literature_corpus_entry.schema.json`](../../shared/contracts/passport/literature_corpus_entry.schema.json)
   - [`shared/contracts/passport/rejection_log.schema.json`](../../shared/contracts/passport/rejection_log.schema.json)
3. Copy one of `folder_scan.py` / `zotero.py` / `obsidian.py` as a starting point.
4. Change the input-reading and field-mapping code for your source.
5. Keep the output shape exactly (sorted `literature_corpus[]` by `citation_key`, always emit `rejection_log.yaml`, schema-clean entries only).
6. Set `obtained_via: "other"` and `adapter_name: "<your-adapter-name>"` on every entry you produce.
7. Reuse helpers in [`_common.py`](_common.py) where possible — `make_citation_key`, `ensure_unique_citekey`, `parse_csl_name`, `parse_semicolon_names`, `path_to_file_uri`, `write_passport`, `write_rejection_log`, `now_iso`. They encode the contract details so you do not have to re-derive them.
8. Validate: `python scripts/check_literature_corpus_schema.py --passport <your passport>`.
9. Write tests modeled on `scripts/adapters/tests/`. The conftest fixtures `clean_timestamps` and `load_yaml` make golden-output testing easy.

## Privacy reminder

`abstract` and `user_notes` can contain publisher-copyrighted material. Before sharing a passport that contains these fields publicly (e.g., in a public repo or over the web), make sure you have the right to publish that text. ARS does not enforce this — it only warns you in the schema description.

## Tests

```bash
cd <repo_root>
pytest scripts/adapters/tests/ -v
```

CI runs these on every push / PR that touches `scripts/adapters/**`, `shared/contracts/passport/**`, the adapter overview, or either of the two lint scripts.
