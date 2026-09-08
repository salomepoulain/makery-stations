#!/usr/bin/env python3
"""crawl: recursively expand the citation graph in citegraph.sqlite outward
from the seed papers in passport.yaml.

Backward (references) and forward (citing works) edges come from OpenAlex
first (generous rate limit, native bidirectional citation queries), with
Semantic Scholar as a fallback for works OpenAlex doesn't index (mainly very
new arXiv preprints). A citation count with no source in either API is left
as NULL/"unknown" here — filling it from Google Scholar via the browse skill
is a separate, human-in-the-loop step (see record_citation_count.py), not
something this script can do on its own since browse isn't callable from
a plain script.

The crawl/expansion heuristic (citation count, recency) only decides which
un-expanded nodes get expanded first within this run's fanout/node budget.
It never excludes a discovered paper from being stored — every paper found
gets inserted and is eligible for classify_relevance.py regardless of score.

Rerunning this script resumes from whatever is still `expanded=0`: that is
the "look deeper" workflow, no separate flag needed.

Usage:
    python scripts/crawl.py [--max-hops N] [--fanout-top-n N]
        [--node-budget N] [--date-floor YEAR] [--config PATH]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).parent))
import _db  # noqa: E402

_OPENALEX = "https://api.openalex.org/works"
_S2 = "https://api.semanticscholar.org/graph/v1/paper"
_MIN_INTERVAL = 1.0
_S2_MIN_INTERVAL = 3.5  # S2's unauthenticated limit is much tighter; back off harder

_last_openalex_call = 0.0
_last_s2_call = 0.0


def _throttle(which: str) -> None:
    global _last_openalex_call, _last_s2_call
    now = time.monotonic()
    if which == "openalex":
        wait = _MIN_INTERVAL - (now - _last_openalex_call)
        if wait > 0:
            time.sleep(wait)
        _last_openalex_call = time.monotonic()
    else:
        wait = _S2_MIN_INTERVAL - (now - _last_s2_call)
        if wait > 0:
            time.sleep(wait)
        _last_s2_call = time.monotonic()


def _get_json(url: str, which: str, retries: int = 3) -> dict[str, Any] | None:
    for attempt in range(retries):
        _throttle(which)
        req = urllib.request.Request(url, headers={"User-Agent": "graphlookup/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:  # nosec B310
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if e.code == 429 and attempt < retries - 1:
                time.sleep(5 * (attempt + 1))
                continue
            return None
        except (urllib.error.URLError, TimeoutError):
            return None
    return None


def openalex_work_by_id(oa_id: str) -> dict[str, Any] | None:
    short = oa_id.rsplit("/", 1)[-1]
    return _get_json(
        f"{_OPENALEX}/{short}?select=id,doi,title,abstract_inverted_index,"
        "publication_year,primary_location,cited_by_count,referenced_works",
        "openalex",
    )


def openalex_work_by_doi(doi: str) -> dict[str, Any] | None:
    quoted = urllib.parse.quote(doi, safe="")
    return _get_json(
        f"{_OPENALEX}/doi:{quoted}?select=id,doi,title,abstract_inverted_index,"
        "publication_year,primary_location,cited_by_count,referenced_works",
        "openalex",
    )


def openalex_citers(oa_id: str, limit: int = 50) -> list[dict[str, Any]]:
    short = oa_id.rsplit("/", 1)[-1]
    data = _get_json(
        f"{_OPENALEX}?filter=cites:{short}&per_page={limit}"
        "&select=id,doi,title,publication_year,cited_by_count",
        "openalex",
    )
    return (data or {}).get("results", [])


def _rebuild_abstract(inverted_index: dict[str, list[int]] | None) -> str | None:
    """OpenAlex serves abstracts as an inverted index (word -> positions),
    not plain text, per their API's copyright-safe format."""
    if not inverted_index:
        return None
    positions: dict[int, str] = {}
    for word, idxs in inverted_index.items():
        for i in idxs:
            positions[i] = word
    return " ".join(positions[i] for i in sorted(positions))


def s2_paper(id_str: str) -> dict[str, Any] | None:
    return _get_json(
        f"{_S2}/{id_str}?fields=title,abstract,year,citationCount,externalIds,"
        "references.title,references.externalIds,references.year,"
        "citations.title,citations.externalIds,citations.year",
        "s2",
    )


def canonical_id(oa_work: dict[str, Any] | None, doi: str | None, arxiv_id: str | None, fallback_title: str) -> str:
    if oa_work and oa_work.get("id"):
        return oa_work["id"]
    if doi:
        return f"doi:{doi}"
    if arxiv_id:
        return f"arxiv:{arxiv_id}"
    return f"title:{fallback_title.lower()[:80]}"


def load_config(path: Path, overrides: argparse.Namespace) -> dict[str, Any]:
    config = json.loads(path.read_text())
    for key in ("max_hops", "fanout_top_n", "node_budget", "date_floor"):
        cli_val = getattr(overrides, key.replace("-", "_"), None)
        if cli_val is not None:
            config[key] = cli_val
    return config


def seed_papers(passport_path: Path) -> list[dict[str, Any]]:
    passport = yaml.safe_load(passport_path.read_text())
    return passport.get("literature_corpus", [])


def priority_score(citation_count: int | None, year: int | None) -> float:
    c = citation_count or 0
    recency = max(0, (year or 2000) - 2018)
    return c + recency * 2


def upsert_from_openalex(conn, oa_work: dict[str, Any], hop_distance: int, discovered_via: str | None, is_seed: bool) -> str:
    oa_id = oa_work["id"]
    venue = ((oa_work.get("primary_location") or {}).get("source") or {}).get("display_name")
    paper = {
        "id": oa_id,
        "doi": oa_work.get("doi"),
        "arxiv_id": None,
        "title": oa_work.get("title") or "(untitled)",
        "abstract": _rebuild_abstract(oa_work.get("abstract_inverted_index")),
        "venue": venue,
        "year": oa_work.get("publication_year"),
        "citation_count": oa_work.get("cited_by_count"),
        "citation_count_source": "openalex",
        "is_seed": 1 if is_seed else 0,
        "hop_distance": hop_distance,
        "discovered_via": discovered_via,
    }
    paper["crawl_priority_score"] = priority_score(paper["citation_count"], paper["year"])
    _db.upsert_paper(conn, paper)
    return oa_id


def expand_seeds(conn, config: dict[str, Any]) -> None:
    for entry in seed_papers(Path(config["passport_path"])):
        doi = entry.get("doi")
        arxiv_id = entry.get("arxiv_id")
        oa_work = openalex_work_by_doi(doi) if doi else None
        if oa_work:
            upsert_from_openalex(conn, oa_work, hop_distance=0, discovered_via=None, is_seed=True)
            continue
        # OpenAlex miss (typically a very new arXiv preprint) -> Semantic Scholar
        s2_id = f"arXiv:{arxiv_id.split('v')[0]}" if arxiv_id else (f"DOI:{doi}" if doi else None)
        s2_data = s2_paper(s2_id) if s2_id else None
        paper = {
            "id": canonical_id(None, doi, arxiv_id, entry["title"]),
            "doi": doi,
            "arxiv_id": arxiv_id,
            "title": entry["title"],
            "abstract": (s2_data or {}).get("abstract"),
            "venue": entry.get("venue"),
            "year": (s2_data or {}).get("year") or entry.get("year"),
            "citation_count": (s2_data or {}).get("citationCount"),
            "citation_count_source": "semantic_scholar" if s2_data and s2_data.get("citationCount") is not None else "unknown",
            "is_seed": 1,
            "hop_distance": 0,
            "discovered_via": None,
        }
        paper["crawl_priority_score"] = priority_score(paper["citation_count"], paper["year"])
        _db.upsert_paper(conn, paper)


def _s2_id_for_row(paper_row) -> str | None:
    if paper_row["arxiv_id"]:
        return f"arXiv:{paper_row['arxiv_id'].split('v')[0]}"
    if paper_row["doi"]:
        return f"DOI:{paper_row['doi']}"
    return None


def upsert_from_s2_ref(conn, ref: dict[str, Any], hop_distance: int, discovered_via: str, is_seed: bool) -> str | None:
    """Upserts a Semantic Scholar reference/citation stub. Tries to resolve it
    through OpenAlex by DOI first (richer metadata, a real citation count);
    falls back to the bare S2 fields (no citation count) otherwise."""
    ext = ref.get("externalIds") or {}
    doi = ext.get("DOI")
    title = ref.get("title")
    if not title:
        return None
    if doi:
        oa_work = openalex_work_by_doi(doi)
        if oa_work:
            return upsert_from_openalex(conn, oa_work, hop_distance, discovered_via, is_seed)
    arxiv_id = ext.get("ArXiv")
    child_id = canonical_id(None, doi, arxiv_id, title)
    paper = {
        "id": child_id,
        "doi": doi,
        "arxiv_id": arxiv_id,
        "title": title,
        "abstract": None,
        "venue": None,
        "year": ref.get("year"),
        "citation_count": None,
        "citation_count_source": "unknown",
        "is_seed": 1 if is_seed else 0,
        "hop_distance": hop_distance,
        "discovered_via": discovered_via,
    }
    paper["crawl_priority_score"] = priority_score(None, paper["year"])
    _db.upsert_paper(conn, paper)
    return child_id


def expand_one(conn, paper_row, config: dict[str, Any]) -> int:
    """Expands one paper's neighbors. Returns the number of new papers inserted."""
    parent_id = paper_row["id"]
    inserted = 0
    date_floor = config["date_floor"]
    fanout = config["fanout_top_n"]
    attempted = False

    if parent_id.startswith("https://openalex.org/"):
        attempted = True
        oa_work = openalex_work_by_id(parent_id)
        if oa_work:
            # Backward: referenced_works, filtered by date floor, capped by fanout.
            ref_ids = (oa_work.get("referenced_works") or [])[: fanout * 2]
            ref_works = [w for w in (openalex_work_by_id(r) for r in ref_ids) if w]
            ref_works = [w for w in ref_works if (w.get("publication_year") or 0) >= date_floor]
            ref_works.sort(key=lambda w: w.get("cited_by_count") or 0, reverse=True)
            for w in ref_works[:fanout]:
                child_id = upsert_from_openalex(conn, w, hop_distance=paper_row["hop_distance"] + 1, discovered_via=parent_id, is_seed=False)
                _db.add_edge(conn, citing_id=parent_id, cited_id=child_id, source="openalex")
                inserted += 1

            # Forward: works that cite this one, capped by fanout, no date floor.
            citers = openalex_citers(parent_id, limit=fanout * 2)
            citers.sort(key=lambda w: w.get("cited_by_count") or 0, reverse=True)
            for w in citers[:fanout]:
                child_id = upsert_from_openalex(conn, w, hop_distance=paper_row["hop_distance"] + 1, discovered_via=parent_id, is_seed=False)
                _db.add_edge(conn, citing_id=child_id, cited_id=parent_id, source="openalex")
                inserted += 1

    elif parent_id.startswith("arxiv:") or parent_id.startswith("doi:"):
        # OpenAlex doesn't index this one (typically a very new arXiv preprint) —
        # Semantic Scholar fallback, one call gets both references and citations.
        s2_id = _s2_id_for_row(paper_row)
        s2_data = s2_paper(s2_id) if s2_id else None
        if s2_data:
            attempted = True
            refs = (s2_data.get("references") or [])[:fanout]
            for ref in refs:
                if (ref.get("year") or 0) < date_floor:
                    continue
                child_id = upsert_from_s2_ref(conn, ref, hop_distance=paper_row["hop_distance"] + 1, discovered_via=parent_id, is_seed=False)
                if child_id:
                    _db.add_edge(conn, citing_id=parent_id, cited_id=child_id, source="semantic_scholar")
                    inserted += 1
            for cit in (s2_data.get("citations") or [])[:fanout]:
                child_id = upsert_from_s2_ref(conn, cit, hop_distance=paper_row["hop_distance"] + 1, discovered_via=parent_id, is_seed=False)
                if child_id:
                    _db.add_edge(conn, citing_id=child_id, cited_id=parent_id, source="semantic_scholar")
                    inserted += 1
        # else: S2 lookup failed (404 / rate-limited) — leave expanded=0 so a
        # later rerun retries it, rather than silently losing it forever.

    else:
        # No doi/arxiv_id at all (title-only canonical id) — nothing more we can
        # fetch for this one; mark it done so it doesn't loop forever.
        attempted = True

    if attempted:
        _db.mark_expanded(conn, parent_id)
    return inserted


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--max-hops", type=int, default=None)
    parser.add_argument("--fanout-top-n", type=int, default=None)
    parser.add_argument("--node-budget", type=int, default=None)
    parser.add_argument("--date-floor", type=int, default=None)
    parser.add_argument("--config", type=Path, default=Path(__file__).parent.parent / "config.json")
    args = parser.parse_args()

    config = load_config(args.config, args)
    repo_root = Path.cwd()
    db_path = repo_root / config["db_path"]

    conn = _db.connect(db_path)
    if _db.total_papers(conn) == 0:
        print("Seeding from passport.yaml...")
        expand_seeds(conn, config)

    inserted_this_run = 0
    while _db.total_papers(conn) < config["node_budget"]:
        candidates = _db.unexpanded_within_hops(conn, config["max_hops"])
        if not candidates:
            break
        target = candidates[0]
        print(f"Expanding [{target['hop_distance']}] {target['title'][:70]}...")
        inserted_this_run += expand_one(conn, target, config)

    effective_config_path = repo_root / config["corpus_dir"] / "graphlookup_config.effective.json"
    effective_config_path.write_text(json.dumps(config, indent=2))

    print(f"Done. {inserted_this_run} new papers this run, {_db.total_papers(conn)} total in db.")
    print(f"Effective config written to {effective_config_path}")
    print("Next: run classify_relevance.py, then export_graph_data.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
