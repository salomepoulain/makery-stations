#!/usr/bin/env bash
# Build the clickable HTML version of a mastery chapter.
# Usage: bash build-website.sh <chapter-folder> [out.html]
# Needs the chapter's PDFs built first (the Contents come from <name>-answers.aux).
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
FOLDER="$(cd "$1" && pwd)"
NAME="$(basename "$FOLDER")"
OUT="${2:-$FOLDER/$NAME-website.html}"
RAW="$(mktemp -t mastery-website).html"

python3 "$HERE/tex2html.py" "$FOLDER" "$RAW"
python3 "$HERE/inject_fonts.py" "$RAW" "$OUT"
rm -f "$RAW"
echo "written: $OUT"

# Optional smoke test in a headless Chromium browser: script errors and sideways scroll at phone width.
for B in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser" "$(command -v chromium || true)"; do
  [ -n "$B" ] && [ -x "$B" ] || continue
  T="$(mktemp -t mastery-check).html"
  { printf '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body><script>window.onerror=function(m,u,l){window.__e=(window.__e||"")+m+"@"+l+";"}</script>'
    cat "$OUT"
    printf '<script>setTimeout(function(){document.title="CHECK errors:"+(window.__e||"none")+" width:"+document.documentElement.scrollWidth+"/"+innerWidth+" math-errors:"+document.querySelectorAll("[data-mjx-error]").length},15000)</script></body></html>'
  } > "$T"
  "$B" --headless=new --disable-gpu --virtual-time-budget=40000 --window-size=400,1000 --dump-dom "file://$T" 2>/dev/null | grep -o '<title>CHECK[^<]*' | sed 's/<title>//' || echo "smoke test: no result"
  rm -f "$T"
  break
done
