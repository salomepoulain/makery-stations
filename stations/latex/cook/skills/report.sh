#!/usr/bin/env bash
# Compile the project report: report/**/main.tex -> main.pdf
# Usage: bake latex report
#        REPORT_DIR=report/<folder> bake latex report   (when there's more than one)

source "$(dirname "${BASH_SOURCE[0]}")/../personality.sh"

# Station commands run from inside the station folder, so find the project first.
PROJECT_ROOT="$PWD"
while [[ "$PROJECT_ROOT" != "/" && ! -d "$PROJECT_ROOT/.makery" ]]; do
    PROJECT_ROOT=$(dirname "$PROJECT_ROOT")
done
cd "$PROJECT_ROOT" || exit 1

STARTER "Compiling report"

# Build the folder you named, or the only main.tex under report/.
if [ -z "${REPORT_DIR:-}" ]; then
    MAINS=$(find report -name main.tex -not -path "*/writing_guides/*" 2>/dev/null)
    case "$(printf '%s\n' "$MAINS" | grep -c .)" in
        0)
            SAY "ERROR: no main.tex under report/"
            exit 1
            ;;
        1)
            REPORT_DIR=$(dirname "$MAINS")
            ;;
        *)
            SAY "There's more than one main.tex under report/:"
            while IFS= read -r m; do SAY "  $(dirname "$m")"; done <<< "$MAINS"
            SAY "Pick one: REPORT_DIR=<folder> bake latex report"
            exit 1
            ;;
    esac
fi

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
