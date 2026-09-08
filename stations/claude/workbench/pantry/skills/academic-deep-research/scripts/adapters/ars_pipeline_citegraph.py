#!/usr/bin/env python3
"""Citation graph builder for the ars_pipeline adapter.

Two passes:

1. Static edges — derived from `phase2_bibliography.md` and
   `phase3_synthesis.md`. The synthesis file mentions papers with
   patterns like `(Mancino, 2025)`, `Huynh et al. (2025)`,
   `Gerzon et al., 2025`. We regex-match those mentions, look up the
   citation_key for the mentioned paper in the passport, and emit
   edges. Co-citation comes from two papers being cited by the same
   third paper.

2. Live edges — when `--with-live-citations` is set, for each passport
   entry we call Semantic Scholar's `/paper/{id}/citations` and
   `/paper/{id}/references` endpoints. Each citing/cited paper that
   resolves to a known passport entry becomes a live edge. Citing
   papers NOT in the passport are recorded as `external` so a future
   re-run can incorporate them. Failures land in the rejection log
   rather than aborting the run (fail-soft).

Output: a single JSON object with `edges[]`, `co_citations[]`, and
`unresolved[]` arrays.
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

# Citation mention patterns. We match four common forms:
#   (Family, YYYY)              e.g. "(Mancino, 2025)"
#   (Family et al., YYYY)       e.g. "(Huynh et al., 2025)"
#   Family (YYYY)               e.g. "Gerzon (2025)"
#   Family et al. (YYYY)        e.g. "Huynh et al. (2025)"
#
# The regex captures the family name (or the first family for et al.)
# and the year as separate groups.
_CITATION_RE = re.compile(
    r"""
    (?<![A-Za-z])              # not part of a longer word
    (?P<family>[A-Z][A-Za-z\-']+)
    (?:\s+et\s+al\.?)?         # optional "et al."
    [,\s]+
    (?:\()?                    # optional opening paren
    (?P<year>(?:19|20)\d{2})
    (?:\))?                    # optional closing paren
    """,
    re.VERBOSE,
)

# Co-citation: within a single sentence, two or more citation mentions
# share a citing context. We split on sentence boundaries then look
# for multiple matches per sentence.
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+|\n\n+")

# Throttle the live-citation pull: limit to first N sources if a corpus
# is very large. The full pipeline corpus is ~20 sources; the cap is a
# safety net for unusually large corpora.
_LIVE_PULL_MAX = 100

# How many sentences of context to keep for a static edge. We pick a
# window around the citation mention so a graph viewer has something
# useful to show.
_CONTEXT_CHARS = 240


def _passport_key_by_family_year(
    entries: list[dict[str, Any]],
) -> dict[tuple[str, int], str]:
    """Index passport entries by (lowercased first family, year) -> citekey.

    Used to look up a citation mention in the corpus. For papers with
    multiple authors, the citekey is keyed on the first family.
    """
    index: dict[tuple[str, int], str] = {}
    for e in entries:
        authors = e.get("authors") or []
        if not authors:
            continue
        first = authors[0]
        family = (first.get("family") or first.get("literal") or "").strip().lower()
        if not family or e.get("year") is None:
            continue
        key = (family, int(e["year"]))
        if key not in index:
            index[key] = e["citation_key"]
    return index


def _passport_key_by_s2_id(
    entries: list[dict[str, Any]],
) -> dict[str, str]:
    """Index passport entries by Semantic Scholar paperId -> citekey.

    Used to match a live-edge paper against the corpus.
    """
    index: dict[str, str] = {}
    for e in entries:
        s2 = e.get("semantic_scholar_id")
        if s2:
            index[s2] = e["citation_key"]
    return index


def _build_static_edges(
    entries: list[dict[str, Any]],
    corpus_texts: list[tuple[str, str]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Pass 1: regex citation mentions across corpus text.

    `corpus_texts` is a list of `(source_name, text)` pairs. The
    source_name is one of "bibliography" or "synthesis"; edges
    carry the source so a viewer can tell where they came from.

    Returns (edges, co_citations).
    """
    key_index = _passport_key_by_family_year(entries)
    if not key_index:
        return [], []

    edges: list[dict[str, Any]] = []
    seen_edges: set[tuple[str, str, str]] = set()  # (citing, cited, source)

    for source_name, text in corpus_texts:
        # Per-sentence pass: collect citations and build edges.
        for sentence in _SENTENCE_SPLIT_RE.split(text):
            sentence_cited: list[str] = []
            for m in _CITATION_RE.finditer(sentence):
                family = m.group("family").lower()
                try:
                    year = int(m.group("year"))
                except (TypeError, ValueError):
                    continue
                key = (family, year)
                if key not in key_index:
                    continue
                sentence_cited.append(key_index[key])

            # Dedupe within the sentence; preserve order.
            seen_in_sentence: set[str] = set()
            unique_cited = []
            for c in sentence_cited:
                if c not in seen_in_sentence:
                    seen_in_sentence.add(c)
                    unique_cited.append(c)

            # All cited papers in this sentence are co-cited by every
            # other paper in the sentence. The "citing" for a static
            # edge is the source the citation appears in (bibliography
            # entry or synthesis). The "cited" is the cited paper.
            #
            # For the static pass, every paper that is mentioned in
            # the synthesis (or in another paper's bibliography
            # entry) gets a static edge from "synthesis" or
            # "bibliography" to the mentioned paper. The "citing"
            # node is the synthesis or the citing entry; the "cited"
            # node is the mentioned paper.
            #
            # We don't have a clear "citing node" for synthesis text
            # itself, so we use the synthesis/bibliography source as
            # the citing anchor and record the context sentence.

            for cited in unique_cited:
                edge = (source_name, cited, source_name)
                if edge in seen_edges:
                    continue
                seen_edges.add(edge)
                ctx = sentence.strip()[:_CONTEXT_CHARS]
                edges.append({
                    "citing": source_name,
                    "cited": cited,
                    "context": ctx if ctx else None,
                    "source": source_name,
                })

    # Co-citations: pairs of papers cited together in the same sentence.
    co_citations: list[dict[str, Any]] = []
    seen_co: set[tuple[str, str, str]] = set()
    for source_name, text in corpus_texts:
        for sentence in _SENTENCE_SPLIT_RE.split(text):
            sentence_cited: list[str] = []
            for m in _CITATION_RE.finditer(sentence):
                family = m.group("family").lower()
                try:
                    year = int(m.group("year"))
                except (TypeError, ValueError):
                    continue
                key = (family, year)
                if key not in key_index:
                    continue
                if key_index[key] not in sentence_cited:
                    sentence_cited.append(key_index[key])
            # All pairs in this sentence.
            for i in range(len(sentence_cited)):
                for j in range(i + 1, len(sentence_cited)):
                    a, b = sorted([sentence_cited[i], sentence_cited[j]])
                    ctx_anchor = (source_name, a, b)
                    if ctx_anchor in seen_co:
                        continue
                    seen_co.add(ctx_anchor)
                    co_citations.append({
                        "paper_a": a,
                        "paper_b": b,
                        "co_cited_by": source_name,
                    })

    return edges, co_citations


def _build_live_edges(
    entries: list[dict[str, Any]],
    s2_client: Any | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Pass 2: Semantic Scholar /citations and /references.

    Returns (live_edges, unresolved). Failures per source land in
    `unresolved` rather than aborting the run.
    """
    if s2_client is None:
        return [], []

    key_by_s2 = _passport_key_by_s2_id(entries)
    live_edges: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []

    sources_to_query = [e for e in entries if e.get("doi") or e.get("title")][: _LIVE_PULL_MAX]

    for entry in sources_to_query:
        citekey = entry.get("citation_key", "")
        try:
            lookup = s2_client.lookup(entry)
        except Exception as exc:  # noqa: BLE001 - any failure is a soft error here
            unresolved.append({
                "citation_key": citekey,
                "reason": f"S2 lookup raised: {type(exc).__name__}: {exc}",
                "source": "semantic_scholar_live",
            })
            continue

        if not lookup.get("matched"):
            unresolved.append({
                "citation_key": citekey,
                "reason": "S2 returned no Semantic Scholar paperId",
                "source": "semantic_scholar_live",
            })
            continue

        s2_id = lookup["paperId"]

        # /citations: who cites this paper?
        try:
            citations_data = s2_client._request(  # noqa: SLF001 - direct call is fine here
                f"/paper/{s2_id}/citations?fields=paperId,title,year&limit=100"
            )
        except Exception as exc:  # noqa: BLE001
            unresolved.append({
                "citation_key": citekey,
                "reason": f"S2 /citations failed: {type(exc).__name__}: {exc}",
                "source": "semantic_scholar_live",
            })
            citations_data = {}

        for cit_block in citations_data.get("data", []) or []:
            citing_paper = cit_block.get("citingPaper") or {}
            citing_id = citing_paper.get("paperId")
            if not citing_id:
                continue
            if citing_id in key_by_s2:
                live_edges.append({
                    "citing": key_by_s2[citing_id],
                    "cited": citekey,
                    "context": None,
                    "source": "semantic_scholar_live",
                    "confidence": 1.0,
                })
            else:
                live_edges.append({
                    "external": citing_id,
                    "external_title": citing_paper.get("title"),
                    "external_year": citing_paper.get("year"),
                    "role": "cited_by",
                    "in_corpus": False,
                    "cites": citekey,
                    "source": "semantic_scholar_live",
                    "confidence": 1.0,
                })

        # /references: what does this paper cite?
        try:
            refs_data = s2_client._request(  # noqa: SLF001
                f"/paper/{s2_id}/references?fields=paperId,title,year&limit=100"
            )
        except Exception as exc:  # noqa: BLE001
            unresolved.append({
                "citation_key": citekey,
                "reason": f"S2 /references failed: {type(exc).__name__}: {exc}",
                "source": "semantic_scholar_live",
            })
            refs_data = {}

        for ref_block in refs_data.get("data", []) or []:
            cited_paper = ref_block.get("citedPaper") or {}
            cited_id = cited_paper.get("paperId")
            if not cited_id:
                continue
            if cited_id in key_by_s2:
                live_edges.append({
                    "citing": citekey,
                    "cited": key_by_s2[cited_id],
                    "context": None,
                    "source": "semantic_scholar_live",
                    "confidence": 1.0,
                })
            else:
                live_edges.append({
                    "external": cited_id,
                    "external_title": cited_paper.get("title"),
                    "external_year": cited_paper.get("year"),
                    "role": "cites",
                    "in_corpus": False,
                    "cites": citekey,
                    "source": "semantic_scholar_live",
                    "confidence": 1.0,
                })

    return live_edges, unresolved


def build_graph(
    entries: list[dict[str, Any]],
    corpus_texts: list[tuple[str, str]],
    s2_client: Any | None = None,
) -> dict[str, Any]:
    """Build the full citation graph for the corpus.

    `entries` is the list of passport entries (literature_corpus[]).
    `corpus_texts` is a list of `(source_name, text)` pairs to scan
    for citation mentions. `s2_client` is a SemanticScholarClient
    instance, or None to skip live edges.
    """
    static_edges, co_citations = _build_static_edges(entries, corpus_texts)
    live_edges, unresolved = _build_live_edges(entries, s2_client)

    all_edges = static_edges + live_edges

    # Sort for determinism.
    all_edges.sort(
        key=lambda e: (
            e.get("citing", ""),
            e.get("cited", e.get("external", "")),
            e.get("source", ""),
        )
    )
    co_citations.sort(key=lambda c: (c["paper_a"], c["paper_b"], c["co_cited_by"]))
    unresolved.sort(key=lambda u: u.get("citation_key", ""))

    return {
        "schema": "ars_citegraph/1",
        "nodes_total": len(entries),
        "edges_static": len(static_edges),
        "edges_live": len(live_edges),
        "edges": all_edges,
        "co_citations": co_citations,
        "unresolved": unresolved,
    }


def write_graph(graph: dict[str, Any], path: Path) -> None:
    """Write the graph to a JSON file."""
    path.write_text(
        json.dumps(graph, indent=2, ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--passport", type=Path, required=True,
        help="Path to passport.yaml",
    )
    ap.add_argument(
        "--synthesis", type=Path, default=None,
        help="Optional path to phase3_synthesis.md for static edge extraction",
    )
    ap.add_argument(
        "--bibliography", type=Path, default=None,
        help="Optional path to phase2_bibliography.md for static edge extraction",
    )
    ap.add_argument(
        "--output", type=Path, required=True,
        help="Path to write bib.citegraph.json",
    )
    args = ap.parse_args()

    import yaml
    passport = yaml.safe_load(args.passport.read_text(encoding="utf-8"))
    entries = passport.get("literature_corpus", [])

    corpus_texts: list[tuple[str, str]] = []
    if args.synthesis and args.synthesis.exists():
        corpus_texts.append(("synthesis", args.synthesis.read_text(encoding="utf-8")))
    if args.bibliography and args.bibliography.exists():
        corpus_texts.append(("bibliography", args.bibliography.read_text(encoding="utf-8")))

    graph = build_graph(entries, corpus_texts, s2_client=None)
    write_graph(graph, args.output)
    print(
        f"Wrote graph: {len(graph['edges'])} edges, "
        f"{len(graph['co_citations'])} co-citations, "
        f"{len(graph['unresolved'])} unresolved",
        file=sys.stderr,
    )
