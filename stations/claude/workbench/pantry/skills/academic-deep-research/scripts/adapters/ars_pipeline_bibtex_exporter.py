#!/usr/bin/env python3
"""BibTeX exporter for the ars_pipeline adapter.

Takes a list of `literature_corpus_entry` dicts and writes a .bib file
suitable for Zotero "Import..." and any LaTeX workflow.

Each entry uses the citation_key from the passport as the BibTeX key.
Field mapping is mostly trivial (title, year, doi, abstract, url), with
two non-trivial cases:

- authors: CSL `[{family, given}, ...]` -> BibTeX `Family, Given and Family, Given`.
- venue_type -> entry type. The passport enum is richer than BibTeX's,
  so we pick the closest fit.

This exporter does not depend on `bibtexparser`; it produces raw BibTeX
so a downstream tool that does not have bibtexparser can still consume
the output. Tests parse the output with bibtexparser to confirm
round-trip fidelity.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

# venue_type -> BibTeX entry type.
_VENUE_TYPE_TO_BIB = {
    "journal-article": "article",
    "conference-paper": "inproceedings",
    "preprint": "misc",
    "book": "book",
    "chapter": "incollection",
    "dissertation": "phdthesis",
    "report": "techreport",
    "dataset": "misc",
    "other": "misc",
    "unknown": "misc",
}


def _author_to_bib(author: dict[str, str]) -> str:
    """Convert one CSL author dict to a BibTeX author string."""
    if "literal" in author:
        # Institutional / corporate author. Wrap in extra braces so
        # BibTeX preserves the literal without trying to parse it.
        return f"{{{author['literal']}}}"
    family = (author.get("family") or "").strip()
    given = (author.get("given") or "").strip()
    if not family:
        return ""
    if given:
        return f"{family}, {given}"
    return family


def _authors_to_bib(authors: list[dict[str, str]] | None) -> str:
    """Convert a CSL author list to a BibTeX author field value (joined by ' and ')."""
    if not authors:
        return ""
    parts = [_author_to_bib(a) for a in authors]
    parts = [p for p in parts if p]
    return " and ".join(parts)


def _escape_bibtex(s: str) -> str:
    """Escape characters that BibTeX treats specially.

    We don't need to be exhaustive for round-trip purposes; this is
    enough to keep the output parseable and to handle the common
    cases (LaTeX special chars, braces, ampersands).
    """
    if not s:
        return s
    # Escape backslash first, then the others.
    s = s.replace("\\", r"\\")
    s = s.replace("&", r"\&")
    s = s.replace("%", r"\%")
    s = s.replace("$", r"\$")
    s = s.replace("#", r"\#")
    s = s.replace("_", r"\_")
    s = s.replace("{", r"\{")
    s = s.replace("}", r"\}")
    return s


def _entry_to_bib(entry: dict[str, Any]) -> str:
    """Convert one passport entry to a BibTeX entry string."""
    citekey = entry.get("citation_key", "")
    if not citekey:
        return ""

    venue_type = entry.get("venue_type", "unknown")
    entry_type = _VENUE_TYPE_TO_BIB.get(venue_type, "misc")

    fields: list[tuple[str, str]] = []
    if entry.get("title"):
        fields.append(("title", entry["title"]))
    if entry.get("authors"):
        fields.append(("author", _authors_to_bib(entry["authors"])))
    if entry.get("year"):
        fields.append(("year", str(int(entry["year"]))))
    if entry.get("venue"):
        # For articles, the journal name; for inproceedings, the conference.
        if entry_type in ("article", "inproceedings", "incollection"):
            field_name = "journal" if entry_type == "article" else "booktitle"
            fields.append((field_name, entry["venue"]))
        else:
            fields.append(("publisher", entry["venue"]))
    if entry.get("doi"):
        fields.append(("doi", entry["doi"]))
    if entry.get("source_pointer"):
        fields.append(("url", entry["source_pointer"]))
    if entry.get("abstract"):
        # BibTeX abstracts are wrapped in extra braces to preserve them
        # across re-parsing (otherwise bibtexparser / LaTeX may try to
        # render LaTeX commands inside the abstract).
        fields.append(("abstract", "{" + entry["abstract"] + "}"))
    if entry.get("tags"):
        # BibTeX keywords are comma-separated inside a single field.
        fields.append(("keywords", ", ".join(entry["tags"])))

    if not fields:
        return ""

    body = ",\n  ".join(f"{name} = {{{_escape_bibtex(value)}}}" for name, value in fields)
    return f"@{entry_type}{{{citekey},\n  {body}\n}}"


def write_bibtex(entries: list[dict[str, Any]], path: Path) -> None:
    """Emit a .bib file, one entry per passport source, sorted by citekey.

    Sorted to match the passport's citation_key sort order so a diff
    between two runs is structural, not cosmetic.
    """
    bib_entries = [_entry_to_bib(e) for e in entries]
    bib_entries = [b for b in bib_entries if b]
    bib_entries.sort(key=lambda e: _extract_citekey(e))
    text = "\n\n".join(bib_entries) + "\n" if bib_entries else ""
    path.write_text(text, encoding="utf-8")


def _extract_citekey(bib_entry: str) -> str:
    """Pull the citekey out of a BibTeX entry for sort purposes.

    Format is `@type{citekey, ...}`. We just take the part between the
    first `{` and the first `,`.
    """
    if "{" not in bib_entry:
        return ""
    after_brace = bib_entry.split("{", 1)[1]
    if "," not in after_brace:
        return ""
    return after_brace.split(",", 1)[0].strip()


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
        help="Path to write the .bib file",
    )
    args = ap.parse_args()

    passport = yaml.safe_load(args.passport.read_text(encoding="utf-8"))
    entries = passport.get("literature_corpus", [])
    write_bibtex(entries, args.output)
    print(f"Wrote {len(entries)} entries to {args.output}", file=sys.stderr)
