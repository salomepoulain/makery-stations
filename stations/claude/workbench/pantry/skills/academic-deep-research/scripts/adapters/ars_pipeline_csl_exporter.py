#!/usr/bin/env python3
"""CSL-JSON exporter for the ars_pipeline adapter.

Takes a list of `literature_corpus_entry` dicts (as produced by
`ars_pipeline.py`) and writes a CSL-JSON array to a path.

The CSL-JSON shape is the canonical interchange format used by Zotero,
Paperpile, Pandoc, and the OpenAlex API. The passport entries are
already CSL-shaped internally (authors, type, title, container-title,
DOI, URL, abstract all map directly), so this is mostly a serialization
job plus field renaming for the small set of fields where the passport
schema uses a different name than CSL.

Output: a single JSON array, one object per source, sorted by `id` to
match the passport's sort order.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# Passport field -> CSL-JSON field mapping. CSL is the canonical name;
# passport is the canonical internal name. Anything not in this map is
# passed through under the same key.
_PASSPORT_TO_CSL = {
    "title": "title",
    "authors": "author",
    "year": "issued",          # passport: int, CSL: {date-parts: [[year]]}
    "doi": "DOI",
    "source_pointer": "URL",
    "venue": "container-title",
    "abstract": "abstract",
    "tags": "keyword",
}

# venue_type -> CSL type. The passport's venue_type enum is richer than
# CSL's "type" enum, so we map it onto the closest CSL equivalent.
_VENUE_TYPE_TO_CSL = {
    "journal-article": "article-journal",
    "conference-paper": "paper-conference",
    "preprint": "manuscript",
    "book": "book",
    "chapter": "chapter",
    "dissertation": "thesis",
    "report": "report",
    "dataset": "dataset",
    "other": "article",
    "unknown": "article",
}


def _entry_to_csl(entry: dict[str, Any]) -> dict[str, Any]:
    """Convert one passport entry to a CSL-JSON object."""
    csl: dict[str, Any] = {
        "id": entry.get("citation_key", ""),
        "type": _VENUE_TYPE_TO_CSL.get(
            entry.get("venue_type", "unknown"), "article"
        ),
    }

    if entry.get("title"):
        csl["title"] = entry["title"]

    if entry.get("authors"):
        csl["author"] = entry["authors"]

    if entry.get("year"):
        csl["issued"] = {"date-parts": [[int(entry["year"])]]}

    if entry.get("doi"):
        csl["DOI"] = entry["doi"]

    if entry.get("source_pointer"):
        csl["URL"] = entry["source_pointer"]

    if entry.get("venue"):
        csl["container-title"] = entry["venue"]

    if entry.get("abstract"):
        csl["abstract"] = entry["abstract"]

    if entry.get("tags"):
        csl["keyword"] = entry["tags"]

    # Pass through any pipeline-specific fields that don't have a CSL
    # equivalent. These land under a `_pipeline` namespace so Zotero
    # ignores them but a downstream tool can read them.
    pipeline_fields = {
        k: v
        for k, v in entry.items()
        if k
        not in (
            "citation_key", "title", "authors", "year", "doi",
            "source_pointer", "venue", "abstract", "tags",
            "venue_type", "venue_type_provenance",
            "obtained_via", "obtained_at", "adapter_name",
            "adapter_version",
        )
    }
    if pipeline_fields:
        csl["_pipeline"] = pipeline_fields

    return csl


def write_csl_json(entries: list[dict[str, Any]], path: Path) -> None:
    """Emit a CSL-JSON array, one entry per passport source, sorted by id.

    Idempotent: same input produces byte-identical output (sorted by id,
    JSON keys in deterministic order).
    """
    csl_array = [_entry_to_csl(e) for e in entries]
    csl_array.sort(key=lambda e: e.get("id", ""))
    path.write_text(
        json.dumps(csl_array, indent=2, ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )


if __name__ == "__main__":
    import argparse
    import sys
    import yaml

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--passport", type=Path, required=True,
        help="Path to passport.yaml",
    )
    ap.add_argument(
        "--output", type=Path, required=True,
        help="Path to write the CSL-JSON file",
    )
    args = ap.parse_args()

    passport = yaml.safe_load(args.passport.read_text(encoding="utf-8"))
    entries = passport.get("literature_corpus", [])
    write_csl_json(entries, args.output)
    print(f"Wrote {len(entries)} entries to {args.output}", file=sys.stderr)
