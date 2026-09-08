"""Tests for scripts/adapters/ars_pipeline.py.

The ars_pipeline adapter is the inverse of the user-owned-source
adapters (folder_scan, zotero, obsidian): it reads a Phase 2
deliverable (a human-written markdown bibliography) and emits the
same passport contract plus three derived files (CSL-JSON, BibTeX,
citation graph).

These tests are golden tests: they run the adapter against a small
synthetic fixture and compare the outputs to checked-in expected
files. The fixture exercises every branch of the parser:
  - §3 source-as-heading (Mancino, Gerzon, Wu, Luo)
  - §5.1 stage-1 exclusion (CryptoTrade, Multi-Agent)
  - §5.2 stage-1 gray literature (sandwiched.me)
  - §5.3 stage-2 gate failure (Huynh)
  - §5.4 comparator meta-note (Mancino ISCC, dropped)
  - §5.5 methodology-only (Arian)
  - §5.6 preprint/in-press (Coordinated Sniper Cohorts)
  - §1, §2, §9 metadata sections (ignored)
  - §4 restated-summary section (ignored)
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
ADAPTER = REPO_ROOT / "scripts/adapters/ars_pipeline.py"
FIXTURE_DIR = REPO_ROOT / "scripts/adapters/examples/ars_pipeline/input_fixture"
EXPECTED_PASSPORT = REPO_ROOT / "scripts/adapters/examples/ars_pipeline/expected_passport.yaml"
EXPECTED_REJECTION = REPO_ROOT / "scripts/adapters/examples/ars_pipeline/expected_rejection_log.yaml"
EXPECTED_CSL = REPO_ROOT / "scripts/adapters/examples/ars_pipeline/expected_bib.csl.json"
EXPECTED_BIB = REPO_ROOT / "scripts/adapters/examples/ars_pipeline/expected_bib.bib"
EXPECTED_GRAPH = REPO_ROOT / "scripts/adapters/examples/ars_pipeline/expected_bib.citegraph.json"


def _run(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["python3", str(ADAPTER)] + list(args),
        capture_output=True,
        text=True,
        cwd=cwd or REPO_ROOT,
    )


def test_adapter_exists():
    assert ADAPTER.exists()


def test_happy_path(tmp_path, load_yaml, clean_timestamps):
    """End-to-end run on the synthetic fixture produces a passport
    that matches the golden, with timestamps and machine-dependent
    values blanked."""
    passport_out = tmp_path / "passport.yaml"
    rejection_out = tmp_path / "rejection_log.yaml"
    csl_out = tmp_path / "bib.csl.json"
    bib_out = tmp_path / "bib.bib"
    graph_out = tmp_path / "bib.citegraph.json"

    r = _run(
        "--bibliography", str(FIXTURE_DIR / "phase2_bibliography.md"),
        "--verification", str(FIXTURE_DIR / "phase2_verification.md"),
        "--synthesis", str(FIXTURE_DIR / "phase3_synthesis.md"),
        "--output-dir", str(tmp_path),
    )
    assert r.returncode == 0, f"adapter failed: {r.stderr}"

    # 1. Passport golden test.
    got = load_yaml(passport_out)
    expected = load_yaml(EXPECTED_PASSPORT)
    assert clean_timestamps(got) == clean_timestamps(expected), (
        "passport output differs from golden"
    )

    # 2. Rejection log golden test.
    got_rej = load_yaml(rejection_out)
    expected_rej = load_yaml(EXPECTED_REJECTION)
    assert clean_timestamps(got_rej) == clean_timestamps(expected_rej), (
        "rejection log output differs from golden"
    )

    # 3. CSL-JSON output should be valid JSON, parseable, and have
    #    one entry per passport source.
    csl = json.loads(csl_out.read_text(encoding="utf-8"))
    assert isinstance(csl, list)
    assert len(csl) == len(got["literature_corpus"])

    # 4. BibTeX output should be parseable, have one entry per
    #    passport source, and round-trip the citekeys.
    bib_text = bib_out.read_text(encoding="utf-8")
    bib_keys = re.findall(r"@\w+\{([^,]+),", bib_text)
    passport_keys = {e["citation_key"] for e in got["literature_corpus"]}
    assert set(bib_keys) == passport_keys

    # 5. Citation graph should be valid JSON with edges, co-citations,
    #    and unresolved arrays.
    graph = json.loads(graph_out.read_text(encoding="utf-8"))
    assert graph["schema"] == "ars_citegraph/1"
    assert "edges" in graph
    assert "co_citations" in graph
    assert "unresolved" in graph
    assert graph["edges_static"] >= 1
    # No live edges (we didn't pass --with-live-citations).
    assert graph["edges_live"] == 0


def test_passport_validates_against_schema(load_yaml):
    """The passport produced from the fixture must validate against
    literature_corpus_entry.schema.json (no additional properties)."""
    passport = load_yaml(EXPECTED_PASSPORT)
    schema_path = (
        REPO_ROOT
        / "shared/contracts/passport/literature_corpus_entry.schema.json"
    )
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    try:
        import jsonschema
    except ImportError:
        pytest.skip("jsonschema not installed")
    for entry in passport["literature_corpus"]:
        jsonschema.validate(entry, schema)


def test_parser_skips_metadata_sections():
    """The bibliography parser must ignore §1, §2, §4, §6-9 — only
    §3 (source-as-heading) and §5.x bullets (source-as-bullet)
    produce SourceRecord objects. §1.1 'Databases queried' is a
    known example of a heading that must NOT be parsed as a source."""
    import sys
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    from scripts.adapters.ars_pipeline import _parse_bibliography
    md = (FIXTURE_DIR / "phase2_bibliography.md").read_text(encoding="utf-8")
    records = _parse_bibliography(md)
    # 4 §3 sources + 2 §5.1 + 1 §5.2 + 1 §5.3 + 1 §5.4 (kept here,
    # dropped downstream by main()'s skip_already_included check) +
    # 1 §5.5 + 1 §5.6 = 11.
    assert len(records) == 11
    sections = {r.section for r in records}
    # §1, §2, §4, §9 sub-headings must NOT appear.
    assert not any(s.startswith("1.") for s in sections)
    assert not any(s.startswith("2.") for s in sections)
    assert "4" not in sections
    assert not any(s.startswith("9.") for s in sections)
    # All four §3 sources must be present.
    assert {"3.1", "3.2", "3.3", "3.4"}.issubset(sections)
    # §5.1 has 2 bullets, §5.2 has 1, §5.3 has 1, §5.4 has 1
    # (classified skip_already_included), §5.5 has 1, §5.6 has 1.
    assert "5.4" in sections
    skip = [r for r in records if r.category == "skip_already_included"]
    assert len(skip) == 1


def test_missing_bibliography_file_fails_loud(tmp_path):
    r = _run(
        "--bibliography", str(tmp_path / "missing.md"),
        "--verification", str(FIXTURE_DIR / "phase2_verification.md"),
        "--output-dir", str(tmp_path),
    )
    assert r.returncode != 0


def test_missing_verification_file_fails_loud(tmp_path):
    r = _run(
        "--bibliography", str(FIXTURE_DIR / "phase2_bibliography.md"),
        "--verification", str(tmp_path / "missing.md"),
        "--output-dir", str(tmp_path),
    )
    assert r.returncode != 0
