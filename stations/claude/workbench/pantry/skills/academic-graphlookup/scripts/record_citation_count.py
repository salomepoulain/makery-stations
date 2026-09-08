#!/usr/bin/env python3
"""record_citation_count: manually patch in a citation count for one paper,
sourced from Google Scholar via the browse skill.

This exists because Google Scholar has no API and can't be queried from a
plain script the way OpenAlex/Semantic Scholar can — checking it is a
human-in-the-loop (browse skill) step, not something crawl.py does on its
own. Use this only as a last resort, when a paper's citation_count is NULL
after crawl.py: query Google Scholar by title via /browse, read off the
"Cited by N" count, then record it here. If Scholar looks blocked or
CAPTCHA'd, don't retry-hammer it — leave the count unknown.

Usage:
    python scripts/record_citation_count.py --id <paper_id> --count <n>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import _db  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--id", required=True, help="Canonical paper id (openalex_id / doi:.. / arxiv:.. / title:..)")
    parser.add_argument("--count", required=True, type=int)
    parser.add_argument("--config", type=Path, default=Path(__file__).parent.parent / "config.json")
    args = parser.parse_args()

    config = json.loads(args.config.read_text())
    conn = _db.connect(Path.cwd() / config["db_path"])
    row = conn.execute("SELECT id FROM papers WHERE id = ?", (args.id,)).fetchone()
    if row is None:
        print(f"error: no paper with id {args.id!r} in the db", file=sys.stderr)
        return 2

    conn.execute(
        "UPDATE papers SET citation_count = ?, citation_count_source = 'google_scholar' WHERE id = ?",
        (args.count, args.id),
    )
    conn.commit()
    print(f"Recorded {args.count} citations (source: google_scholar) for {args.id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
