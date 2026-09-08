#!/usr/bin/env python3
"""ars_pipeline: produce a literature_corpus passport (and three derived
artifacts) from a completed academic-deep-research Phase 2 run.

This is the inverse of the Zotero / Obsidian / folder_scan adapters
in this directory. Those adapters read user-owned sources and emit a
passport. This one reads the pipeline's Phase 2 outputs and emits a
passport plus three derived files the user can load into Zotero,
BibTeX, or a citation graph viewer.

Inputs (all paths are user-supplied via CLI):
  - `phase2_bibliography.md` — the Phase 2 search log + annotated
    bibliography + gated-out appendix + comparator-adequacy log.
  - `phase2_verification.md` — the citation verification table,
    evidence tier matrix, currency assessment, cross-source
    corroboration, top-3 replication check, bias/quality flags.
  - `phase3_synthesis.md` (optional) — the synthesis narrative. Used
    for the static-edge pass in the citation graph; not required for
    the passport / CSL / BibTeX outputs.

Outputs (all written to `--output-dir`):
  - `passport.yaml` — standard ARS passport contract, sorted by
    citation_key. Conforms to `literature_corpus_entry.schema.json`.
  - `rejection_log.yaml` — gated-out sources, comparator-inadequate
    sources, methodology-only sources, and any source whose
    verification row could not be matched.
  - `bib.csl.json` — CSL-JSON array derived from the passport.
  - `bib.bib` — BibTeX derived from the passport.
  - `bib.citegraph.json` — citation graph with static edges (from
    synthesis + bibliography mentions) and live edges (Semantic
    Scholar /citations + /references) when `--with-live-citations`
    is set.

Adapter contract: see `academic-pipeline/references/adapters/overview.md`.
The contract is the same as the other three reference adapters
(`--input`, `--passport`, `--rejection-log` equivalents), but this
adapter has more inputs and more outputs because the source is
richer (a human-written Phase 2 deliverable, not a flat database).

Privacy: passport entries may carry `abstract` from publisher
metadata. The CSL-JSON and BibTeX outputs include abstracts. The
schema description marks `abstract` as PRIVATE; ARS does not
enforce this, but downstream tools / users must strip these fields
before sharing publicly.

Usage:
  python scripts/adapters/ars_pipeline.py \\
      --bibliography <docs/academic-research/phase2_bibliography.md> \\
      --verification <docs/academic-research/phase2_verification.md> \\
      --synthesis <docs/academic-research/phase3_synthesis.md> \\
      --output-dir <docs/academic-research/corpus/> \\
      [--with-live-citations]
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Dual-path import so the adapter runs from either the repo root or
# the scripts/adapters/ directory directly. Mirrors the pattern used
# by the other reference adapters.
_THIS = Path(__file__).resolve()
_REPO_ROOT = _THIS.parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.adapters._common import (  # noqa: E402
    ensure_unique_citekey,
    make_citation_key,
    now_iso,
    parse_csl_name,
    parse_family_year_key,
    write_passport,
    write_rejection_log,
)
from scripts.adapters.ars_pipeline_bibtex_exporter import write_bibtex  # noqa: E402
from scripts.adapters.ars_pipeline_citegraph import build_graph, write_graph  # noqa: E402
from scripts.adapters.ars_pipeline_csl_exporter import write_csl_json  # noqa: E402

ADAPTER_NAME = "ars_pipeline.py"
ADAPTER_VERSION = "1.0.0"


# ----------------------------------------------------------------------------
# Parsing helpers
# ----------------------------------------------------------------------------

# A heading like "### 3.1 Mancino, D. (2025) — Solana measurement / descriptive"
# captures the section number, the citation header, the year, and the
# short family tag. We use this to find the annotated-bibliography
# entries in phase2_bibliography.md §3.
_BIB_HEADING_RE = re.compile(
    r"^###\s+(?P<num>\d+\.\d+(?:\.\d+)?)\s+(?P<header>.+?)\s*$",
    re.MULTILINE,
)

# A bullet item in §5 looks like:
#   - **Author, X. (YEAR) — Title.** body text...
#   - **"Title" (arXiv:XXXX.YYYYY).** body text...
# The leading "**...**" is the source's header; the rest is the body.
_BULLET_HEADER_RE = re.compile(
    r"^-\s+\*\*(?P<header>[^*]+?)\*\*\s*\.?\s*(?P<rest>.*)$",
    re.MULTILINE,
)


@dataclass
class SourceRecord:
    """A parsed source candidate from a bibliography block.

    `section` is the §-number where the block lives (e.g. "3.1"
    for included, "5.1" for Stage 1 exclusions, "5.5" for
    methodology-only). `category` is one of:
      - "included"
      - "methodology_only" (§5.5)
      - "stage1_excluded" (§5.1, §5.2)
      - "stage2_excluded" (§5.3)
      - "preprint_in_press" (§5.6)
      - "skip_already_included" (§5.4, dropped by the caller)
    """
    section: str
    category: str
    header: str
    body: str
    title: str | None = None
    authors: list[dict[str, str]] = field(default_factory=list)
    year: int | None = None
    venue: str | None = None
    doi: str | None = None
    url: str | None = None
    arxiv_id: str | None = None
    rejection_reason: str | None = None
    rejection_detail: str | None = None


def _split_md_sections(md: str) -> list[tuple[str, str, str]]:
    """Split markdown by `## ` headings; return (level, heading, body) tuples.

    `level` is 2 for `## `, 3 for `### `, etc. Body is everything
    between this heading and the next same-or-higher level heading.
    """
    pattern = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
    matches = list(pattern.finditer(md))
    sections: list[tuple[str, str, str]] = []
    for i, m in enumerate(matches):
        level = len(m.group(1))
        heading = m.group(2).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(md)
        body = md[start:end]
        sections.append((level, heading, body))
    return sections


def _parse_year_from_header(header: str) -> int | None:
    """Find the year in a heading or bullet header."""
    m = re.search(r"\(((?:19|20)\d{2})\)", header)
    if m:
        return int(m.group(1))
    m = re.search(r"((?:19|20)\d{2})", header)
    if m:
        return int(m.group(1))
    return None


def _parse_authors_from_header(header: str) -> list[dict[str, str]]:
    """Parse 'Family, I., Family, I., & Family, I.' from an APA-7 heading.

    The annotated-bibliography headings use the APA 7.0 inverted form
    with `&` before the last author. Each author chunk is either
    "Family, Initials" (e.g. "Wu, C.") or a multi-token family like
    "La Morgia, M." or a single-word one-name author.

    The difficulty is that APA 7.0 separates authors with `, ` and the
    initials block also uses `, `, so a naive split on every comma
    mangles "Wu, C., Chen, J." into one author. We use a
    lookahead-style split: a comma is a separator only when the
    following token is an uppercase initial (one or more letters
    followed by a period, e.g. "C.", "H.", "A.B.").
    """
    # Strip the year and any " — tag" tail, also strip a leading
    # quoted title. We anchor on the first year occurrence or the
    # first em-dash separator. We do NOT match plain hyphens because
    # they appear inside hyphenated family names like "Nita-Rotaru".
    year_or_dash_re = re.compile(
        r"\(\s*(?:[A-Z][a-z]+\s+)?(?:arXiv:[\d.]+(?:v\d+)?,?\s+)?((?:19|20)\d{2})[a-z]?\s*\.?\s*\)|"
        r"\s*[—–]\s*"
    )
    m = year_or_dash_re.search(header)
    head = (header[: m.start()] if m else header).strip()
    head = head.strip('"').strip()
    if not head:
        return []

    # Split on `&` first to get the last-author boundary.
    parts = [p.strip() for p in head.split("&") if p.strip()]
    if not parts:
        return []

    # Treat each part as a sequence of one or more authors separated
    # by ", <Initials>." patterns. We do this by walking through
    # the text and looking for the boundary pattern.
    initial_re = re.compile(r"^[A-Z]\.(\s*[A-Z]\.)*$")

    authors: list[dict[str, str]] = []
    for part in parts:
        # Tokenize on commas, dropping empty tokens (e.g. trailing
        # comma before "&" leaves an empty string).
        tokens = [t.strip() for t in part.split(",") if t.strip()]
        if not tokens:
            continue
        i = 0
        while i < len(tokens):
            cur = tokens[i]
            if i + 1 < len(tokens) and initial_re.match(tokens[i + 1]):
                # cur is a family, tokens[i+1] is initials, possibly
                # more initials on subsequent tokens.
                j = i + 2
                while j < len(tokens) and initial_re.match(tokens[j]):
                    j += 1
                initials = ", ".join(tokens[i + 1 : j])
                authors.append({"family": cur, "given": initials})
                i = j
            else:
                # cur is a complete family (single-word or multi-word
                # like "La Morgia"). If it has a space, treat the last
                # word as the family and the rest as a "given" prefix.
                if " " in cur:
                    *given_parts, family = cur.split()
                    authors.append({
                        "family": family,
                        "given": " ".join(given_parts),
                    })
                else:
                    authors.append({"family": cur})
                i += 1
    return authors


def _parse_title_from_body(body: str) -> str | None:
    """Pull the title from the first APA-7 citation line in the body.

    The body of a §3 source usually starts with a full citation of
    the form:

        Author, A., & Author, B. (YEAR). Title goes here. In *Venue*...

    We want the "Title goes here" portion. Strategy: find the first
    line that looks like an APA citation, then locate the year-period
    and take everything between that and the next sentence boundary
    (period + space + capital) — but only if the resulting cut falls
    inside a reasonable title length (5-200 chars). Otherwise prefer
    the explicit " In *Venue*" marker.
    """
    apa_year_re = re.compile(r"\(\d{4}[a-z]?\)\.\s*")

    for line in body.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("-") or stripped.startswith("**"):
            continue
        if stripped.startswith("http") or stripped.startswith("arXiv:"):
            continue
        if stripped.startswith("|") or stripped.startswith("#"):
            continue
        if stripped.startswith("**") and ":**" in stripped:
            continue

        m = apa_year_re.search(stripped)
        if not m:
            continue
        after_year = stripped[m.end():]
        if not after_year:
            return None

        # Find the earliest reasonable title-cut. We support four
        # APA-7 markers that appear after the title:
        # 1. " In *Venue*" or " In Journal name" where the next word
        #    is capitalized (real venue names always start with a
        #    capital). The lookahead prevents matching the common
        #    English word "in" inside the title.
        # 2. "*Venue name*, *Volume*" — italic venue immediately
        #    followed by italic volume (article case).
        # 3. "*Italic title* (Publisher / arXiv ID)..." — preprint
        #    case where the title is in italics and immediately
        #    followed by a parenthetical.
        # 4. First period followed by capital letter and another word
        #    of at least 3 letters (heuristic: skip single-letter
        #    abbreviations like "A." in "chain-of-thought").
        in_venue_re = re.compile(r"\s+In\s+(?:\*[^*]+\*|[A-Z][A-Za-z0-9]+)")
        italic_venue_re = re.compile(r"\s+\*[A-Z][^*]+\*,\s+\*")
        italic_then_anno_re = re.compile(r"\s+\*[^*]+\*[\s;,]")
        italic_title_re = re.compile(r"^\*([^*]+)\*\s*\(")
        period_cap_re = re.compile(r"\.\s+[A-Z][a-zA-Z]{2,}")

        candidates: list[tuple[int, str]] = []
        m_in = in_venue_re.search(after_year)
        if m_in:
            candidates.append((m_in.start(), "in_venue"))
        m_iv = italic_venue_re.search(after_year)
        if m_iv:
            candidates.append((m_iv.start(), "italic_venue"))
        m_ia = italic_then_anno_re.search(after_year)
        if m_ia:
            candidates.append((m_ia.start(), "italic_anno"))
        m_it = italic_title_re.match(after_year)
        if m_it:
            # Title is the italic-wrapped string at the start of
            # after_year; return it directly.
            return m_it.group(1).strip()
        # For period+cap: only count it if the cut produces a chunk
        # of at least 12 characters (real titles aren't 1 word).
        for m_p in period_cap_re.finditer(after_year):
            cut = m_p.start()
            chunk = after_year[:cut].strip()
            if len(chunk) >= 12:
                candidates.append((cut, "period_cap"))
                break  # take the first qualifying one
        if not candidates:
            return after_year.rstrip(".,")
        candidates.sort(key=lambda x: x[0])
        cut, _ = candidates[0]
        title = after_year[:cut].strip().rstrip(".,")
        if title.startswith('"') and title.endswith('"'):
            title = title[1:-1]
        return title or None
    return None


def _parse_venue_from_body(body: str) -> str | None:
    """Pull the venue string from the first APA-7 citation line.

    Patterns, in order of preference:

    1. " In *Venue Name* (pp. ...). Publisher." — most common
       journal/conference pattern.
    2. First italic-wrapped string in the citation line that is NOT
       the title (titles are returned by ``_parse_title_from_body``
       and we exclude the same italic in both places). We do this
       by skipping the first italic if it immediately follows the
       year-period; subsequent italics are treated as venue.
    3. Trailing publisher token before the URL ("SSRN", "ACM",
       etc.). For preprints this is the best signal.
    4. A literal "arXiv" or "arXiv:NNNN.NNNNN" appearing as a
       standalone token in the citation line. Used for preprints
       that cite only the arXiv ID with no other venue marker.
    """
    in_italic_re = re.compile(r"\s+In\s+\*([^*]+)\*")
    arxiv_inline_re = re.compile(r"\*arXiv:[\d.]+(?:v\d+)?\*")
    trailing_publisher_re = re.compile(
        r"[.)]\s+([A-Z][A-Za-z0-9\.\-]{1,40})\.\s+https?://"
    )
    arxiv_only_re = re.compile(r"\barXiv:(\d{4}\.\d{4,5}(?:v\d+)?)\b")

    for line in body.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("-") or stripped.startswith("**"):
            continue
        if stripped.startswith("http") or stripped.startswith("arXiv:"):
            continue
        if not re.search(r"\(\d{4}[a-z]?\)\.", stripped):
            continue

        m = in_italic_re.search(stripped)
        if m:
            return m.group(1).strip()

        # Find the first italic; if it wraps an arXiv ID, look at
        # the SECOND italic instead (which is usually the venue
        # for journal articles like "Title. *Venue*, *25*(3)").
        italics = list(re.finditer(r"\*([^*]+)\*", stripped))
        non_arxiv_italics = [
            im.group(1).strip()
            for im in italics
            if not arxiv_inline_re.fullmatch("*" + im.group(1) + "*")
        ]
        if non_arxiv_italics:
            # The first italic in the citation is usually the title
            # (when the title is in italics, as in some preprints);
            # the second italic is the venue. We try second first,
            # fall back to first only if the first doesn't look like
            # a title (titles are long and may contain colons).
            for inner in non_arxiv_italics[1:]:
                if len(inner) >= 3:
                    return inner
            first = non_arxiv_italics[0]
            looks_like_title = len(first) > 60 or ":" in first
            if len(first) >= 3 and not first.lower().startswith("arXiv") and not looks_like_title:
                return first

        m = trailing_publisher_re.search(stripped)
        if m:
            return m.group(1).strip()

        m = arxiv_only_re.search(stripped)
        if m:
            return f"arXiv:{m.group(1)}"
    return None


_DOI_RE = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b", re.IGNORECASE)
_ARXIV_RE = re.compile(r"\barXiv:(\d{4}\.\d{4,6}(?:v\d+)?)\b", re.IGNORECASE)
_URL_RE = re.compile(r"https?://[^\s\)\]]+")


def _parse_doi(body: str) -> str | None:
    m = _DOI_RE.search(body)
    return m.group(0) if m else None


def _parse_arxiv_id(body: str) -> str | None:
    m = _ARXIV_RE.search(body)
    return m.group(1) if m else None


def _parse_url(body: str) -> str | None:
    m = _URL_RE.search(body)
    return m.group(0).rstrip(".,;") if m else None


def _classify_section(section_num: str) -> str:
    """Map a §-number to a category used for passport / rejection routing.

    Section numbers come from the section structure of the
    phase2_bibliography.md file as documented in the design plan.

    §5.4 is special: it's a meta-note ("this already-included source
    has a comparator-adequacy tag") rather than a separate source.
    We return "skip_already_included" so the caller can drop it.
    """
    if section_num.startswith("3.") or section_num == "4":
        return "included"
    if section_num == "5.1" or section_num == "5.2":
        return "stage1_excluded"
    if section_num == "5.3":
        return "stage2_excluded"
    if section_num == "5.4":
        return "skip_already_included"
    if section_num == "5.5":
        return "methodology_only"
    if section_num == "5.6":
        return "preprint_in_press"
    return "unknown"


def _parse_bibliography(md: str) -> list[SourceRecord]:
    """Parse all real source entries from phase2_bibliography.md.

    Two source-listing patterns:

    1. §3 annotated-bibliography headings (`### 3.N`). The heading
       itself names the source; the body has metadata. Sources here
       are in the primary evidence matrix.
    2. §5 gated-out appendix bullet items. Each bullet's leading
       `**...**` is the source header; the rest is body. Sources here
       are excluded for various reasons.

    §1, §2, §4, §6, §7, §8, §9 sub-headings are metadata / summary
    sections, not source records, and are skipped.
    """
    sections = _split_md_sections(md)
    records: list[SourceRecord] = []

    for level, heading, body in sections:
        if level != 3:
            continue

        # Section 3.x: heading IS a source.
        m = _BIB_HEADING_RE.match(f"### {heading}")
        if m and m.group("num").startswith("3."):
            num = m.group("num")
            header = m.group("header")
            category = _classify_section(num)
            rec = SourceRecord(
                section=num,
                category=category,
                header=header,
                body=body,
                title=_parse_title_from_body(body),
                authors=_parse_authors_from_header(header),
                year=_parse_year_from_header(header),
            )
            rec.doi = _parse_doi(body)
            rec.url = _parse_url(body)
            rec.arxiv_id = _parse_arxiv_id(body)
            rec.venue = _parse_venue_from_body(body)
            records.append(rec)
            continue

        # Section 5.x: each bullet is a source.
        if heading.startswith("5."):
            num_match = re.match(r"^(\d+\.\d+)\s+", heading)
            if not num_match:
                continue
            num = num_match.group(1)
            category = _classify_section(num)
            for bm in _BULLET_HEADER_RE.finditer(body):
                bullet_header = bm.group("header").strip()
                bullet_body = bm.group("rest").strip()
                rec = SourceRecord(
                    section=num,
                    category=category,
                    header=bullet_header,
                    body=bullet_body,
                    title=None,
                    authors=_parse_authors_from_header(bullet_header),
                    year=_parse_year_from_header(bullet_header),
                )
                rec.doi = _parse_doi(bullet_header + " " + bullet_body)
                rec.url = _parse_url(bullet_header + " " + bullet_body)
                rec.arxiv_id = _parse_arxiv_id(bullet_header + " " + bullet_body)
                records.append(rec)
            continue

        # §1.x, §2.x, §4, §6, §7, §8, §9: not source records. Skip.

    return records


# Verification table parsing: a markdown table with columns
# Study | Citation correctness | Abstract-vs-paper alignment |
# Reproducibility verdict holds | Conflict-of-interest status
_VERIFICATION_HEADER_RE = re.compile(
    r"\|\s*Study\s*\|.*Conflict-of-interest\s*status\s*\|",
    re.IGNORECASE,
)
_TABLE_ROW_RE = re.compile(r"^\|\s*([^|].*?)\s*\|\s*([^|].*?)\s*\|", re.MULTILINE)


def _parse_verification_table(md: str) -> dict[str, dict[str, str]]:
    """Parse the citation-verification table from phase2_verification.md.

    Returns a dict keyed by `parse_family_year_key` -> row dict with
    fields `citation_correctness`, `abstract_alignment`, `reproducibility`,
    `coi_status`, and the original `study_label`.
    """
    if not _VERIFICATION_HEADER_RE.search(md):
        return {}

    # Find the table region (from the header line to the next blank-line
    # followed by non-table content).
    sections = _split_md_sections(md)
    table_text = ""
    for level, heading, body in sections:
        if "citation verification" in heading.lower() or level == 2 and "1." in heading:
            table_text = body
            break
    if not table_text:
        return {}

    rows: dict[str, dict[str, str]] = {}
    # Skip the header line and any separator (|---|---|...) line.
    lines = table_text.splitlines()
    parsing = False
    for line in lines:
        stripped = line.strip()
        if _VERIFICATION_HEADER_RE.match("| " + stripped + " |" if not stripped.startswith("|") else stripped):
            parsing = True
            continue
        if not parsing:
            continue
        if not stripped.startswith("|"):
            # End of table.
            break
        if re.match(r"^\|[\s\-:|]+\|\s*$", stripped):
            continue
        # Split on |, skip first and last empty cells.
        cells = [c.strip() for c in stripped.split("|")]
        if len(cells) < 5:
            continue
        # cells[0] is empty (leading |), cells[-1] is empty (trailing |).
        study_label = cells[1]
        citation_correctness = cells[2] if len(cells) > 2 else ""
        abstract_alignment = cells[3] if len(cells) > 3 else ""
        reproducibility = cells[4] if len(cells) > 4 else ""
        coi_status = cells[5] if len(cells) > 5 else ""

        # Build a key from the study label.
        # Study labels look like "Mancino 2025 (ISCC, arXiv 2512.11850)" or
        # "sandwiched.me / Ghostlogs (May 2025, gated out)". For known
        # academic sources, pull out the family and year.
        family_match = re.search(r"\b([A-Z][A-Za-z\-']+)", study_label)
        year_match = re.search(r"((?:19|20)\d{2})", study_label)
        if family_match and year_match:
            family = family_match.group(1).lower()
            year = int(year_match.group(1))
            key = f"{family}{year}"
            rows[key] = {
                "study_label": study_label,
                "citation_correctness": citation_correctness,
                "abstract_alignment": abstract_alignment,
                "reproducibility": reproducibility,
                "coi_status": coi_status,
            }
    return rows


# Tier matrix parsing: a table of "Study | Tier | Notes" or similar.
def _parse_tier_matrix(md: str) -> dict[str, str]:
    """Parse the evidence-tier matrix from phase2_verification.md §2.

    Returns a dict keyed by family+year -> tier string (e.g. "Tier 1").
    """
    sections = _split_md_sections(md)
    out: dict[str, str] = {}
    for level, heading, body in sections:
        if "evidence tier" not in heading.lower() and "tier matrix" not in heading.lower():
            continue
        for line in body.splitlines():
            if not line.strip().startswith("|"):
                continue
            if re.match(r"^\|[\s\-:|]+\|\s*$", line):
                continue
            cells = [c.strip() for c in line.split("|")]
            if len(cells) < 3:
                continue
            study = cells[1] if cells else ""
            tier = cells[2] if len(cells) > 2 else ""
            family_match = re.search(r"\b([A-Z][A-Za-z\-']+)", study)
            year_match = re.search(r"((?:19|20)\d{2})", study)
            if family_match and year_match and tier:
                family = family_match.group(1).lower()
                year = int(year_match.group(1))
                out[f"{family}{year}"] = tier
    return out


# ----------------------------------------------------------------------------
# Passport entry assembly
# ----------------------------------------------------------------------------

# venue_type inference from the body text. The passport schema requires
# a `venue_type` (and a paired `venue_type_provenance` per the v3.10
# pair invariant). We never infer from free-form text alone when the
# section number tells us what kind of source it is; this is
# `adapter_declared` provenance.
_CATEGORY_TO_VENUE_TYPE = {
    "included": "unknown",          # we don't know the venue type from §3 headings
    "methodology_only": "journal-article",
    "stage1_excluded": "unknown",
    "stage2_excluded": "unknown",
    "preprint_in_press": "preprint",
    "skip_already_included": "unknown",
    "unknown": "unknown",
}


def _infer_venue_type_from_body(body: str) -> str:
    """Sniff common venue strings from the citation line of the body.

    We check the strongest signals first (peer-reviewed venue markers)
    and only fall back to preprint/other if those are absent. A body
    that mentions both "arXiv" and "Proceedings of the IEEE Symposium"
    is treated as a conference paper with an arXiv mirror, not a
    preprint.
    """
    # Peer-reviewed venue signals (checked first, so an arXiv mirror
    # of a published conference/journal paper is still typed correctly).
    if "Proceedings of the" in body or "Proceedings of ACM" in body:
        return "conference-paper"
    if "Symposium" in body and "IEEE" in body:
        return "conference-paper"
    if "Transactions on" in body:
        return "journal-article"
    if "Knowledge-Based Systems" in body or "Journal of" in body:
        return "journal-article"
    if re.search(r"\bACM\s+(Conference|Symposium|Web Conference)\b", body):
        return "conference-paper"

    # Preprint signals.
    if "arXiv" in body or "arxiv:" in body.lower() or "ssrn" in body.lower():
        return "preprint"

    # Other (blog, website, etc.).
    body_lower = body.lower()
    if "blog" in body_lower or ("http" in body_lower and "arxiv" not in body_lower):
        return "other"
    return "unknown"


def _build_passport_entry(
    rec: SourceRecord,
    verification_row: dict[str, str] | None,
    tier: str | None,
    citation_key_used: str,
) -> dict[str, Any]:
    """Assemble one literature_corpus_entry from a SourceRecord + verification data."""
    venue_type = _infer_venue_type_from_body(rec.body)
    # If the section number gives us a stronger signal, use it.
    if _CATEGORY_TO_VENUE_TYPE.get(rec.category) in ("preprint", "journal-article"):
        venue_type = _CATEGORY_TO_VENUE_TYPE[rec.category]

    entry: dict[str, Any] = {
        "citation_key": citation_key_used,
        "title": rec.title or rec.header,
        "authors": rec.authors,
        "year": rec.year,
        "source_pointer": rec.url or (f"https://arxiv.org/abs/{_parse_arxiv_id(rec.body)}" if _parse_arxiv_id(rec.body) else ""),
        # The user wrote the Phase 2 markdown by hand; this adapter
        # lifts sources out of it. `manual` is the closest enum value
        # in the schema; the adapter_name carries the actual
        # provenance.
        "obtained_via": "manual",
        "obtained_at": now_iso(),
        "adapter_name": ADAPTER_NAME,
        "adapter_version": ADAPTER_VERSION,
        "venue_type": venue_type,
        "venue_type_provenance": "adapter_declared",
    }

    if rec.doi:
        entry["doi"] = rec.doi
    if _parse_arxiv_id(rec.body):
        entry["arxiv_id"] = _parse_arxiv_id(rec.body)
    if rec.venue:
        entry["venue"] = rec.venue

    # Tags: drive from the category and any explicit family tags
    # extracted from the body. Keeps the tag list short and useful
    # for filtering.
    tags: list[str] = []
    if rec.category and rec.category != "included":
        tags.append(rec.category)
    for family_tag in re.findall(r"\*\*Family\*\*:\s*([^.\n]+)", rec.body):
        for f in family_tag.split(","):
            f = f.strip()
            if f and f not in tags:
                tags.append(f)
    if tags:
        entry["tags"] = tags

    # Verification provenance and evidence tier live in the
    # phase2_verification.md report (the user owns that file and
    # can join by `citation_key`). The passport schema is strict
    # on additionalProperties, so we don't carry those fields
    # here. `tier` and `verification_row` are accepted so the
    # caller can pass them, but we keep this function schema-clean.

    return entry


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--bibliography", type=Path, required=True,
        help="Path to phase2_bibliography.md",
    )
    ap.add_argument(
        "--verification", type=Path, required=True,
        help="Path to phase2_verification.md",
    )
    ap.add_argument(
        "--synthesis", type=Path, default=None,
        help="Optional path to phase3_synthesis.md (used for the static citation graph)",
    )
    ap.add_argument(
        "--output-dir", dest="output_dir", type=Path, required=True,
        help="Directory to write passport.yaml, rejection_log.yaml, bib.csl.json, bib.bib, bib.citegraph.json",
    )
    ap.add_argument(
        "--with-live-citations", dest="with_live_citations", action="store_true",
        help="Pull live citation edges from Semantic Scholar (slower; requires network)",
    )
    args = ap.parse_args()

    if not args.bibliography.exists():
        print(f"ERROR: bibliography not found: {args.bibliography}", file=sys.stderr)
        return 1
    if not args.verification.exists():
        print(f"ERROR: verification not found: {args.verification}", file=sys.stderr)
        return 1

    args.output_dir.mkdir(parents=True, exist_ok=True)

    bibliography_text = args.bibliography.read_text(encoding="utf-8")
    verification_text = args.verification.read_text(encoding="utf-8")
    synthesis_text = args.synthesis.read_text(encoding="utf-8") if args.synthesis and args.synthesis.exists() else ""

    # Parse.
    records = _parse_bibliography(bibliography_text)
    verification_rows = _parse_verification_table(verification_text)
    tier_rows = _parse_tier_matrix(verification_text)

    # Assemble passport entries + rejections.
    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    seen_keys: set[str] = set()

    for rec in records:
        # Drop §5.4 meta-notes: they're commentary about already-
        # included sources, not new entries.
        if rec.category == "skip_already_included":
            continue

        # Build a join key against the verification table.
        join_key = parse_family_year_key(rec.authors, rec.year) if rec.authors else ""
        if not join_key and rec.header:
            # Fall back: try the header.
            family_match = re.search(r"\b([A-Z][A-Za-z\-']+)", rec.header)
            if family_match and rec.year:
                join_key = f"{family_match.group(1).lower()}{rec.year}"
        verification_row = verification_rows.get(join_key)
        tier = tier_rows.get(join_key)

        # Reject if there's no verification row at all (the
        # bibliography is the source of truth; everything in it must
        # be verifiable).
        if not verification_row and rec.category == "included":
            rejected.append({
                "source": rec.header,
                "reason": "unresolvable_source_pointer",
                "detail": f"included study has no matching row in verification table (join key: {join_key!r})",
                "raw": rec.header,
            })
            continue

        # Reject methodology-only sources with a clear reason.
        if rec.category == "methodology_only":
            rejected.append({
                "source": rec.header,
                "reason": "methodology_only_not_strategy_result",
                "detail": "Cited as a methodology reference, not a strategy result; excluded from primary evidence matrix.",
                "raw": rec.header,
            })
            continue

        # Reject stage-1 and stage-2 exclusions from the passport
        # but record them in the rejection log so downstream
        # tools can still see what was screened.
        if rec.category in ("stage1_excluded", "stage2_excluded", "preprint_in_press"):
            reason_map = {
                "stage1_excluded": "stage1_no_solana_mapping_or_gray_literature",
                "stage2_excluded": "stage2_gate_failure",
                "preprint_in_press": "preprint_in_press_no_artifact",
            }
            rejected.append({
                "source": rec.header,
                "reason": reason_map[rec.category],
                "detail": (rec.body.splitlines()[0] if rec.body else "").strip()[:200],
                "raw": rec.header,
            })
            continue

        # Build the citekey from the bibliography's natural key
        # (first-author family + year + first-title-word) so it
        # matches what a human reading the report would expect.
        family = rec.authors[0].get("family", "") if rec.authors else ""
        title_hint = rec.title or rec.header
        first_title_word = ""
        for word in re.findall(r"[A-Za-z]+", title_hint):
            if word.lower() not in ("a", "an", "the", "of", "in", "on", "for", "to", "and", "or"):
                first_title_word = word
                break

        if family and rec.year:
            base_key = make_citation_key(
                family=family,
                year=rec.year,
                title_hint=first_title_word,
                existing=seen_keys,
            )
        else:
            # Fall back to a sanitized header.
            base = re.sub(r"[^A-Za-z0-9]+", "", rec.header)[:24] or "ref"
            base_key = ensure_unique_citekey(base, seen_keys)
        seen_keys.add(base_key)

        entry = _build_passport_entry(rec, verification_row, tier, base_key)
        accepted.append(entry)

    # Write outputs.
    passport_path = args.output_dir / "passport.yaml"
    rejection_path = args.output_dir / "rejection_log.yaml"
    csl_path = args.output_dir / "bib.csl.json"
    bib_path = args.output_dir / "bib.bib"
    graph_path = args.output_dir / "bib.citegraph.json"

    write_passport(passport_path, accepted)
    write_rejection_log(
        rejection_path,
        adapter_name=ADAPTER_NAME,
        adapter_version=ADAPTER_VERSION,
        rejected=rejected,
        total_input=len(records),
        total_accepted=len(accepted),
    )
    write_csl_json(accepted, csl_path)
    write_bibtex(accepted, bib_path)

    # Citation graph.
    corpus_texts: list[tuple[str, str]] = []
    if synthesis_text:
        corpus_texts.append(("synthesis", synthesis_text))
    if bibliography_text:
        corpus_texts.append(("bibliography", bibliography_text))

    s2_client = None
    if args.with_live_citations:
        try:
            from scripts.semantic_scholar_client import SemanticScholarClient
            s2_client = SemanticScholarClient()
        except Exception as exc:  # noqa: BLE001
            print(
                f"WARN: could not initialize SemanticScholarClient: {exc}; "
                "falling back to static-only graph",
                file=sys.stderr,
            )

    graph = build_graph(accepted, corpus_texts, s2_client=s2_client)
    write_graph(graph, graph_path)

    print(
        f"Wrote {len(accepted)} passport entries, {len(rejected)} rejections, "
        f"{len(graph['edges'])} graph edges to {args.output_dir}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
