#!/usr/bin/env python3
"""Sci-Hub PDF downloader — skill script for scihub-dl

Usage:
    python scihub_dl.py <DOI_or_URL> [--outdir DIR]

Features:
    - Reads default output directory from config.json next to this script's parent
    - Dynamic domain discovery via sci-hub.pub
    - Fallback to known mirrors (sci-hub.ru, sci-hub.se, sci-hub.st)
    - Multiple PDF link extraction strategies
    - Exponential-backoff retry with random UA rotation
    - Optional debug HTML dump on failure
"""
import argparse
import json
import logging
import os
import random
import re
import sys
import time
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger("scihub-dl")

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

# Skill root dir: scripts/ -> skill root
SKILL_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = SKILL_ROOT / "config.json"

CONFIG_DEFAULTS = {
    "outdir": "",
    "last_used_outdir": "",
}


def load_config() -> dict:
    """Load config.json; return defaults if file is missing or invalid."""
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            # Merge with defaults so new keys appear
            merged = {**CONFIG_DEFAULTS, **cfg}
            return merged
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Failed to read config.json: %s — using defaults", exc)
    return dict(CONFIG_DEFAULTS)


def save_config(cfg: dict) -> None:
    """Write config.json atomically."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = CONFIG_PATH.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
        f.write("\n")
    tmp.replace(CONFIG_PATH)


def resolve_outdir(cli_outdir: Optional[str]) -> str:
    """Resolve output directory: CLI arg > config outdir > config last_used > cwd.

    If none of these yield a valid path, print a setup hint and exit.
    """
    cfg = load_config()

    # 1. Explicit CLI argument wins
    if cli_outdir:
        resolved = os.path.expanduser(cli_outdir)
        cfg["last_used_outdir"] = resolved
        save_config(cfg)
        return resolved

    # 2. Config outdir
    if cfg.get("outdir"):
        resolved = os.path.expanduser(cfg["outdir"])
        os.makedirs(resolved, exist_ok=True)
        cfg["last_used_outdir"] = resolved
        save_config(cfg)
        return resolved

    # 3. Last used outdir
    if cfg.get("last_used_outdir"):
        resolved = os.path.expanduser(cfg["last_used_outdir"])
        if os.path.isdir(resolved):
            return resolved

    # 4. No config — ask user to set up
    print(
        "ERROR: No output directory configured.\n"
        f"\n"
        f"Edit the config file to set your default download path:\n"
        f"  {CONFIG_PATH}\n"
        f"\n"
        f'Example config.json:\n'
        f'  {{\n'
        f'    "outdir": "~/Downloads/papers"\n'
        f'  }}\n'
        f"\n"
        f"Or specify a directory on the command line:\n"
        f"  python scihub_dl.py <DOI> --outdir ~/Downloads/papers\n"
    )
    sys.exit(2)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FALLBACK_DOMAINS = [
    "https://sci-hub.ru",
    "https://sci-hub.se",
    "https://sci-hub.st",
]

DISCOVERY_URL = "https://www.sci-hub.pub/"

_UA_LIST_URL = (
    "https://gist.githubusercontent.com/ozturkoktay/"
    "f1073b3038cab632c16231ef73353d7c/raw/"
    "cf847b76a142955b1410c8bcef3aabe221a63db1/user-agents.txt"
)

DEFAULT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

MAX_RETRIES = 5
CONNECT_TIMEOUT = 30
READ_TIMEOUT = 60


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _fetch_ua_pool() -> list[str]:
    """Fetch a list of user-agents; fall back to a single default."""
    try:
        r = requests.get(_UA_LIST_URL, timeout=10)
        if r.status_code == 200:
            return [u.strip() for u in r.text.splitlines() if u.strip()]
    except Exception:
        pass
    return [DEFAULT_UA]


def _random_ua(pool: list[str]) -> str:
    return random.choice(pool) if pool else DEFAULT_UA


def _normalise_doi(raw: str) -> str:
    """Strip doi: prefix and https://doi.org/ prefix."""
    return re.sub(r"^(doi:|https?://doi\.org/)", "", raw).strip()


def _discover_domains() -> list[str]:
    """Discover currently available Sci-Hub domains via sci-hub.pub."""
    try:
        r = requests.get(DISCOVERY_URL, timeout=15, headers={"User-Agent": DEFAULT_UA})
        soup = BeautifulSoup(r.content, "html.parser")
        links = [
            a.get("href")
            for a in soup.find_all("a", href=lambda h: h and "sci-hub." in h)
        ]
        if links:
            return links
    except Exception as exc:
        logger.debug("Domain discovery failed: %s", exc)
    return []


def _abs_url(href: str, base: str) -> str:
    """Turn a possibly-relative href into an absolute URL."""
    if href.startswith("//"):
        return "https:" + href
    if href.startswith("/"):
        parsed = re.match(r"(https?://[^/]+)", base)
        root = parsed.group(1) if parsed else base.rstrip("/")
        return root + href
    return href


# ---------------------------------------------------------------------------
# Core downloader
# ---------------------------------------------------------------------------


class SciHubDownloader:
    def __init__(self, ua_pool: Optional[list[str]] = None):
        self.ua_pool = ua_pool or _fetch_ua_pool()
        self.session = requests.Session()
        self.domains: list[str] = []

    def _init_domains(self):
        """Populate domain list: discovered first, then fallbacks."""
        discovered = _discover_domains()
        self.domains = discovered + FALLBACK_DOMAINS
        logger.debug("Domains: %s", self.domains)

    def _request(self, url: str, stream: bool = False) -> requests.Response:
        """GET with retries and UA rotation."""
        for attempt in range(MAX_RETRIES + 1):
            headers = {"User-Agent": _random_ua(self.ua_pool)}
            try:
                r = self.session.get(
                    url,
                    headers=headers,
                    timeout=READ_TIMEOUT if stream else CONNECT_TIMEOUT,
                    stream=stream,
                )
                return r
            except requests.exceptions.RequestException as exc:
                logger.debug("Attempt %d failed: %s", attempt + 1, exc)
                if attempt < MAX_RETRIES:
                    time.sleep(1.0 * 2 ** attempt)
        raise RuntimeError(f"All {MAX_RETRIES + 1} retries failed for {url}")

    def _extract_pdf_url(self, soup: BeautifulSoup, page_url: str) -> Optional[str]:
        """Try multiple extraction strategies to find the PDF link."""
        # Strategy 1: <meta name="citation_pdf_url">
        meta = soup.find("meta", {"name": "citation_pdf_url"})
        if meta and meta.get("content"):
            return _abs_url(meta["content"], page_url)

        # Strategy 2: <iframe id="pdf">
        iframe = soup.find("iframe", {"id": "pdf"})
        if iframe and iframe.get("src"):
            return _abs_url(iframe["src"], page_url)

        # Strategy 3: <embed src="...pdf">
        embed = soup.find("embed", src=lambda s: s and ".pdf" in s)
        if embed and embed.get("src"):
            return _abs_url(embed["src"], page_url)

        # Strategy 4: <a href="/storage/...pdf">
        link = soup.find("a", href=lambda h: h and "/storage/" in h and h.endswith(".pdf"))
        if link and link.get("href"):
            return _abs_url(link["href"], page_url)

        return None

    def download(self, doi_or_url: str, outdir: str = ".") -> str:
        """Download a paper PDF. Returns the local file path."""
        self._init_domains()

        doi = _normalise_doi(doi_or_url)
        errors: list[str] = []

        for domain in self.domains:
            url = f"{domain}/{doi}" if not doi_or_url.startswith("http") else doi_or_url
            try:
                r = self._request(url)
                if any(kw in r.text.lower() for kw in ("not found", "sorry")):
                    errors.append(f"{domain}: paper not found")
                    continue

                soup = BeautifulSoup(r.content, "html.parser")
                pdf_url = self._extract_pdf_url(soup, r.url)

                if not pdf_url:
                    debug_path = os.path.join(outdir, "debug.html")
                    os.makedirs(outdir, exist_ok=True)
                    with open(debug_path, "w", encoding="utf-8") as f:
                        f.write(r.text)
                    errors.append(f"{domain}: no PDF link found (debug.html saved)")
                    continue

                # Download PDF
                r2 = self._request(pdf_url, stream=True)
                content_type = r2.headers.get("content-type", "")
                if "pdf" not in content_type and "octet-stream" not in content_type:
                    logger.warning("Response type: %s — may not be a PDF", content_type)

                filename = re.sub(r"[^\w.]", "_", doi.split("/")[-1]) + ".pdf"
                path = os.path.join(outdir, filename)
                os.makedirs(outdir, exist_ok=True)

                with open(path, "wb") as f:
                    for chunk in r2.iter_content(chunk_size=1024):
                        f.write(chunk)

                size = os.path.getsize(path)
                print(f"OK: {path} ({size} bytes)")
                return path

            except Exception as exc:
                errors.append(f"{domain}: {exc}")
                continue

        print("ERROR: All Sci-Hub domains failed:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Sci-Hub PDF downloader (scihub-dl skill)"
    )
    parser.add_argument("doi_or_url", help="DOI or Sci-Hub URL to download")
    parser.add_argument(
        "--outdir", "-o",
        default=None,
        help="Output directory (overrides config.json outdir)",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    level = logging.DEBUG if args.debug else logging.WARNING
    logging.basicConfig(level=level, format="%(name)s: %(message)s")

    outdir = resolve_outdir(args.outdir)
    dl = SciHubDownloader()
    dl.download(args.doi_or_url, outdir)


if __name__ == "__main__":
    main()
