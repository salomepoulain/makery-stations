#!/usr/bin/env python3
"""classify_relevance: ask a free OpenRouter model, per unclassified paper in
citegraph.sqlite, (a) how relevant it is to the project's research question
and (b) which strategy family it belongs to.

Reuses the mechanism in
.makery/kitchen/stations/claude/cook/recipes/commit-yolo.sh: point the
Claude CLI at OpenRouter via a temporary settings.local.json
(ANTHROPIC_BASE_URL + ANTHROPIC_AUTH_TOKEN) and run `claude -p` headless.
Papers are classified in batches (`batch_size` in config.json, default 8),
not one call each: the research-question/scope/family-list boilerplate is
identical for every paper in a run, so paying for it once per batch instead
of once per paper cuts both the call count and the token cost roughly
`batch_size`-fold, which matters a lot against OpenRouter's free-tier rate
limits. Every paper in a batch is tagged with its own index in the prompt
and expected to come back the same way — if the model only gets through
part of a batch (truncation, one malformed block), whichever indices did
parse are still applied; nothing else is guessed at. Rotates across the
free models listed in config.json on a rate-limit or empty response, with
backoff. Every paper gets a verdict written back — this is the only place
a "not_relevant" judgment is made; crawl.py never excludes anything on its
own.

Relevance is a 5-point scale (highly_relevant / relevant / uncertain /
probably_not / not_relevant), not 3 — with fewer buckets, "uncertain" ends
up as the model's default whenever it's even slightly unsure. The prompt
also tells it explicitly to commit to a side unless the abstract gives it
genuinely nothing to go on.

Family is matched against the vocabulary already in the `families` table
(seeded from docs/academic-research/phase1_revised_v2.md's 9 strategy
families) via `_db.resolve_family`, which fuzzy-matches a new proposal
against existing names before accepting it as genuinely new — this stops
the vocabulary fragmenting into near-duplicates ("rug-pull detection" vs.
the existing "Rug-pull / fraud prediction") the way pure freeform tagging
would. New families are auto-accepted (this run doesn't block on human
review, matching candidates_for_review.md's existing "first pass, not
ground truth" precedent) but every one created this run is reported here
and belongs in `families.md` after the next `export_graph_data.py` run.

Requires OPENROUTER_API_KEY in the environment. Fails loudly if unset —
it does not silently skip classification.

Usage:
    python scripts/classify_relevance.py [--config PATH] [--limit N]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import _db  # noqa: E402

_VERDICTS = ["highly_relevant", "relevant", "uncertain", "probably_not", "not_relevant"]
# One block per paper: "PAPER <n>" followed by its VERDICT/FAMILY/REASON,
# up to (but not including) the next "PAPER" marker or end of string. The
# leading paper index is what makes partial-batch recovery possible — order
# in the reply doesn't have to match order in the prompt, and a skipped
# index just means that one paper stays unclassified for a future rerun.
_BLOCK_RE = re.compile(
    r"PAPER\s+(\d+)\s*\n"
    r"VERDICT:\s*(" + "|".join(_VERDICTS) + r")\s*\n"
    r"FAMILY:\s*(.+?)\s*\n"
    r"REASON:\s*(.+?)(?=\n\s*PAPER\s+\d+|\Z)",
    re.IGNORECASE | re.DOTALL,
)


def load_research_question(path: Path) -> str:
    """Pulls Research Question + Scope Boundaries, not just the RQ line —
    the scope section is what actually tells the model that, e.g., an
    Ethereum/BSC comparator paper is in-scope, not out. Feeding only the
    bare RQ (an earlier version of this script did) is what caused real
    seeds like Gerzon/Huynh to get misclassified as not_relevant in
    testing: the RQ alone reads as Solana-only, and only the scope section
    clarifies the comparator-chain carve-out."""
    text = path.read_text(encoding="utf-8")
    sections = []
    for heading in ("Research Question", "Scope Boundaries"):
        match = re.search(rf"### {heading}\s*\n+(.+?)(?=\n#{{2,3}} )", text, re.DOTALL)
        if match:
            sections.append(f"{heading}:\n{match.group(1).strip()}")
    return "\n\n".join(sections) if sections else text[:1500]


def write_openrouter_settings(claude_dir: Path, model: str, api_key: str) -> None:
    (claude_dir / ".claude").mkdir(parents=True, exist_ok=True)
    (claude_dir / ".claude" / "settings.local.json").write_text(json.dumps({
        "model": model,
        "env": {
            "ANTHROPIC_BASE_URL": "https://openrouter.ai/api/v1",
            "ANTHROPIC_AUTH_TOKEN": api_key,
        },
    }))


def ask_model(claude_dir: Path, prompt: str, timeout: int = 60) -> str | None:
    env = dict(os.environ)
    env["CLAUDE_DIR"] = str(claude_dir / ".claude")
    try:
        result = subprocess.run(
            ["claude", "-p", prompt],
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def classify_batch(
    claude_dir: Path, models: list[str], api_key: str, research_question: str,
    papers: list[sqlite3.Row], family_names: list[str], timeout: int,
) -> dict[int, tuple[str, str, str]]:
    """Classifies up to len(papers) candidates in one call. Returns a dict
    keyed by the 1-based index into `papers` (only for indices the reply
    actually contained a parseable block for) -> (verdict, family, reason)."""
    family_list = "\n".join(f"- {name}" for name in family_names)
    papers_block = "\n\n".join(
        f"PAPER {i}\nTitle: {p['title']}\nAbstract: {p['abstract'] or '(no abstract available)'}"
        for i, p in enumerate(papers, 1)
    )
    prompt = f"""You are screening {len(papers)} candidate papers for a literature review, in one pass.

Research question and scope:
{research_question}

Existing strategy-family tags already in use (reuse one of these per paper if
it fits, even loosely — do not invent a near-duplicate of one that already exists):
{family_list}

Candidates:
{papers_block}

For EACH paper above, decide:
Task 1 — relevance. Commit to a side unless the abstract genuinely gives you
nothing to judge from. "uncertain" should be rare, not a default.
Task 2 — family. Pick the closest existing tag. Only propose a new one if the
paper truly fits none of them.

Reply with one block per paper, in this EXACT format, nothing else, one block
right after another (same PAPER numbers as above):
PAPER <n>
VERDICT: highly_relevant | relevant | uncertain | probably_not | not_relevant
FAMILY: <an exact existing tag, or a short new one if genuinely none fit>
REASON: <one sentence covering both the verdict and the family choice>"""

    for model in models:
        write_openrouter_settings(claude_dir, model, api_key)
        output = ask_model(claude_dir, prompt, timeout=timeout)
        if output:
            results = {}
            for match in _BLOCK_RE.finditer(output):
                idx = int(match.group(1))
                if 1 <= idx <= len(papers):
                    results[idx] = (match.group(2).lower(), match.group(3).strip(), match.group(4).strip())
            if results:
                return results
        time.sleep(2)  # brief backoff before trying the next model / giving up

    return {}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--config", type=Path, default=Path(__file__).parent.parent / "config.json")
    parser.add_argument("--limit", type=int, default=None, help="Classify at most N papers this run.")
    parser.add_argument("--batch-size", type=int, default=None, help="Override config.json's batch_size for this run.")
    args = parser.parse_args()

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("error: OPENROUTER_API_KEY is not set. Relevance classification requires it — "
              "set it and rerun rather than skipping this step.", file=sys.stderr)
        return 2

    config = json.loads(args.config.read_text())
    batch_size = args.batch_size or config.get("batch_size", 8)
    repo_root = Path.cwd()
    db_path = repo_root / config["db_path"]
    research_question = load_research_question(repo_root / config["research_question_path"])

    conn = _db.connect(db_path)
    pending = _db.unclassified(conn)
    if args.limit:
        pending = pending[: args.limit]

    if not pending:
        print("Nothing to classify.")
        return 0

    batches = [pending[i:i + batch_size] for i in range(0, len(pending), batch_size)]
    new_families: list[str] = []
    classified_count = 0
    claude_dir = Path(tempfile.mkdtemp(prefix="graphlookup-openrouter-"))
    try:
        for b, batch in enumerate(batches, 1):
            print(f"[batch {b}/{len(batches)}] classifying {len(batch)} papers...")
            family_names = _db.all_family_names(conn)
            # +45s of headroom per extra paper beyond the first: a batch reply
            # is proportionally longer than a single-paper one.
            timeout = 60 + 45 * (len(batch) - 1)
            results = classify_batch(claude_dir, config["openrouter_models"], api_key, research_question, batch, family_names, timeout)

            for idx, row in enumerate(batch, 1):
                if idx not in results:
                    print(f"    [{idx}] {row['title'][:60]} -> no parseable block, left unclassified for a later rerun")
                    continue
                verdict, proposed_family, reason = results[idx]
                final_family, created = _db.resolve_family(conn, proposed_family, row["id"])
                _db.set_verdict(conn, row["id"], verdict, reason)
                _db.set_family(conn, row["id"], final_family)
                if created:
                    new_families.append(final_family)
                classified_count += 1
                print(f"    [{idx}] {row['title'][:60]} -> {verdict} | {final_family}{' (new)' if created else ''}")
    finally:
        shutil.rmtree(claude_dir, ignore_errors=True)

    print(f"Classified {classified_count}/{len(pending)} papers across {len(batches)} batches.")
    if new_families:
        print(f"New families created this run: {', '.join(new_families)}")
        print("Run export_graph_data.py to refresh families.md with these.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
