---
name: write-mastery-website
description: Turn a mastery chapter into a clickable website (one HTML page published as an artifact) that looks like the LaTeX PDF. Solutions sit behind a blue bar, hints open one at a time, every solution line has a "why" toggle, MC options can be checked, and each exercise has a finished circle and a flag. Use when the user asks for the website, HTML or clickable version of a chapter, or for /write-mastery-website. The chapter content itself is written with write-mastery-chapter.
---

# Write mastery website

A mastery chapter has one source: its `.tex`. This skill does not write content of its own. It adds
a few authoring rules so the `.tex` converts cleanly, then builds the HTML and publishes it.

## 1. Write or update the chapter with write-mastery-chapter

Follow `write-mastery-chapter` (its SKILL.md and reference files) for everything that is content:
plan gate, Theory blocks, exercises, solutions, Legend, Contents, Summary, Diagnostic check.
If the course has its own spec in `lessons/` (for ML1: `lessons/ml1-session-mode-spec.md`),
that spec wins over the chapter skill's defaults.

## 2. Authoring rules the converter relies on

The converter reads the chapter's own macros. Write the `.tex` this way:

- **Solutions, one rule per line.** One log rule, one algebra move or one arithmetic operation per
  display. Before each display, one short sentence ending in `:` that says what the move is. That
  sentence becomes the hidden "why" of the line. Text that does not end in `:` stays visible.
  Never chain relations in one display (`a=b=c`), never write "Solve" for several moves.
- **Grading marks stay visible.** A sentence with `\textbf{+0.5} for ...:` is never hidden.
- **Hints** as `\hint{(1) ... (2) ... (3) ...}`. Each numbered piece becomes one click of the grey
  hint bar. A hint without numbers is one piece.
- **Multiple choice** with `\opt{a} ... \opt{b} ...`, and the solution must start with the answer
  letters, e.g. `\sol{(a) and (c). ...}`, `\sol{Answer (c), ...}` or `\sol{None ...}`. That first
  sentence is how the "Check my answer" bar knows the key. Without it the item gets a normal
  solution bar.
- **Figures** go in `\begin{center}...\end{center}` with a `tikzpicture`, or with a figure macro
  defined in the body by `\def\name#1{...}`. V exercises use `\vfilltrue` inside the `\sol` for the
  filled version. Figures are compiled with pdflatex and embedded as SVG.
- **Questions the user asks** about an exercise (in the terminal, or as a comment on the artifact)
  are answered with `\qa{question}{answer}` placed right after that exercise's `\sol`. Add once to
  the preamble:
  ```latex
  \newcommand{\qa}[2]{\par\smallskip\noindent\begin{tcolorbox}[enhanced, sharp corners, colback=teal!6,
    colframe=teal!6, boxrule=0pt, left=8pt, right=8pt, top=3pt, bottom=4pt]%
    \textbf{\color{teal!70!black}Question.} \textit{#1}\par\smallskip #2\end{tcolorbox}}
  ```
  In the HTML the box opens and closes on a click, and "remove" hides it in that browser.
- Supported structure: `\chaptertitle`, `priorsection`, `\parasection`, `\frontsection{Summary}`,
  `\frontsection{Diagnostic check}`, `theorybox`, `priorbox`, `theorycont`, `recipebox`,
  `workedbox` (`\workedheading`, `\wpart`, `\workedanswer`), exercise lists with
  `\extag`/`\extags`/`\priornum`/`\diagnum`/`\diagnums`, parts with `\srcref`, `\extitle`,
  `\scenario`, `\newterm`, `\review`, `\rvsummary`, `summarybox`, `\sumhead`, `\priorgroup`,
  `\priorfrom`, `\secref`, `\thyref`, `\pthyref`, `itemize`, numbered `enumerate[label=...]`.
  Anything else prints as raw text; the build lists such leftovers under "unhandled macros".

## 3. Build

1. Build the PDFs first (`bash ./build-chapter.sh <name>` in the chapter folder). The Contents come
   from `<name>-answers.aux`.
2. Build the page:
   ```bash
   bash .claude/skills/write-mastery-website/reference/build-website.sh lessons/<name> [out.html]
   ```
   Default output: `lessons/<name>/<name>-website.html`. The script also runs a headless browser
   check: it must report `errors:none`, width equal to the window width, and `math-errors:0`.
3. "unhandled macros" from the converter may only list names that occur in CSS comments
   (`\sol`, `\hint`, `\opt`, `\secbandn`). Any other name is a macro to add to the converter or
   to rewrite in the `.tex`.
4. Look at the result once: render one Theory box, one exercise with its solution open, and the
   Summary (a headless screenshot with the other sheets hidden by CSS works well).

## 4. Publish

Publish the built file with the Artifact tool (first publish: `icon: "book"`). For an update keep
the same URL: publish again with `url` set to the chapter's artifact. Write the URL in the course
spec so later sessions update it instead of making a new one. Finished marks and flags live in the
viewer's browser storage under a key made from the chapter name, so they survive updates to the
same URL but not a new URL.

## Look and feel: copy the PDF, do not redesign

The user wants the page to look like the LaTeX output. Same font (Latin Modern, embedded by
`inject_fonts.py` from TeX Live), colours computed from the preamble's xcolor values (the chapter
colour comes from `\definecolor{chcolorN}`), same boxes, pills, source tags, bands and Legend.
Only the interaction is new. Do not add design ideas of your own; propose them first.

Interaction, as approved:
- closed solution = a blue bar (blue!12) across the text width; it stays above the open box and
  closes it again; MC items use the same bar for "Check my answer" (ticks and crosses per option);
- hints = a grey bar with one segment per hint; each click adds the next hint above it;
- every solution line has a small "why" link; "Show all reasons" opens them all;
- right margin: an empty circle (finished, turns green with a tick) nearest the text, then a flag
  shaped like the source tag mirrored (outline, orange when set); the Contents underline finished
  cells in green, and the top line lists finished count and flagged exercises as links;
- a dome at the bottom of the screen goes back to the Contents;
- body text, hints and reasons all at the same 11pt size.

## Files

- `reference/website-template.html`: page head (CSS, MathJax), Legend sheet and scripts.
  Placeholders: `@@TITLE@@`, `@@N@@`, `@@KEY@@`, markers `<!--FRONT-->` and `<!--CONTENT-->`.
- `reference/chapter.css`: the boxes of the chapter body.
- `reference/tex2html.py`: the converter. `python3 tex2html.py <chapter-folder> <raw.html>`.
- `reference/inject_fonts.py`: embeds Latin Modern. `python3 inject_fonts.py <raw.html> <out.html>`.
- `reference/build-website.sh`: both steps plus the smoke test.

## Known limits

- MathJax loads from a CDN, so the page needs internet on first load.
- Finished marks and flags are per browser.
- The HTML has no page numbers; the Legend says so (dome instead).
