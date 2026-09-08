#!/usr/bin/env python3
"""export_graph_data: dump citegraph.sqlite into the two files citegraph.html
and the researcher actually look at:

  - graph_data.json — nodes + edges for citegraph.html (same shape as
    before, extended with hop_distance / relevance_verdict / is_seed so
    the page can filter/style by them without another schema change)
  - candidates_for_review.md — papers not yet in the seed corpus with a
    relevant/uncertain verdict, ranked by citation count, for manual
    promotion into phase2_bibliography.md

No live API calls here — this only reads the local db.

Usage:
    python scripts/export_graph_data.py [--config PATH]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import _db  # noqa: E402


def export(conn, corpus_dir: Path) -> None:
    rows = conn.execute("SELECT * FROM papers").fetchall()
    edges = conn.execute("SELECT * FROM edges").fetchall()

    # citation_count is NULL when no API ever resolved it (rate-limited, or the
    # paper isn't indexed) — that's "unknown," not zero. But the crawl itself
    # may have already discovered real papers citing this one (in-degree in
    # `edges`), which is a verified lower bound. Never display a number lower
    # than what we've actually found, and never silently turn "unknown" into 0.
    in_degree: dict[str, int] = {}
    for e in edges:
        in_degree[e["cited_id"]] = in_degree.get(e["cited_id"], 0) + 1

    nodes = []
    for r in rows:
        if r["year"] is None:  # can't be color-scaled meaningfully
            continue
        crawled_citers = in_degree.get(r["id"], 0)
        if r["citation_count"] is not None:
            citations = max(r["citation_count"], crawled_citers)
            source = r["citation_count_source"] or "unknown"
        elif crawled_citers > 0:
            citations = crawled_citers
            source = "crawled_edges (lower bound — no API citation count resolved)"
        else:
            citations = 0
            source = "unknown"
        nodes.append({
            "id": r["id"],
            "title": r["title"],
            "venue": r["venue"] or "",
            "year": r["year"],
            "citations": citations,
            "citation_count_source": source,
            "is_seed": bool(r["is_seed"]),
            "hop_distance": r["hop_distance"],
            "relevance_verdict": r["relevance_verdict"],
            "family": r["family"],
        })
    node_ids = {n["id"] for n in nodes}
    links = [
        {"source": e["citing_id"], "target": e["cited_id"], "source_api": e["source"]}
        for e in edges
        if e["citing_id"] in node_ids and e["cited_id"] in node_ids
    ]

    graph_data = {
        "nodes": nodes,
        "links": links,
        "edge_check": "Edges are real citation relationships (OpenAlex referenced_works / cites-filter, "
                       "Semantic Scholar references/citations fallback) discovered by graphlookup's crawl, "
                       "not the co-occurrence placeholder used before this corpus had any crawled papers.",
    }
    (corpus_dir / "graph_data.json").write_text(json.dumps(graph_data, indent=2))

    def best_known_citations(r) -> int:
        return max(r["citation_count"] or 0, in_degree.get(r["id"], 0))

    candidates = sorted(
        (r for r in rows if not r["is_seed"] and r["relevance_verdict"] in ("highly_relevant", "relevant", "uncertain")),
        key=best_known_citations,
        reverse=True,
    )
    lines = ["# Candidates for review\n",
             "Papers found by graphlookup that aren't in the seed corpus yet, ranked by citation count. "
             "Verdict and reasoning are from a free-tier model — treat as a first pass, not ground truth.\n"]
    for r in candidates:
        crawled_citers = in_degree.get(r["id"], 0)
        if r["citation_count"] is not None:
            cite_text = f"{r['citation_count']} ({r['citation_count_source'] or 'unknown'})"
        elif crawled_citers > 0:
            cite_text = f"at least {crawled_citers} (found via crawled edges, no API count resolved)"
        else:
            cite_text = "unknown"
        lines.append(
            f"## {r['title']}\n\n"
            f"- Verdict: **{r['relevance_verdict']}** — {r['relevance_reasoning'] or '(no reasoning recorded)'}\n"
            f"- Venue: {r['venue'] or 'unknown'} ({r['year'] or 'unknown year'})\n"
            f"- Citations: {cite_text}\n"
            f"- DOI: {r['doi'] or '—'}  |  arXiv: {r['arxiv_id'] or '—'}\n"
            f"- Hop distance from seed corpus: {r['hop_distance']}\n"
        )
    (corpus_dir / "candidates_for_review.md").write_text("\n".join(lines))

    families = conn.execute("SELECT * FROM families ORDER BY is_original DESC, name ASC").fetchall()
    paper_counts: dict[str, int] = {}
    for r in rows:
        if r["family"]:
            paper_counts[r["family"]] = paper_counts.get(r["family"], 0) + 1

    flines = ["# Families\n",
              "The current tag vocabulary for this corpus — the 9 original strategy families from "
              "phase1_revised_v2.md, plus any the classifier has proposed since (auto-accepted, "
              "fuzzy-deduped against the existing list — see graphlookup/SKILL.md). This is the "
              "single source of truth for tag names; `citegraph.html`'s by-tag clustering reads "
              "directly off `graph_data.json`'s per-node `family` field, which comes from here.\n"]
    for f in families:
        origin = "original (phase1)" if f["is_original"] else f"discovered via crawl (from {f['created_from_paper_id']})"
        flines.append(
            f"## {f['name']}\n\n"
            f"- Papers tagged: {paper_counts.get(f['name'], 0)}\n"
            f"- Origin: {origin}\n"
            + (f"- {f['description']}\n" if f["description"] else "")
        )
    (corpus_dir / "families.md").write_text("\n".join(flines))

    print(f"Exported {len(nodes)} nodes, {len(links)} edges -> {corpus_dir / 'graph_data.json'}")
    print(f"{len(candidates)} candidates for review -> {corpus_dir / 'candidates_for_review.md'}")
    print(f"{len(families)} families ({sum(1 for f in families if not f['is_original'])} crawl-discovered) -> {corpus_dir / 'families.md'}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--config", type=Path, default=Path(__file__).parent.parent / "config.json")
    args = parser.parse_args()

    config = json.loads(args.config.read_text())
    repo_root = Path.cwd()
    conn = _db.connect(repo_root / config["db_path"])
    export(conn, repo_root / config["corpus_dir"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
