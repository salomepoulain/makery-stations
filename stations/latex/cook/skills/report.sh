#!/usr/bin/env bash
# shellcheck disable=SC2034
# Compile the project report: report/.../main.tex → main.pdf
# Usage: bake call s=latex d=report

source "$(dirname "${BASH_SOURCE[0]}")/../personality.sh"

REPOSITORY="$(git rev-parse --show-toplevel 2>/dev/null)"
REPORT_DIR="$REPOSITORY/report/Machine_Learning_For_The_Quantified_Self___Group_55"

STARTER "Compiling report"

SAY "Source: $REPORT_DIR/main.tex"

cd "$REPORT_DIR" || { SAY "ERROR: report directory not found"; exit 1; }

if command -v latexmk &>/dev/null; then
    SAY "Running latexmk..."
    latexmk -pdf -interaction=nonstopmode main.tex
else
    SAY "latexmk not found, falling back to pdflatex + bibtex..."
    pdflatex -interaction=nonstopmode main.tex
    bibtex main
    pdflatex -interaction=nonstopmode main.tex
    pdflatex -interaction=nonstopmode main.tex
fi

if [[ -f main.pdf ]]; then
    SAY "Done! Output: $REPORT_DIR/main.pdf"
    SAY "Cleaning up intermediary files..."
    if command -v latexmk &>/dev/null; then
        latexmk -c main.tex &>/dev/null
    else
        rm -f main.aux main.bbl main.blg main.log main.out main.toc missfont.log
    fi
else
    SAY "ERROR: main.pdf not produced. Check main.log for details"
    exit 1
fi

FINISHED
