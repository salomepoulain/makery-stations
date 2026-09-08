#!/usr/bin/env python3
"""fetch_oa_pdfs: download legally open-access PDFs for a literature_corpus
passport, into a `raw/` folder alongside it.

Reads `passport.yaml` (as produced by `ars_pipeline.py` or any other
adapter in this directory) and looks up a free-to-read copy for each
entry via three open-access sources, in order:

  1. arXiv `https://arxiv.org/pdf/{arxiv_id}` when the entry carries an
     `arxiv_id` (arXiv preprints are always open access — no lookup
     needed, the URL is derived directly)
  2. OpenAlex `best_oa_location.pdf_url` when the entry carries a `doi`
     (no API key required)
  3. Unpaywall `best_oa_location.url_for_pdf` as a fallback for the same
     `doi` (requires a contact email, per Unpaywall's usage terms)

This script only ever fetches copies that a publisher or repository has
made open access. It does not use Sci-Hub or any other unauthorized
mirror, and it will not try to route around a paywall. Entries with no
open-access copy are recorded as such in the manifest, not silently
skipped.

Usage:
    python scripts/adapters/fetch_oa_pdfs.py \\
        --passport docs/academic-research/corpus/passport.yaml \\
        --raw-dir  docs/academic-research/corpus/raw/ \\
        --email    you@example.com

`--email` is required by Unpaywall's API terms (it is sent as the
`email` query param, not stored anywhere). OpenAlex lookups work
without it but are politer (higher rate limit) if `--email` is passed.

Output:
    - one `<citation_key>.pdf` per open-access hit, written to `--raw-dir`
    - `raw_manifest.yaml` in `--raw-dir`, one entry per passport source,
      recording status (`downloaded` / `already_present` / `no_oa_copy`
      / `no_doi` / `error`), the source used, and the URL tried.

Exit codes:
    0 - ran to completion (individual misses are not a failure)
    2 - invocation error (passport missing / unreadable)
"""
from __future__ import annotations

import argparse
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

import yaml

_OPENALEX_BASE = "https://api.openalex.org/works/doi:"
_UNPAYWALL_BASE = "https://api.unpaywall.org/v2/"
_ARXIV_PDF_BASE = "https://arxiv.org/pdf/"
_TIMEOUT = 30
_MIN_INTERVAL = 1.0  # be polite to both free APIs


def _get_json(url: str) -> dict[str, Any] | None:
    req = urllib.request.Request(url, headers={"User-Agent": "ARS-fetch-oa-pdfs/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:  # nosec B310
            import json

            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
        return None


def _openalex_pdf_url(doi: str) -> str | None:
    quoted = urllib.parse.quote(doi, safe="")
    data = _get_json(f"{_OPENALEX_BASE}{quoted}?select=best_oa_location")
    if not data:
        return None
    loc = data.get("best_oa_location") or {}
    return loc.get("pdf_url")


def _unpaywall_pdf_url(doi: str, email: str) -> str | None:
    quoted = urllib.parse.quote(doi, safe="")
    email_q = urllib.parse.quote(email, safe="")
    data = _get_json(f"{_UNPAYWALL_BASE}{quoted}?email={email_q}")
    if not data:
        return None
    loc = data.get("best_oa_location") or {}
    return loc.get("url_for_pdf")


def _download_pdf(url: str, dest: Path) -> str | None:
    """Downloads `url` to `dest`. Returns an error string, or None on success."""
    req = urllib.request.Request(url, headers={"User-Agent": "ARS-fetch-oa-pdfs/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:  # nosec B310
            content_type = resp.headers.get("Content-Type", "")
            body = resp.read()
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        return f"download failed: {e}"
    if "pdf" not in content_type.lower() and not body[:5] == b"%PDF-":
        return f"response was not a PDF (Content-Type: {content_type or 'unknown'})"
    dest.write_bytes(body)
    return None


def fetch_all(passport_path: Path, raw_dir: Path, email: str | None) -> list[dict[str, Any]]:
    passport = yaml.safe_load(passport_path.read_text(encoding="utf-8")) or {}
    entries = passport.get("literature_corpus") or []
    raw_dir.mkdir(parents=True, exist_ok=True)

    manifest: list[dict[str, Any]] = []
    last_request = 0.0

    for entry in entries:
        citation_key = entry.get("citation_key", "unknown")
        doi = entry.get("doi")
        arxiv_id = entry.get("arxiv_id")
        dest = raw_dir / f"{citation_key}.pdf"

        if dest.exists():
            manifest.append({"citation_key": citation_key, "status": "already_present", "path": str(dest)})
            continue

        if not doi and not arxiv_id:
            manifest.append({"citation_key": citation_key, "status": "no_doi"})
            continue

        pdf_url: str | None = None
        source = ""

        if arxiv_id:
            pdf_url = f"{_ARXIV_PDF_BASE}{arxiv_id}"
            source = "arxiv"

        if not pdf_url and doi:
            elapsed = time.monotonic() - last_request
            if elapsed < _MIN_INTERVAL:
                time.sleep(_MIN_INTERVAL - elapsed)
            last_request = time.monotonic()

            pdf_url = _openalex_pdf_url(doi)
            source = "openalex"
            if not pdf_url and email:
                pdf_url = _unpaywall_pdf_url(doi, email)
                source = "unpaywall"

        if not pdf_url:
            manifest.append({"citation_key": citation_key, "status": "no_oa_copy", "doi": doi})
            continue

        error = _download_pdf(pdf_url, dest)
        if error:
            manifest.append({"citation_key": citation_key, "status": "error", "doi": doi, "url": pdf_url, "detail": error})
            continue

        manifest.append({
            "citation_key": citation_key,
            "status": "downloaded",
            "source": source,
            "url": pdf_url,
            "path": str(dest),
        })

    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--passport", required=True, type=Path)
    parser.add_argument("--raw-dir", required=True, type=Path)
    parser.add_argument("--email", default=None, help="Contact email for Unpaywall fallback lookups (recommended).")
    args = parser.parse_args()

    if not args.passport.exists():
        print(f"error: passport not found: {args.passport}", file=sys.stderr)
        return 2

    manifest = fetch_all(args.passport, args.raw_dir, args.email)

    manifest_path = args.raw_dir / "raw_manifest.yaml"
    manifest_path.write_text(yaml.safe_dump({"raw_pdfs": manifest}, sort_keys=False), encoding="utf-8")

    downloaded = sum(1 for m in manifest if m["status"] == "downloaded")
    present = sum(1 for m in manifest if m["status"] == "already_present")
    missed = len(manifest) - downloaded - present
    print(f"OK: {downloaded} downloaded, {present} already present, {missed} without an open-access copy")
    print(f"manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
