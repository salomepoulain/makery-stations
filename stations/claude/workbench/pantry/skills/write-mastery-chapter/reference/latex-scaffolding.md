> **Superseded in places.** The preamble to copy into every chapter is `reference/preamble-visual.tex` and the look is described in
> `reference/design-system.md`. Read this file for the structure rules (Summary, Diagnostic check, cross-references), not for the
> old badge, header and Legend macros.

# LaTeX scaffolding

The exact preamble every chapter this skill produces shares. Copy this block into the
chapter's single `.tex` file (see "File structure" below). There is only one preamble, so there
is nothing to keep in sync.

## Dependencies

This preamble needs `tcolorbox` (with the `skins` and `breakable` libraries) and `hyperref`,
neither of which ships with a minimal/basic TeX Live install. If `pdflatex` fails with
`File 'tcolorbox.sty' not found` (or `tikzfill.image.sty`, or `pdfcol.sty`; these come in
one at a time as tcolorbox's own dependency chain unfolds), install them without touching the
system tree:

```bash
tlmgr init-usertree   # once, if not already done
tlmgr --usermode install tcolorbox environ pgfopts trimspaces tikzfill pdfcol pgfplots
```

This installs into the user's own texmf tree and needs no admin/sudo access. Confirmed working
this way in this project's environment (a TeX Live "basic" scheme was missing all six
packages initially).

## The preamble

```latex
\documentclass[11pt]{article}
\usepackage[margin=1in,bottom=0.8in]{geometry}
\usepackage{amsmath,amssymb}
\usepackage{xcolor}
\usepackage{tikz}
\usetikzlibrary{matrix,decorations.pathreplacing,calc,positioning}
\usepackage{pgfplots}\pgfplotsset{compat=1.16}
\definecolor{vpink}{RGB}{233,30,140}
\pgfplotsset{mastery/.style={width=4.9cm,height=3.6cm,axis lines=left,grid=major,grid style={gray!25},tick label style={font=\scriptsize},label style={font=\footnotesize},title style={font=\footnotesize},ymin=0,scaled y ticks=false,yticklabel style={/pgf/number format/.cd,fixed,precision=3},every axis plot/.append style={thick}}}
\usepackage{tcolorbox}
\tcbuselibrary{skins,breakable}
\usepackage{pdfrender}
\usepackage{multicol}
\usepackage{hyperref}
\hypersetup{colorlinks=true, linkcolor=violet!55!black, citecolor=violet!55!black,
  urlcolor=violet!55!black, linktoc=all}

\newcommand{\R}{\mathbb{R}}
\renewcommand{\labelenumii}{(\alph{enumii})}
\setlength{\jot}{8pt}
\newif\ifshowanswers
% one source, two PDFs: build-chapter.sh defines \hidesolutions for the questions-only PDF
\ifdefined\hidesolutions\showanswersfalse\else\showanswerstrue\fi

\newcommand{\sol}[1]{%
\ifshowanswers
\par\noindent\colorbox{blue!5}{\begin{minipage}{0.96\linewidth}#1\end{minipage}}\par\vspace{0.7em}
\else
\par\vspace{1.8em}
\fi}

\let\oldenumerate\enumerate
\let\endoldenumerate\endenumerate
\renewenvironment{enumerate}{\oldenumerate\setlength{\itemsep}{3pt}\setlength{\parskip}{1pt}\setlength{\topsep}{2pt}}{\endoldenumerate}

% --- chapter identity: the chapter number picks a dark rainbow color, used by every header ---
\definecolor{chcolor1}{RGB}{183,28,28}    % 1 red
\definecolor{chcolor2}{RGB}{204,85,0}     % 2 orange
\definecolor{chcolor3}{RGB}{166,124,0}    % 3 yellow (dark gold)
\definecolor{chcolor4}{RGB}{27,120,45}    % 4 green
\definecolor{chcolor5}{RGB}{21,101,192}   % 5 blue
\definecolor{chcolor6}{RGB}{63,61,168}    % 6 indigo
\definecolor{chcolor7}{RGB}{123,47,158}   % 7 violet
\colorlet{chapcolor}{black}
\newcommand{\thick}{\pdfrender{TextRenderingMode=FillStroke,LineWidth=0.45pt}}  % faux extra-bold, stroked in the current color
\newcommand{\setchapter}[1]{\colorlet{chapcolor}{chcolor#1}}
\newcommand{\chaptertitle}[4]{\setchapter{#2}\begin{center}%
{\LARGE\bfseries\color{chapcolor}\thick #1: CHAPTER #2\enspace #3}\\[6pt]{\large\color{chapcolor} #4}\end{center}}
\makeatletter
\renewcommand\section{\@startsection{section}{1}{\z@}{-3.5ex \@plus -1ex \@minus -.2ex}{2.3ex \@plus.2ex}{\normalfont\Large\bfseries\color{chapcolor}\thick}}
\renewcommand\subsection{\@startsection{subsection}{2}{\z@}{-3.25ex\@plus -1ex \@minus -.2ex}{1.5ex \@plus .2ex}{\normalfont\large\bfseries\color{chapcolor}\thick}}
\newcommand{\pnum}{\tikz[remember picture,overlay]{\fill[chapcolor,fill opacity=0.3]([xshift=-0.6cm]current page.south) arc[start angle=180,end angle=0,radius=0.6cm]--cycle;\node[text=chapcolor,font=\bfseries\small,anchor=south] at ([yshift=0.08cm]current page.south){\thepage};}}  % dome on the bottom edge, page number inside
\def\ps@plain{\let\@oddhead\@empty\let\@evenhead\@empty\def\@oddfoot{\hfil\pnum\hfil}\let\@evenfoot\@oddfoot}
\pagestyle{plain}
\makeatother

% --- badges: exercise role, not exercise identity. No outline on any of them. ---
\newcommand{\badge}[2]{\begin{tikzpicture}[baseline=-0.65ex]\node[shape=circle,fill=#1,inner sep=1.4pt,font=\bfseries\scriptsize,text=white]{#2};\end{tikzpicture}}
\newcommand{\Obadge}{\badge{teal!60!black}{O}}
\newcommand{\Tbadge}{\badge{orange!85!red}{T}}
\newcommand{\Rbadge}{\badge{violet!70!black}{R}}
\newcommand{\Abadge}{\badge{green!45!black}{A}}
\newcommand{\Dbadge}{\badge{red!70!black}{D}}
\newcommand{\Pbadge}{\badge{yellow!40!orange!85!black}{P}}
\newcommand{\Vbadge}{\badge{vpink}{V}}
\newif\ifvfill  % V exercises: axes are drawn blank in the question, and filled inside \sol
% starts a new page when less than the given space is left (exact test with \pagetotal; the stretch trick of the needspace package
% is not used, it breaks the page early whenever the page has no stretch)
\newcommand{\needspace}[1]{\par\begingroup\dimen0=\pagetotal\advance\dimen0 by #1\relax\ifdim\dimen0>\pagegoal\penalty-10000 \fi\endgroup}

% --- the Theory unit: a STACK OF SIBLING BOXES (text, worked example, text ...) ---
% tcolorbox cannot nest a breakable box inside another one, and a worked example with a figure in it
% must be able to break across pages. So the unit is theorybox, then workedbox, then theorycont, ...
% with matching tints and no gap between them; the reader sees one region.
\newtcolorbox{theorybox}[2]{breakable, enhanced, sharp corners, colback=yellow!15, colframe=yellow!15,
  boxrule=0pt, frame hidden, left=8pt, right=8pt, top=2pt, bottom=4pt,
  before skip=6pt, after skip=0pt,
  title={\large\bfseries\color{chapcolor}\thick Theory #1}, fonttitle=\normalsize,
  coltitle=chapcolor, colbacktitle=yellow!15, toptitle=3pt, bottomtitle=3pt,
  label={thy:#2}}
\newtcolorbox{theorycont}{breakable, enhanced, sharp corners, colback=yellow!15, colframe=yellow!15,
  boxrule=0pt, frame hidden, left=8pt, right=8pt, top=2pt, bottom=4pt,
  before skip=0pt, after skip=0pt}
\newtcolorbox{recipebox}{enhanced, colback=yellow!15, colframe=yellow!15, boxrule=0pt,
  borderline west={2pt}{0pt}{violet!55!black}, left=10pt, right=4pt, top=3pt, bottom=3pt}
\newtcolorbox{workedbox}{breakable, enhanced, sharp corners, colback=yellow!4, colframe=yellow!15,
  boxrule=0pt, leftrule=8pt, rightrule=8pt, toprule=4pt, bottomrule=4pt,
  toprule at break=0pt, bottomrule at break=0pt,
  left=6pt, right=6pt, top=4pt, bottom=4pt, before skip=0pt, after skip=0pt}
\newcommand{\workedheading}{\textbf{\color{teal!55!black}Worked example}\par\smallskip\noindent\itshape}
\newcommand{\workedanswer}{\par\upshape\smallskip\noindent{\color{teal!55!black}\rule{2.5em}{0.6pt}}\par\smallskip\noindent}
\newcommand{\scenario}[1]{\par\noindent#1\par\medskip}
\newtcolorbox{refreshbox}[1]{breakable, enhanced, colback=yellow!9, colframe=yellow!9,
  boxrule=0pt, frame hidden, left=8pt, right=8pt, top=2pt, bottom=4pt,
  title={\Pbadge\enspace\large\bfseries\color{chapcolor}\thick Prior knowledge: #1}, fonttitle=\normalsize,
  coltitle=chapcolor, colbacktitle=yellow!9, toptitle=3pt, bottomtitle=3pt}
\newtcolorbox{terugblikbox}{breakable, enhanced, colback=purple!5, colframe=purple!5,
  boxrule=0pt, frame hidden, left=8pt, right=8pt, top=2pt, bottom=4pt,
  title={\Large\bfseries\color{chapcolor}\thick Review}, fonttitle=\normalsize,
  coltitle=chapcolor, colbacktitle=purple!5, toptitle=4pt, bottomtitle=4pt}
\newenvironment{summarybox}{\pagecolor{purple!5}\small\raggedright\setlength{\columnsep}{22pt}\begin{multicols}{2}}{\end{multicols}\clearpage\nopagecolor}  % tinted page, two columns (multicols cannot live inside a breakable tcolorbox)
\newcommand{\sumsetup}{\setlength{\itemsep}{2pt}\setlength{\parsep}{0pt}\setlength{\topsep}{2pt}\setlength{\leftmargin}{1.2em}}
\newcommand{\sumhead}[1]{\medskip\noindent{\large\bfseries\color{chapcolor}\thick #1}\par\smallskip}

% --- exercise numbering: always a bare number, never a compound label ---
\newcounter{exN}     % one continuous stream across the whole chapter, never reset
\newcounter{priorN}  % Prior knowledge's own separate stream, never reset
\newcommand{\exnum}{\stepcounter{exN}{\bfseries\large\arabic{exN}}}
\newcommand{\priornum}{\stepcounter{priorN}{\bfseries\large\arabic{priorN}}}
\newcommand{\extag}[1]{#1\,\exnum}      % badge immediately left of the number
\newcommand{\priortag}[1]{#1\,\priornum}  % same, for the Prior knowledge stream

% --- paragraph headings, cross-references, table of contents ---
\newcommand{\parasection}[2]{\clearpage\section*{\S#1: #2}\addcontentsline{toc}{section}{\S#1: #2}\label{sec:#1}}
\newcommand{\frontsection}[1]{\section*{#1}\addcontentsline{toc}{section}{#1}}
\newcommand{\secref}[1]{\hyperref[sec:#1]{\S#1}}
\newcommand{\thyref}[2]{\hyperref[thy:#1#2]{\S#1 Theory #2}}
\newcommand{\pthyref}[1]{\hyperref[thy:P#1]{Prior knowledge Theory #1}}

% --- new term marker: the one moment a term/symbol gets defined, never after ---
\newcommand{\newterm}[1]{\textbf{\color{chapcolor}#1}}

% --- provenance marker: one mechanism for any reference to a known source document ---
% (superseded: the source label is a grey arrow or capsule, see preamble-visual.tex and design-system.md, "Source labels")
\newcommand{\srcref}[1]{\textit{\footnotesize[$\blacktriangleright$#1]}}
```

## Usage rules

- **Writing for good breaks** (the page rules are in `design-system.md`, "Line and page breaks"). Every part of an exercise is an
  `\item[(a)]` of a level-2 `enumerate` and ends with `\sol{...}`; the page-break hook relies on both. Never write a long formula
  (more than about half a line) in running text, make it a display, because inline formulas do not break. Tie one- and two-letter words and
  a lone symbol to the next word with `~` (`at distance~$h$`, `a~line`, `is~$0$`), so a line does not end on them. Give an exercise with 4 or
  more parts a natural split (2+2, 3+3), and keep an exercise of 3 parts short enough to fit on a page.

- **A Worked example is a `workedbox` that directly follows its `theorybox`** (sibling boxes,
  no gap, matching outer tint), not bare inline text and not separated by anything: it needs a clearly lighter yellow background,
  distinct enough from the theory's own tint to actually read as a separate region (a gap of
  only a few percentage points, e.g. `yellow!8` next to `yellow!4`, is too subtle to notice;
  the current pairing is `yellow!15` for the theory and `yellow!4` for the worked example) so
  a reader can see where the theory ends and the example begins, without it ever leaving the
  theory's own colored region. Structure:
  ```latex
  \begin{theorybox}{...}{...}
    ...theory prose...
  \end{theorybox}
  \begin{workedbox}
    \workedheading <problem statement, printed in italics>

    \workedanswer <worked steps, upright, after a short teal rule>
  \end{workedbox}
  \begin{theorycont}   % only if more theory follows the example (a recipebox goes in here)
    ...
  \end{theorycont}
  ```
  The heading stands on its own line, the question is italic, and a short teal rule separates it
  from the answer. Never write the word "Solution" in a worked example. Every `\workedheading`
  must be followed by a `\workedanswer` in the same box, or the italics leak. For a question
  with parts, use `\workedanswer \textbf{(a)}\enspace ...` and `\textbf{(b)}\enspace ...`
  for the later parts.
  A second example in the same block opens another `workedbox` lower in the same theorybox.
  `workedbox` is `breakable`, with `toprule at break=0pt` so the seam at a page break is clean.
  A worked example never floats away from the theory it belongs to. Nesting breakable boxes is
  impossible in tcolorbox, which is why the unit is a stack of siblings.
- **`recipebox` lives inside a `theorybox` or a `theorycont`**, not standalone. Only use it for genuinely
  procedural content (a numbered how-to); not every Theory block needs one.
- **Diagrams/visuals that explain a Theory concept live inside that `theorybox`** too (as plain
  TikZ content in the main text of the `theorybox`/`theorycont`). Never as a standalone box.
- **Never narrate the source assignment's own scaffolding inline** (no "per the hint," no
  "as the homework suggests"). Theory and Worked-example prose stand alone, as if no external
  assignment existed; provenance is marked only via `\srcref{...}`, never narrated in the text
  itself.
- **`\scenario{...}`** puts extra vertical space after a concrete setup's setting prose, so it
  reads visually as its own beat before the question that follows, without needing a color
  change (plain black, same as everything else). If that setup
  only feeds the first exercise that uses it (the usual case: a paragraph opens with one
  running example, and only its first item actually needs the setup restated), put
  `\scenario{...}` *inside that exercise's own item*, as its opening line, not as a free
  paragraph sitting above the `enumerate` before the badge/number even starts. A paragraph
  that reads as free-floating text with no badge or number next to it looks like it belongs to
  everything that follows, which is misleading if it's really just leading into one specific
  exercise. Only place it outside the `enumerate`, as its own paragraph, when the setup
  genuinely spans the whole paragraph's Theory block and every exercise in it, not just the
  first one.
- **Theory letters run continuously across the whole chapter and never reset at a paragraph
  boundary.** If Prior knowledge has Theory A and Theory B, the first numbered paragraph's
  first Theory block is Theory C, not Theory A again; the next paragraph picks up from
  wherever the previous one left off. This is a plain authoring convention (the letter you
  type in `\theorybox`'s title), not something a counter enforces automatically, so keep track
  of the running letter as you write each paragraph in order.
- **`\exnum`/`\priornum` are called once per exercise**, in document order, inside `\item[...]`.
  Exercises in the Prior knowledge section are plain `\item[\priornum]` (their own counter)
  with no badge: the yellow Prior knowledge pages already say what they are, and a badge on
  every one is redundant. A regular badged item is `\item[\extag{\Tbadge}]`; a plain item is
  `\item[\exnum]`. Sub-parts inside one exercise stay ordinary `(a)`, `(b)`, `(c)` via the
  nested `enumerate`'s `labelenumii`.
- **Prior knowledge has two forms, and both use the same yellow identity.** (1) The opening
  Prior knowledge section: own yellow-tinted pages, plain `\item[\priornum]` exercises with no
  badge. Aim to make this section good enough that nothing else is needed. (2) An inline
  *refresher* inside a numbered paragraph, when a reader hits a gap (this is what a Mode B
  fix usually adds): a `\begin{refreshbox}{Topic}...\end{refreshbox}` (pale yellow box, amber
  `\Pbadge` and the chapter-colored title "Prior knowledge: Topic") holding a concise recap and,
  if useful, one tiny worked line, followed by a normal `\item[\extag{\Pbadge}]` exercise on
  that paragraph's own `\exnum` stream. A refresher never introduces new material; anything
  that is genuinely new gets a Theory block instead. Place it right before the first use of
  the thing it refreshes. The badge is drawn like every other one (solid amber circle, white
  letter, no outline).
- **`\parasection{N}{Title}` starts every numbered paragraph** and forces a fresh page. It does
  *not* reset the exercise counter: exercise numbers run continuously through the whole
  chapter, so if §1's last exercise is 7, §2's first is 8. Never call `\setcounter{exN}{0}`
  anywhere. (Prior knowledge keeps its own separate `\priornum` stream, and the Diagnostic
  check uses its own plain independent numbering; neither touches `exN`.)
- **Page tints mark the special sections, and the Legend explains each of them.** Prior knowledge pages get a very pale, almost white yellow page
  background: `\clearpage\pagecolor{yellow!8}` right before `\frontsection{Prior knowledge}`,
  and `\clearpage\nopagecolor` right before the first `\parasection`. The Diagnostic check
  pages use the chapter's own color: `\clearpage\pagecolor{chapcolor!10}` right before
  `\frontsection{Diagnostic check}` (nothing needs to reset it, it runs to the end). The
  Summary is already tinted by `summarybox`. Numbered paragraphs stay on plain white.
- **Don't re-explain the P badge in Prior knowledge's opening sentence.** The Legend already
  says what it means; the section intro should only say which tools the chapter leans on.
- **Prior knowledge is not a numbered paragraph.** Use `\frontsection{Prior knowledge}` (no
  `\clearpage`, no `\label{sec:...}`, no entry in the `\secref`/`\thyref` system, but it still
  gets a table-of-contents entry) and its own `\priornum` stream.
- **Every "§N" or "§N Theory X" mention in authored prose uses `\secref{N}`/`\thyref{N}{X}`.**
  A Theory block inside Prior knowledge instead uses `\pthyref{X}` (there's no section number to
  hyperlink from there). Never write the section symbol as bare text; every such mention must be
  a working hyperlink.
- **Every top-level heading that deserves a table-of-contents entry uses `\frontsection{...}`,
  with no exceptions**, including Summary and Diagnostic check. A bare `\section*{...}` never
  appears in a chapter body; if you catch yourself writing one, it's a `\frontsection{...}`
  or a mistake. There is no separate "Synthesis" section reproducing the source assignment
  verbatim; questions taken from a known source get answered where they naturally belong, in
  the paragraph whose Theory block covers them, or as a Diagnostic check item, tagged with
  `\srcref{...}` for provenance, not gathered into their own standalone section.
- **`\newterm{word}`** marks the single first appearance of a new term or symbol, bold and
  colored, immediately followed by a plain-language explanation. Every later use of that same
  term is ordinary unstyled text. See `reference/pedagogy-cycle.md`'s "Baseline knowledge and
  ground-up notation" for the rule this enforces (everything past high-school math gets
  introduced this way, no exceptions).
- **`\srcref{label}`** is the one mechanism for pointing at a known source document, rendering
  a terse bracketed code like `[►PS1]` or `[►HW1 3b]`, never a prose caption. Include the
  specific sub-part when there is one (`\srcref{HW1 3b}` for source exercise 3, part b), not
  just the document name; the point is knowing exactly which question, not just which document.
  Use it for either case: a whole exercise adapted from an external source (place it right
  after the exercise's own number, e.g. `\item[\exnum] Adapted from a Practice Set
  \srcref{PS1}. ...`), or one sub-part reproduced verbatim from the source assignment (place it
  inline in that sub-part's own text, e.g. `\item[(a)] \srcref{HW1 3a} ...`, at the sub-part's
  normal indented level). It is a provenance marker, not a pedagogical-role badge; don't
  conflate it with O/T/R/A/D/P.
- **`\sol{}` and `\ifshowanswers` are unchanged from the existing pattern**, see "File
  structure" below. `\sol{}` boxes stay plain `\colorbox`+`minipage` (not `tcolorbox`); they are
  short enough in practice that breakability hasn't been needed. If a future solution runs long
  enough to overflow a page, that's a sign to split it across multiple `\sol{}` calls (one per
  major step), not to redesign this macro.

## Required opening: title, Contents, Legend, Prior knowledge

Every chapter opens with these things, in this order, before any numbered paragraph. This is a
body-level contract, not only a macro choice: a chapter can use the right preamble and still be
wrong if the Contents, Legend or Prior knowledge plumbing is missing.

1. **Title.** Call `\chaptertitle{COURSE}{N}{Chapter name}{Subtitle}` right after
   `\begin{document}` (never `\maketitle`); it prints `COURSE: CHAPTER N  Chapter name` in bold
   in the chapter's rainbow color with the subtitle beneath. It also sets the chapter color,
   so it must come before anything else. Follow it with one or two sentences naming what the
   chapter covers and whether this PDF shows full worked solutions, using
   `\ifshowanswers ... \else ... \fi` so one sentence works for both PDFs.

   **Rainbow rule.** The chapter number picks a dark rainbow color (1 red, 2 orange, 3 yellow,
   4 green, 5 blue, 6 indigo, 7 violet; the RGB values are in the preamble, chosen dark enough
   to contrast with a white page) and every header is bold (with a thin same-color outline for extra weight) in that color: the
   title, `\section` and `\subsection` headings, Theory and Review box titles, and
   `\sumhead`. Page numbers sit in a small faint dome (half circle, 30% opacity) of the same color on the
   bottom edge of the page (`\pnum`, wired into the plain page style; it needs the extra
   `bottom=0.8in` geometry setting and a second pdflatex pass), which keeps the number
   low and out of the text area. Prior knowledge's heading is just "Prior knowledge", with no
   subtitle after it (its opening sentence says what it covers). A chapter numbered
   past 7 needs its own `\definecolor{chcolorN}` line added to the preamble first.
2. **Contents.** Put the Contents on the title page, directly after the short introductory
   sentence(s), and wrap it so links render black:

   ```latex
   \begingroup
   \hypersetup{linkcolor=black}
   \tableofcontents
   \endgroup
   \clearpage
   ```

   The `preamble-visual.tex` preamble redefines `\tableofcontents` so the page-number dome can
   link back to it. Keep this wrapper in the body anyway: it is the visible house style for the
   Contents page. The Contents must be complete on page 1; if it spills, shorten the title-page
   introduction before changing the Contents style.

3. **Legend.** The Legend is a locked page, not authored content. Copy
   `reference/legend-template.tex` verbatim into the chapter body after the Contents and before
   Prior knowledge. Do not rewrite it, shorten it, localize it, swap in chapter-specific source
   labels, change the example Contents pill, or move it to another page. The checker compares
   the chapter's Legend against this template after whitespace normalization.

   The template is built from the macros `preamble-visual.tex` defines for exactly this purpose
   (`\legletter`, `\legbox`, `\legpage`, `\legchap`, `\legpnum`, `\legsrcpill`, `\srcinline`,
   `\pillgroup`). This structure is settled, the same in every chapter this skill produces,
   matching the badge taxonomy of `reference/pedagogy-cycle.md` letter for letter (`\Pbadge
   \Obadge \Tbadge \Dbadge \Vbadge \Ebadge \Cbadge \Rbadge`, in that order: P O T D V E C R).
   Do not redesign it, invent a different set of badges, or fall back to a plain `description`
   list.

   For reference, the locked page currently reads:

   ```latex
   \frontsection{Legend}
   \noindent Every exercise has a tag in the left margin: a coloured letter for its type, then its number. The numbers run through the whole
   chapter. The parts of an exercise are (a), (b), (c).

   \medskip\noindent\textbf{The boxes}\par\smallskip
   \begin{tcolorbox}[enhanced, sharp corners, colback=yellow!15, colframe=yellow!15, boxrule=0pt, left=8pt, right=8pt, top=4pt, bottom=4pt, before skip=5pt, after skip=0pt]
   \textbf{\color{chapcolor}Theory block.} Theory, built up from a concrete case. A new term is marked once, where it first appears.
   Figures sit in this box.
   \begin{recipebox}
   \textbf{Recipe.} A numbered how-to, marked by a purple bar.
   \end{recipebox}
   \end{tcolorbox}
   \begin{workedbox}
   \textbf{Worked example}\par\smallskip\noindent\itshape Worked example. The question is in italics.

   \par\upshape\smallskip\noindent\rule{2.5em}{0.6pt}\par\smallskip\noindent The answer follows below the short rule, one step per line.
   \end{workedbox}
   \legbox{purple!5}{\textbf{\color{chapcolor}Review.} Closes a paragraph with its terms (click one to jump to where it was introduced), its formulas and its recipes.}
   \legbox{blue!5}{\textbf{Solution.} The answer to the exercise above. Only in the answers version.}\medskip

   \noindent\textbf{The exercise types, in the order they appear}\nopagebreak
   \begin{description}[style=unboxed,leftmargin=0pt,itemsep=7pt,parsep=0pt]
   \item[\legletter{\cP}{P}\hspace{0.6em}Prior knowledge] Something you are assumed to know, made fluent before new material builds on it. Its exercises
   have their own numbers, in gold, and no letter.
   \item[\legletter{\cO}{O}\hspace{0.6em}Orient] A concrete probe you can already solve with what you know. It comes before a Theory block, so that the
   general rule feels earned and does not arrive cold.
   \item[\legletter{\cT}{T}\hspace{0.6em}Test] A gate-check right after the worked example: the same task with smaller numbers. It shows whether you are
   ready to move on, and it drills a little too.
   \item[\legletter{\cD}{D}\hspace{0.6em}Drill] The bulk of the practice: one family of the same move with different numbers, so the skill gets fast
   before anything harder is asked.
   \item[\legletter{\cV}{V}\hspace{0.6em}Visualize] Predict or sketch a picture, such as how a curve moves when a parameter changes, on empty axes first.
   Then compare with the plot in the solution. It builds a feel for what the formula does.
   \item[\legletter{\cE}{E}\hspace{0.6em}Exam] The level the course expects: chained questions with no hints, where you choose the method and write out the
   whole argument. If you can do these cleanly, you are ready.
   \item[\legletter{\cC}{C}\hspace{0.6em}Challenge] Harder than the exam asks, for example an unusual framing or an edge case. It is for depth, so skip it
   on a first pass.
   \item[\legletter{\cR}{R}\hspace{0.6em}Reflect] A short question that asks why. It revisits a step and generalizes it, answered in words. It deepens
   understanding, but the exam does not depend on it.
   \end{description}
   \noindent\textbf{Short on time?} Do T, D, V and E. C and R are extras.\par\medskip

   \needspace{12\baselineskip}
   \noindent\textbf{How to read the chapter}\nopagebreak
   \begin{description}[style=unboxed,leftmargin=0pt,itemsep=8pt,parsep=0pt]
   \item[Colours] The chapter number sets the colour of all headers. This is chapter \thischap. Prior knowledge always has its own colour, mustard.\par\smallskip
   \noindent\legchap
   \item[Contents] Each exercise is a cell in the colour of its type, and each Theory block is one pill that starts with its letter. Click a
   cell to jump there.\par\smallskip
   \noindent\mbox{\pillgroup{{L/K,O/1,T/2,D/3,D/4,D/5,D/6,V/7,E/8,C/9,R/10}}}
   \item[Links] Almost everything you can click jumps somewhere. A cell in the Contents goes to its exercise or Theory block. A term in a Review or Summary, in the chapter colour, goes to the place where it was introduced. A source line in the Summary goes to its Theory block. The page number \legpnum\ at the bottom of every page goes back to the Contents.
   \item[Source tag] A brown label marks a question taken from a source, in that source's wording. A source is on the whole exercise or on its parts, never on both.\par\smallskip
   \noindent\hspace*{\dimexpr\wfix-2pt\relax}\srcinline{Math4AI Ex 2}\enspace An arrow in the margin points to a part.\par\smallskip
   \noindent\legsrcpill{HW1 1a}{green!45!black}{E}{7}\enspace A capsule around a badge marks the whole exercise.
   \item[New term] A \newterm{bold coloured term} marks the first use of a new term, explained where it appears.
   \item[Assumed] Dutch VWO mathematics (wiskunde B), and nothing else. Matrices, sums with the Sigma symbol and partial derivatives are built up here.
   \end{description}
   \medskip

   \noindent\textbf{The pages}\par\smallskip
   \legpage{white}{\textbf{White page.} The numbered paragraphs, where new material is taught.}
   \legpage{yellow!8}{\textbf{Prior knowledge page.} What you are assumed to know, made fluent.}
   \legpage{purple!5}{\textbf{Summary page.} A two-column cheat sheet of the chapter.}
   \legpage{chapcolor!10}{\textbf{Diagnostic check page.} Fresh questions to test yourself, in the chapter colour.}
   ```

   Never drop the eight-entry taxonomy list, never rename or reorder a badge, and never invent a
   badge outside P O T D V E C R.
4. **Prior knowledge.** Start Prior knowledge after the Legend, on a fresh mustard-tinted page,
   and immediately register its Contents row:

   ```latex
   \clearpage
   \pagecolor{yellow!8}
   \begin{priorsection}
   \priortitle
   \addtocontents{toc}{\protect\dcrowflat{0}}

   \priorgroup{From wiskunde B}
   ...
   \end{priorsection}
   \clearpage
   \pagecolor{white}
   ```

   The `\addtocontents{toc}{\protect\dcrowflat{0}}` line is mandatory whenever there is a Prior
   knowledge section. Prior exercises log themselves under paragraph `0`; this line is what
   makes the mustard Prior-knowledge pills appear in the Contents. Without it, the PDF compiles
   but the navigation grammar is broken.

Keep the Contents to paragraph-level and front/back-matter entries (Prior knowledge, Legend
itself, Summary, Diagnostic check); do not add individual Theory blocks to it. A Theory block is
reached via `\thyref`/`\pthyref` from running prose, not from the table of contents. This keeps
the table of contents small, matching its job: orient the reader, not enumerate everything.

Use `\frontsection{...}` (not bare `\section*{...}`) for every top-level heading that isn't a
numbered paragraph but still deserves a table-of-contents entry: Legend, Prior knowledge,
Summary, Diagnostic check. This is not optional for any of them; a chapter with a bare
`\section*{Diagnostic check}` has a bug, not a stylistic variation.

## Required closing: summary, diagnostic check

After the last numbered paragraph's Review, precede `\frontsection{Summary}` with a
`\clearpage`, exactly like a numbered paragraph does, so it starts its own fresh page. Every
chapter with more than one paragraph gets this Summary, in a `summarybox`, covering the
*whole* chapter, everything together, not just the numbered paragraphs. It is a cheat sheet:
someone should be able to redo the chapter's exercises from this page alone. The box has no
title of its own (the `\frontsection{Summary}` heading above it is the only "Summary" on the
page). Structure it as follows:

- **Grouped by paragraph, in chapter order**: one `\sumhead{...}` sub-heading each for Prior
  knowledge and for every numbered paragraph, so the reader can find a paragraph's material
  at a glance.
- **Under each sub-heading, three labeled kinds of content, in this order**: the *terms*
  introduced there (each name with a one-line meaning), the *formulas* (every boxed result,
  stated in full), and the *recipes* (the numbered how-to procedures, restated step by step).
  Rules for how to create or compute things belong here as much as facts do. Skip a kind only
  if that paragraph genuinely has none of it.
- **Completeness over brevity.** Never drop a term, formula, recipe step, or result to save
  space; a full page is fine, several pages is fine if the chapter earns it. Compress phrasing,
  not content.
- **Two columns, small font, one tinted page.** `summarybox` is an environment (not a
  `tcolorbox`, because `multicols` overflows inside a breakable one) that tints the page,
  sets `\small`, and flows the content in two columns, so a chapter's whole cheat sheet stays
  compact. Use `\begin{itemize}\sumsetup` for each list (tight item spacing, small indent),
  one item per term, formula, or recipe, rather than running everything together as one
  dense paragraph.
- **Hyperlink each group back to its source Theory block** with `\thyref`/`\pthyref`, on a
  small `Source:` line directly under the `\sumhead`, not inside the heading itself (the
  link text already says "Theory X", which makes a heading repeat itself).

A single-paragraph chapter can skip this (its one Review already serves the same purpose) and
go straight to the Diagnostic check.

Precede `\frontsection{Diagnostic check}` with a `\clearpage` too, so it always starts its own
distinct page, never sharing a page with the end of the Summary. Per
`reference/pedagogy-cycle.md`'s "Diagnostic check (chapter-end)": independent numbering, no
O/T/R/A/D/P tags, grouped under repeated paragraph sub-headings, roughly even item count per
section regardless of how much practice that section's body actually had. Questions taken
verbatim from the chapter's source assignment, if any, are one more group inside this same
Diagnostic check (tagged with `\srcref{...}`), not a separate section.

## File structure

Every chapter is ONE source file, `<name>-chapter.tex`: the preamble above, then
`\begin{document}`, the opening, the content, and `\end{document}`. There is no separate body
and no wrapper files. Two PDFs come out of it:

- `<name>-chapter-answers.pdf`: complete, with every `\sol{}` block shown.
- `<name>-chapter-questions.pdf`: the same chapter with the solutions left out (blank space
  where each `\sol{}` was).

The switch is `\ifdefined\hidesolutions` in the preamble. Compiling the file normally shows the
solutions. Defining `\hidesolutions` on the command line hides them:

```sh
pdflatex -jobname=<name>-chapter-answers <name>-chapter.tex
pdflatex -jobname=<name>-chapter-questions "\def\hidesolutions{1}\input{<name>-chapter.tex}"
```

Run `reference/build-chapter.sh` (in this skill) from the chapter's folder to build both, 3 passes each, and print error count and page
count per PDF: `bash <skill>/reference/build-chapter.sh <name>-chapter`. The first run copies `mastery-breaks.sty` and the script itself next to the chapter,
so the folder is self-contained afterwards (`./build-chapter.sh <name>-chapter`). The chapter also comes with `<name>-coverage.md` (see pedagogy-cycle.md). `\sol{}` checks `\ifshowanswers` at every
call site, which is what makes one source render both ways. Never split the source into two
files or copy the preamble; a second copy will drift.

## Verification artifact

A throwaway smoke test exercising every macro above (including a genuine forced page break
inside a `theorybox`, confirming `breakable` produces a clean split with no duplicated title,
and confirming a `\workedheading`-marked example inside that same box never visually reads as
a separate floating region) was built and visually verified during this skill's own design.
Rebuild an equivalent smoke test any time these macros change, before trusting them in a real
chapter. A compile-clean macro is not the same as a visually-correct one; both were checked
here, not just the first.
