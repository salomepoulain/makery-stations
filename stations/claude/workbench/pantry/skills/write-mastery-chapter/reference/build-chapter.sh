#!/bin/sh
# usage: bash <skill>/reference/build-chapter.sh ml1-chap1-mvcalc-chapter      (run it inside the chapter's folder)
# builds NAME-answers.pdf (with solutions) and NAME-questions.pdf (without) from the single NAME.tex
# The chapter loads mastery-breaks.sty. The first run copies it and this script next to the chapter, so the folder builds by itself afterwards.
# If the script was copied without the .sty, set MASTERY_SKILL to the skill's reference folder.
here="$(cd "$(dirname "$0")" && pwd)"
sk="${MASTERY_SKILL:-$here}"
if [ -f "$sk/mastery-breaks.sty" ] && [ "$(pwd)" != "$sk" ]; then
  cp -f "$sk/mastery-breaks.sty" ./mastery-breaks.sty
  [ "$here" != "$(pwd)" ] && cp -f "$0" ./build-chapter.sh
fi
export TEXINPUTS=".:$sk:"
n="$1"
for i in 1 2 3; do pdflatex -interaction=nonstopmode -jobname="$n-answers" "$n.tex" >/dev/null 2>&1; done
for i in 1 2 3; do pdflatex -interaction=nonstopmode -jobname="$n-questions" "\def\hidesolutions{1}\input{$n.tex}" >/dev/null 2>&1; done
for v in answers questions; do echo "$n-$v: $(grep -a -c '^!' "$n-$v.log") errors, $(pdfinfo "$n-$v.pdf" | grep Pages)"; done
