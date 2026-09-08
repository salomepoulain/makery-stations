"""SQLite schema and helpers shared by crawl.py and export_graph_data.py."""
from __future__ import annotations

import sqlite3
import time
from pathlib import Path
from typing import Any

SCHEMA = """
CREATE TABLE IF NOT EXISTS papers (
    id TEXT PRIMARY KEY,
    doi TEXT,
    arxiv_id TEXT,
    title TEXT NOT NULL,
    abstract TEXT,
    venue TEXT,
    year INTEGER,
    citation_count INTEGER,
    citation_count_source TEXT,
    is_seed INTEGER NOT NULL DEFAULT 0,
    hop_distance INTEGER NOT NULL,
    discovered_via TEXT,
    expanded INTEGER NOT NULL DEFAULT 0,
    crawl_priority_score REAL,
    relevance_verdict TEXT,
    relevance_reasoning TEXT,
    added_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS edges (
    citing_id TEXT NOT NULL,
    cited_id TEXT NOT NULL,
    source TEXT NOT NULL,
    PRIMARY KEY (citing_id, cited_id)
);

CREATE TABLE IF NOT EXISTS families (
    name TEXT PRIMARY KEY,
    description TEXT,
    is_original INTEGER NOT NULL DEFAULT 0,
    created_from_paper_id TEXT,
    created_at TEXT NOT NULL
);
"""

# Papers created before the family/relevance-score columns existed need a
# migration, not just CREATE TABLE IF NOT EXISTS (which only affects brand-new
# tables). Idempotent: skipped if the column is already there.
_MIGRATIONS = [
    ("papers", "family", "TEXT"),
]


def _migrate(conn: sqlite3.Connection) -> None:
    for table, column, coltype in _MIGRATIONS:
        existing_cols = {row["name"] for row in conn.execute(f"PRAGMA table_info({table})")}
        if column not in existing_cols:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {coltype}")
    conn.commit()


# The 9 strategy families from docs/academic-research/phase1_revised_v2.md
# "Strategy Families" section — the pre-existing, human-authored vocabulary
# that classify_relevance.py's tagging should extend, not replace.
ORIGINAL_FAMILIES = {
    "Sniper bots": "First-N-block automated buys at token launch.",
    "Sandwich / MEV extraction": "Jito bundle / MEV-extraction strategies targeting memecoin pools.",
    "Copy-trading / wallet-following": "Bots that replicate wallets with a positive trading history.",
    "Rug-pull / fraud prediction": "Target identification using rug-probability or scam-detection features.",
    "Social-signal-only": "Pure social-graph / sentiment-driven entries, no wallet signal.",
    "Wallet-clustering alpha": "Signal derived from on-chain wallet cluster behavior.",
    "HFT / high-frequency momentum": "Short-horizon momentum strategies at sub-minute scale.",
    "Filter / gating strategies": "Feature-based gating or panels that select which tokens to enter.",
    "Hybrid strategies": "Signal source and execution logic drawn from different families.",
    "Background / survey": "Contextual or survey-level work, not itself a strategy evaluation.",
}


def seed_original_families(conn: sqlite3.Connection) -> None:
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    for name, description in ORIGINAL_FAMILIES.items():
        conn.execute(
            "INSERT OR IGNORE INTO families (name, description, is_original, created_from_paper_id, created_at) "
            "VALUES (?, ?, 1, NULL, ?)",
            (name, description, now),
        )
    conn.commit()


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    _migrate(conn)
    seed_original_families(conn)
    return conn


def upsert_paper(conn: sqlite3.Connection, paper: dict[str, Any]) -> None:
    """Inserts a new paper, or fills in fields on an existing one without
    clobbering already-set values (e.g. a re-discovered node keeps its
    existing relevance_verdict rather than losing it)."""
    existing = conn.execute("SELECT * FROM papers WHERE id = ?", (paper["id"],)).fetchone()
    if existing is None:
        conn.execute(
            """INSERT INTO papers
               (id, doi, arxiv_id, title, abstract, venue, year, citation_count,
                citation_count_source, is_seed, hop_distance, discovered_via,
                expanded, crawl_priority_score, relevance_verdict, relevance_reasoning, added_at)
               VALUES (:id, :doi, :arxiv_id, :title, :abstract, :venue, :year, :citation_count,
                       :citation_count_source, :is_seed, :hop_distance, :discovered_via,
                       :expanded, :crawl_priority_score, :relevance_verdict, :relevance_reasoning, :added_at)""",
            {
                "expanded": 0,
                "crawl_priority_score": None,
                "relevance_verdict": None,
                "relevance_reasoning": None,
                "added_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                **paper,
            },
        )
    else:
        for field in ("doi", "arxiv_id", "abstract", "venue", "citation_count", "citation_count_source"):
            if paper.get(field) and not existing[field]:
                conn.execute(f"UPDATE papers SET {field} = ? WHERE id = ?", (paper[field], paper["id"]))
    conn.commit()


def add_edge(conn: sqlite3.Connection, citing_id: str, cited_id: str, source: str) -> None:
    conn.execute(
        "INSERT OR IGNORE INTO edges (citing_id, cited_id, source) VALUES (?, ?, ?)",
        (citing_id, cited_id, source),
    )
    conn.commit()


def unexpanded_within_hops(conn: sqlite3.Connection, max_hops: int) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM papers WHERE expanded = 0 AND hop_distance < ? ORDER BY hop_distance ASC",
        (max_hops,),
    ).fetchall()


def mark_expanded(conn: sqlite3.Connection, paper_id: str) -> None:
    conn.execute("UPDATE papers SET expanded = 1 WHERE id = ?", (paper_id,))
    conn.commit()


def unclassified(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM papers WHERE relevance_verdict IS NULL").fetchall()


def set_verdict(conn: sqlite3.Connection, paper_id: str, verdict: str, reasoning: str) -> None:
    conn.execute(
        "UPDATE papers SET relevance_verdict = ?, relevance_reasoning = ? WHERE id = ?",
        (verdict, reasoning, paper_id),
    )
    conn.commit()


def total_papers(conn: sqlite3.Connection) -> int:
    return conn.execute("SELECT COUNT(*) FROM papers").fetchone()[0]


def all_family_names(conn: sqlite3.Connection) -> list[str]:
    return [r["name"] for r in conn.execute("SELECT name FROM families ORDER BY name")]


def _name_similarity(a: str, b: str) -> float:
    """max(whole-string ratio, word-containment) — plain character-level
    ratio alone misses short-vs-long rephrasings ("rug-pull detection" vs.
    "rug-pull / fraud prediction" scores 0.71, i.e. it's brittle right at
    the threshold that matters); word containment catches those (the
    shorter phrase's words mostly appear in the longer one) while still
    reading as near-zero for genuinely unrelated names."""
    import difflib
    import re

    a, b = a.lower(), b.lower()
    char_ratio = difflib.SequenceMatcher(None, a, b).ratio()
    words_a, words_b = set(re.findall(r"[a-z]+", a)), set(re.findall(r"[a-z]+", b))
    containment = len(words_a & words_b) / min(len(words_a), len(words_b)) if words_a and words_b else 0.0
    return max(char_ratio, containment)


def resolve_family(conn: sqlite3.Connection, proposed_name: str, paper_id: str, dedup_threshold: float = 0.6) -> tuple[str, bool]:
    """Maps a model-proposed family name onto the vocabulary: an exact
    (case-insensitive) match reuses it as-is; otherwise a fuzzy match against
    every existing name snaps onto the closest one above `dedup_threshold`
    (catches "Rug-pull detection" landing on the existing "Rug-pull / fraud
    prediction" instead of forking a near-duplicate); only a proposal that
    resembles nothing gets created as new. Returns (final_name, was_created).
    """
    existing = all_family_names(conn)
    for name in existing:
        if name.lower() == proposed_name.strip().lower():
            return name, False

    if existing:
        best = max(existing, key=lambda n: _name_similarity(n, proposed_name))
        if _name_similarity(best, proposed_name) >= dedup_threshold:
            return best, False

    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    conn.execute(
        "INSERT INTO families (name, description, is_original, created_from_paper_id, created_at) "
        "VALUES (?, NULL, 0, ?, ?)",
        (proposed_name.strip(), paper_id, now),
    )
    conn.commit()
    return proposed_name.strip(), True


def set_family(conn: sqlite3.Connection, paper_id: str, family_name: str) -> None:
    conn.execute("UPDATE papers SET family = ? WHERE id = ?", (family_name, paper_id))
    conn.commit()
