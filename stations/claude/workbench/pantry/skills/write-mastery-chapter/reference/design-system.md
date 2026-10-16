# Design system

The canonical preamble is `reference/preamble-visual.tex`. Copy that preamble, do not rewrite it. Where this file and
`latex-scaffolding.md` disagree, this file wins. Build with `reference/build-chapter.sh`.

## Page and exercise layout
- Left and right margins are equal (1.25in), top 1in, bottom 0.8in. The exercise text is flush with the text block.
- **The exercise tag is a pill that hangs in the left margin**, its right end 1em before the text edge, vertically
  centred on the first line, digits on the text baseline. It is one letter cell (type colour at 75%, white letter) and one number
  cell (type colour at 22%, dark number). No outline, no line between the cells. The pill is as long as its number needs
  (`\tagpill`). It is built from `enumitem`: level 1 lists have `leftmargin=0pt,labelsep=1em`, level 2 (the parts (a), (b), ...)
  have a fixed label box so wrapped lines continue under the first letter of the part.
- The bold title of a drill family (`\extitle{Rules of Sigma.}`) is plain bold black. The gap between the pill and the text is
  0.6em (the margin source tags and the paragraph number use the same 0.6em, so they line up).
- Colours: P yellow, O teal, T orange, D dark blue, V pink, E green, C red, R violet.
- **Source labels** are small, italic, without a triangle, in brown (RGB 140,90,45) at 26% fill and 95% text opacity, so they take a little of the tint of the page they stand on. A source is on the **whole exercise or on its parts, never on both** (the macros give a warning
  in the log if an exercise has both).
  - A part: `\srcref{HW1 2b}` at the start of the part. An arrow (notch on the left, point on the right, as high as the number pill) hangs in the left margin
    on the line of the part, and its point ends on the right edge of the badges. The text stands against the point.
  - A whole exercise: `\extags{HW1 2}{\Ebadge}` instead of `\extag{\Ebadge}`. A capsule with a notched left edge and a round right end goes around the badge,
    and the text stands against the pill. All capsules are at least as long as `Math4AI`, so the notches line up.
  - A Diagnostic item: `\diagnums{HW1 1a}` instead of `\diagnum`. The same arrow as a part, left of the number and pointing at it.
  - `\srcinline{...}` is the arrow inside running text (Legend). The Legend explains all of it with a sample arrow and a sample capsule.
- **Solutions are breakable** (`solbox`), so a solution may continue on the next page. A new page starts only at a new paragraph
  (`\parasection`), never to keep a solution whole.

## Headers, Contents, Legend
- **Chapter title**: a solid band across the whole page in the chapter colour, white text, a credit line (`\chaptercredit`,
  "Created with the write-mastery-chapter skill"). White space above (34pt) and below (56pt) the band, not extra padding inside it.
  Under the band: a short introduction that shows why the topic matters (2 to 3 sentences), a line of key terms, and a small
  note. Keep it short.
- **Section headers** (paragraphs, Legend, Contents, Summary, Diagnostic check): a pale band (chapter colour at 22%) from the left
  page edge to the text edge, rounded on the right. The paragraph number hangs in the margin, right-aligned like the pills, the
  title starts at the text edge (`\secbandn`).
- **Page 1 holds the title, the introduction and the Contents in full. The Legend starts on page 2**, so every chapter looks the
  same, and this is a hard requirement, not a best effort: check it after every build (see SKILL.md's "Compile and verify"). A
  longer chapter has a longer Contents (more paragraph rows), not a longer introduction, so when the two together don't fit,
  the introduction gives way first, in this order: (1) drop the small note under the key terms line, (2) cut the introduction to
  one sentence, (3) as a last resort, tighten the vertical space between the title band and the Contents band. Never shrink the
  Contents pills, their font, or their row spacing to make room; that is what makes the pills hard to click and read, and the
  Contents is the page a reader returns to constantly.
- **Contents** sits above the Legend. Entries are `\large\bfseries` and black, page number on the right, no leaders. Under each
  paragraph, every Theory block is one long pill made of cells: a solid chapter-colour cell with the Theory letter (white), then the
  orienting exercise, then one light cell (type colour at 35%) per exercise, each a hyperlink. A pill is one unbreakable box, rows
  are ragged right, and cell widths depend on the number of letters or digits, never on a measured width (a measured width flips
  at a threshold and cuts the rounded ends). Every numbered badge and every theorybox writes a line to the `.aux`; the
  Contents reads it back (`\exentry`, `\dcrowflat`). An O exercise stands before its Theory box in the text but is drawn after
  the Theory cell in the pill.
  Prior knowledge (letter cell, then P cells on their own numbering), the Summary (one snake pill of all Theory letters) and the Diagnostic
  check (pale numbered cells in the page-number style, one pill per paragraph group, no labels) are built in chapter 1; see
  `reference/contents-mock.tex` for the target look.
- **Legend**: short, on its own page, at most two pages. Intro line, the boxes shown in their real colours (Theory with Recipe,
  Worked example, Prior knowledge box, Review, Solution strip), the exercise types each with a letter cell and one pedagogical sentence
  (why the type exists, in the words of `pedagogy-cycle.md`), a "Short on time?" line, then "How to read the chapter" as one item per
  line: Contents (with a sample pill), Source tag, New term, Assumed knowledge, Colours (a row of the seven chapter colours with the
  current chapter outlined), and last the page tints as swatches. Never a single long sentence for the reading aids.
- **Title block spacing**: the white space above the band and below it are equal (64pt). The band keeps its compact padding.
  Under the band, the key terms come first, then a short paragraph on why the topic matters.

## Exercises
- Run per Theory block: T, D, V, E, C, R (an O before the block, if any). See `pedagogy-cycle.md`.
- The Worked example is a model problem of the same type as the E questions. The course's own questions go to E, in their own
  wording, with a source tag on the part.
- Write a variation map (comment) per Theory block before writing its run, and check every dimension has an exercise.

## Review and Summary
The Review closes a paragraph and the Summary at the end of the chapter repeats it. They have one source: `\review{id}{terms}{formulas}{recipes}` typesets
the Review box and stores the three parts, `\rvsummary{id}{heading}{sources}` puts the same parts in the Summary, and `\rvdata{id}{...}{...}{...}` stores
parts without a box (used for the Prior knowledge block, which has no Review). Write every part once.
- **A Review is never split over two pages.** It may stand under the last exercises of its paragraph when it fits there. If it does not fit, the whole Review starts on the next page (the box is not breakable). Keep a Review short enough for one page.
- **Terms**: a run of `\tm{key}{formula}`, separated by commas by the macro, ending in a full stop. `key` is the text of a `\newterm` in the Theory (the macro
  lower-cases it and drops spaces), so the term is a link in the chapter colour to the place where it was introduced. `\tm[display text]{key}{...}` shows other
  text. The formula or notation goes behind the term in grey brackets, and every term that has a formula or notation gets one (`Kronecker delta [d_ij = 1 if i = j, 0 otherwise]`).
  Each term is unbreakable, the run is left-aligned. Use `\tn{text}{formula}` for a term without a `\newterm` (no link). A `\tm` with a key that has no `\newterm`
  gives a warning in the log.
- **Formulas**: `\item` lines, one formula (or one short rule) per bullet, bullet in the chapter colour.
- **Recipes**: `\recipe{name}{\item step ...}`. In the Review the name stands in a left column and the numbered steps (numbers in the chapter colour) run on to its right,
  which keeps a Review on one page. In the Summary the name stands above the steps. Write every step as a full sentence with a full stop. One recipe never splits.
- `\newterm` makes the link target only the first time a term is used, and defines the key. A term that a Review needs must be introduced with `\newterm` before it.
- The Summary is a two-column page in `summarybox` with more line spacing. It is about 3 pages for a chapter of 4 paragraphs and Prior knowledge.

## Prior knowledge
Prior knowledge stands apart from the chapter. It is everything the rest of the chapter's theory builds on: concepts from wiskunde B (`reference/vwo-wiskunde-b.md`)
and from earlier chapters of the course, found by dependency (see "What Prior knowledge is" in `pedagogy-cycle.md`), and only what the chapter uses.
- **Colour.** Its own mustard (RGB 150,104,8), never the chapter colour: the header band, the box titles, the new terms, the letter cells in the Contents. The title line "Prior knowledge" in the Contents stays black like the other titles. Put the
  whole section in `\begin{priorsection}\priortitle ... \end{priorsection}`, which sets the colour locally.
- **Letters.** The blocks are `\begin{priorbox}{A: title}{PA}` and are titled "Prior A", "Prior B", ...; the chapter's own Theory starts at A again, in the chapter
  colour. In the Contents the Prior letters are mustard cells with their gold exercise numbers, in one flowing row like the other paragraphs, with no label text.
- **Origin.** With only wiskunde B there is one group and no sub-heading. When earlier chapters are repeated too, group the blocks with `\priorgroup{From wiskunde B}` and
  `\priorgroup{From chapter 1}`, and start a block from an earlier chapter with `\priorfrom{Taught in chapter 1, Theory G}`. The Contents shows the groups as a small gap.
- **Not in the Summary.** The Summary and its letter row (A to the last chapter letter) contain only the chapter's own Theory.

## Line and page breaks
These rules live in one shared file, `reference/mastery-breaks.sty`. The chapter loads it with `\usepackage{mastery-breaks}` (in the preamble), adds the key
`partbreaks` to its `\setlist[enumerate,2]{...}`, and uses `\mbkeep` / `\mbtight` in its boxes and in `\sol`. `build-chapter.sh` puts the reference folder on
`TEXINPUTS`, so nothing is copied next to the chapter. Change a rule in the `.sty` and every chapter follows at its next build. Do not override the rules per chapter.
1. **An exercise (one number) stays on one page.** A break between its parts costs a penalty of 3000, a break between two exercises is
   cheap, so a whole exercise moves to the next page when it does not fit.
2. **If an exercise must split, at least 2 parts stay on each side.** With n parts a break before part i is allowed only when
   3 <= i <= n-1. So an exercise of 3 parts or fewer never splits, one of 4 splits 2+2, and the intro text is never left with 0 or 1 parts.
   The preamble counts the parts of every level-2 list through the `.aux` (`\dcnp`), so it needs the 3 passes of `build-chapter.sh`.
3. **Theory boxes never break inside a paragraph** (`theorybox`, `theorycont`, `workedbox`, `terugblikbox`, and the `recipebox` inside
   them): `\interlinepenalty=10000`. A page break falls between paragraphs. A lead-in line stays with its display.
4. **A solution stays with its part**: `\sol` puts `\nobreak` before the solution and after it, and the space after a part is glue that
   is not a break point. A solution box may still break between steps, but never leaves a single line alone.
5. **No single line at the top or bottom of a page** (`\clubpenalty`, `\widowpenalty`, `\displaywidowpenalty` = 10000).
6. **No hyphenation** (`\hyphenpenalty=10000`). To keep lines even: `microtype` protrusion (font expansion is off, because one font in the
   chapters is not scalable and expansion stops the build), `\tolerance=2000`, `\emergencystretch=2em`.
7. **A formula in running text never breaks** (`\binoppenalty=\relpenalty=10000`). A formula longer than a line overflows, so it must
   be written as a display.

8. **`\needspace` is an exact test** (`\pagetotal` against `\pagegoal`), used before a V exercise so its stem and axes start on a page with room for them.
   The stretch trick of the real `needspace` package must not be used: on a page without stretch it makes TeX break early and leaves half a page empty.

Measured on chapter 1: about 2 percent more pages in the questions PDF and about 4 percent in the answers PDF, because whole exercises and
whole Theory paragraphs move to the next page and leave white space at the page bottom. This is the intended trade.

## Contents pills for Prior knowledge, Summary and Diagnostic check
`reference/contents-mock.tex` is a compiling mock-up of the full Contents page (fake data). It shows the target:
- Prior knowledge: one pill per Prior knowledge Theory block (letter cell, then P cells numbered on their own stream).
- Summary: one snake pill with every Theory letter of the chapter, A to the last, one cell each (cells 11pt, 15pt for two letters).
- Diagnostic check: pale cells in the page-number style (chapter colour at 35%, number in the chapter colour), only numbers, one pill
  per paragraph group, no labels.
Build the registration for these the same way as for the paragraphs (write `\exentry` lines, read them back in the Contents).

- `\newterm{...}` (first use of a new term, in the Theory blocks and in the Legend line "New term") is bold in the chapter colour (`chapcolor`), not orange.
- Legend page: the "Colours" row is the first item under "How to read the chapter", the current chapter outlined with a 1.6pt black line. The worked example title and its rule are black everywhere (also in the Legend sample), and the Solution strip is a `\legbox` (same padding as Review). There is no separate Prior knowledge box in the Legend, "The pages" covers it.

- **Links.** The page number at the bottom of every page (the whole dome) links back to the Contents (`\hypertarget{contents}` is put above `\tableofcontents`). The Legend has a "Links" item that
  lists everything that can be clicked: Contents cells, terms in a Review or Summary, source lines and the page number.
- **Worked example questions.** Every lettered part of the question starts on its own line (`\wpart(a)`, `\wpart(b)`, ...), never all in one running italic paragraph. The stem, if there is one, stands on the line above (a).
