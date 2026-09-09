#!/usr/bin/env python3
"""free_scout: run one scouting prompt on a free OpenRouter model instead of
spawning a real Sonnet subagent, to save Claude Pro usage-limit quota on
small, well-scoped, read-only tasks.

Reuses the mechanism in
.makery/kitchen/stations/claude/cook/skills/commit-yolo.sh and
academic-graphlookup/scripts/classify_relevance.py: point the Claude CLI at
OpenRouter via a temporary settings.local.json (model + ANTHROPIC_BASE_URL +
ANTHROPIC_AUTH_TOKEN) and run `claude -p` headless. Unlike graphlookup (which
needs no tools, just text completion), the temp settings here also grant a
fixed read-only permission baseline (config.json's permissions_allow), since
scouting means actually reading files — and a headless -p process has no TTY
to answer a permission prompt, so anything not pre-allowed just fails.

Rotates across config.json's openrouter_models on rate-limit or empty/
malformed response, with backoff — same pattern as classify_relevance.py.

Exit codes (the caller uses these to decide whether to fall back to a real
subagent):
  0 = success, scout's answer printed to stdout
  2 = OPENROUTER_API_KEY not set — fall back, don't retry
  3 = every model in rotation failed — fall back, don't retry

Usage:
    python scripts/free_scout.py "<self-contained prompt>"
    python scripts/free_scout.py < prompt.txt
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def write_openrouter_settings(claude_dir: Path, model: str, api_key: str, config: dict) -> None:
    (claude_dir / ".claude").mkdir(parents=True, exist_ok=True)
    (claude_dir / ".claude" / "settings.local.json").write_text(json.dumps({
        "model": model,
        "env": {
            "ANTHROPIC_BASE_URL": "https://openrouter.ai/api/v1",
            "ANTHROPIC_AUTH_TOKEN": api_key,
        },
        "permissions": {
            "allow": config["permissions_allow"],
            "deny": config["permissions_deny"],
        },
    }))


def ask_model(claude_dir: Path, prompt: str, timeout: int) -> str | None:
    env = dict(os.environ)
    env["CLAUDE_DIR"] = str(claude_dir / ".claude")
    try:
        result = subprocess.run(
            ["claude", "-p", prompt],
            cwd=Path.cwd(),
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None
    if result.returncode != 0:
        return None
    output = result.stdout.strip()
    return output or None


def run_scout(prompt: str, config: dict, api_key: str) -> str | None:
    claude_dir = Path(tempfile.mkdtemp(prefix="free-scout-openrouter-"))
    try:
        for model in config["openrouter_models"]:
            write_openrouter_settings(claude_dir, model, api_key, config)
            output = ask_model(claude_dir, prompt, timeout=config.get("timeout_seconds", 120))
            if output:
                return output
            time.sleep(2)  # brief backoff before trying the next model / giving up
        return None
    finally:
        shutil.rmtree(claude_dir, ignore_errors=True)


def main() -> int:
    if len(sys.argv) > 1:
        prompt = sys.argv[1]
    else:
        prompt = sys.stdin.read()

    if not prompt.strip():
        print("error: no prompt given (pass as an argument or on stdin)", file=sys.stderr)
        return 1

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("FALLBACK: OPENROUTER_API_KEY is not set.", file=sys.stderr)
        return 2

    config_path = Path(__file__).parent.parent / "config.json"
    config = json.loads(config_path.read_text())

    output = run_scout(prompt, config, api_key)
    if output is None:
        print("FALLBACK: every model in rotation failed or returned empty output.", file=sys.stderr)
        return 3

    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
