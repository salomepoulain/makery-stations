# Visual intuition

This skill builds pictures into every chapter. The reader is a visual learner, and the model for the
style is the way 3Blue1Brown builds intuition: start from a picture and a question, let the
formula fall out of the picture, change one thing at a time, and make the reader predict before
they see the answer. Nothing from those videos is copied (the scene code is CC BY-NC-SA and the
figures are theirs). Every figure here is drawn from scratch, in LaTeX, from the chapter's own
formulas. A "watch this" pointer to a video by title is fine, never a copied figure.

## Find the 3Blue1Brown material first

Before drawing anything, look up how 3Blue1Brown teaches the chapter's topics and take the visual idea, drawn again in your own figure. This is a required part of Mode A step 1, and the plan shows the result.

1. **Search.** For each Theory block, or group of neighbouring blocks, run a web search on `3blue1brown <topic>` (topic words of the block, for example "linear transformations", "determinant", "chain rule", "gradient", "eigenvectors", "Bayes theorem"). Open the lesson page on 3blue1brown.com (`https://www.3blue1brown.com/lessons/<slug>`, it carries the written text of the video) with WebFetch. WebSearch and WebFetch may be deferred tools: load them with ToolSearch. If a page cannot be reached, list it as a gap in the plan. Never fill the gap from memory of what a video shows.
2. **Extract.** Per block, write down in your own words: what is drawn, what changes from frame to frame, the question the video asks the viewer, and the wrong picture it corrects.
3. **Turn it into pictures.** The device becomes the Theory figure of the block (a film strip if it moves) and one or more V exercises ("what happens to the picture when ..."). Both use the chapter's own formulas and colours.
4. **Record it.** The coverage file gets a section "Visual sources": one row per block with the video (series and title), the device in your words, the figure in the chapter and the V exercise. A block without a source needs a reason in that row. Every device that fits a block becomes a figure or a V exercise, or is listed as skipped with a reason.

Limits: ideas only. No 3Blue1Brown figure, screenshot, scene code (manim, CC BY-NC-SA) or wording is copied. A "Watch this: series, title" pointer at the end of a Review is fine and welcome, by title.

Starting points, to be confirmed by the search and not trusted from this list: the series "Essence of linear algebra" (linear transformations and matrices, matrix multiplication as composition, the determinant, inverse matrices, dot products and duality, change of basis, eigenvectors), "Essence of calculus" (the derivative as slope and as a nudge, derivative formulas through geometry, the chain rule and product rule), the neural network series (gradient descent, backpropagation and its calculus), and single videos on Bayes' theorem, the Gaussian and the central limit theorem.

## Two jobs for pictures

1. **Figures inside Theory boxes show.** One picture per idea, placed right where the formula or
   definition appears, so the reader sees what the symbols mean. Put it inside the `theorybox`
   (or its `workedbox`), never floating between boxes. Typical: the curve of the density the box
   defines, the area that a probability is, a grid before and after a matrix.
2. **V exercises make the reader predict.** Badge `\Vbadge` (hot pink circle, white letter).
   The reader draws or predicts first, then compares with the picture in the answers PDF. These
   build the feel that an interactive slider would give: what happens to the curve when a
   parameter goes up, down, doubles, or hits an extreme.

Both use the same look, so the reader recognises the picture family. The Theory figure shows one
case. The V exercise asks about a new case of the same family.

## What a V exercise looks like

One number, one theme, 2 to 4 lettered sub-parts, in the same "one exercise, many parts" shape
as plain drills. Question forms that work:

- **Predict the shape.** "Sketch P(K = k) for lambda = 0.5, 3 and 10." Where is the peak, how
  wide is it, what happens to the tail?
- **What changes if.** "The rate doubles. Which way does the curve move, and does its height go
  up or down? Why?" Pair every "what changes" with a one-line reason in the solution.
- **Match.** Three plots and three parameter values. Which plot belongs to which value?
- **Read off.** Read a probability as an area, a mean as a balance point, an MLE as the top of a
  curve, a posterior as a ratio of two areas.
- **Extremes and limits.** What does the picture become when the parameter goes to 0, or to
  infinity? This is where intuition sticks.
- **Spot the mistake.** A wrong sketch is given; say what is wrong and why.
- **Complete the picture.** Half a diagram is given (a Bayes box with two areas filled in); fill
  in the rest and read the answer off it.

Rules:
- Ask about an idea a Theory box has already shown. A V exercise never introduces a new fact.
- Vary one parameter at a time, and keep the axes the same across panels. Comparing curves on
  different axes hides the very change the reader should see.
- Each solution says what the reader should have seen and why, in one or two plain sentences
  next to the figure. A picture alone is not a solution.
- Every paragraph gets 2 to 4 V exercises, placed where a picture teaches something. A paragraph
  gets fewer only when it is purely algebraic or proof-only, and the plan says so with the reason.
  `check-chapter.py` lists every paragraph with fewer than 2. Skip the badge for a proof-heavy or
  purely algebraic block, and never force a picture where it teaches nothing.

## Questions PDF versus answers PDF

The chapter is one source that builds two PDFs, and a V exercise works so that both PDFs show the
same question:

- The **question** always shows labelled axes (same ranges, same grid) with nothing drawn on them,
  in both PDFs. On a printout of the questions PDF the reader sketches on them.
- The **solution** (`\sol{...}`, shown only in the answers PDF) repeats the same figure with the
  curves drawn in, one figure per sub-part, followed by one or two plain sentences on what the
  reader should have seen and why.

Draw each figure once. Define it as a macro, put the curves under `\ifvfill ... \fi`, and switch
the flag on inside the solution:

```latex
\newif\ifvfill                      % in the preamble
\def\pA{\begin{tikzpicture}\begin{axis}[mastery,xlabel={$k$},...]
  \ifvfill\addplot[ycomb,color=vpink,...]{exp(-3)*3^x/factorial(x)};\fi
  \end{axis}\end{tikzpicture}}
...
\begin{center}\pA\end{center}      % question: blank axes
\sol{\vfilltrue\begin{center}\pA\end{center} What to see and why.}   % answer: same axes, curves in
```

Put `\needspace{14\baselineskip}` before the stem so the question starts on a page with room for its
axes (the macro is an exact test, it only breaks the page when less than that space is left). A Match exercise draws the given curves unconditionally and only the asked-for ones under
`\ifvfill`.

This guard covers only the question. The `\sol{...}` box is measured as a whole and made
non-breakable only when it is short (see the `\sol` definition in `preamble-visual.tex`); a V
solution that runs formula, values, features and drawing steps before the figure is usually long
enough to land in the breakable box, and without its own guard the figure itself can start on one
page and finish on the next. Put a second `\needspace` right before the `\begin{center}\pA\end{center}`
inside the solution too, whenever the figure is not the very first line of the solution (size it to
the figure's height plus about 2 lines, for example `\needspace{12\baselineskip}` for the usual
4.9 by 3.6 cm panel). Check this on the rendered PNG of the solution page, not just the log.

## A V solution shows how to get the picture

A finished plot alone teaches little. The solution of a V exercise also shows the working that
lets the reader draw the picture by hand, so they can check their own sketch step by step. Space
is not a concern here. In this order:

1. **The formula** the picture comes from, written out for the case asked.
2. **The values to compute**, as a small table or a short list, with the arithmetic shown: a few
   key points (for a pmf, p(0), p(1), p(2), ... up to where it is negligible; for a density, the
   value at the centre and at one or two widths away; for a likelihood, the value at a few
   parameters).
3. **The features to locate**, each with the one-line reason: where the peak sits and how it is
   found (ratio of neighbouring values, derivative zero), where the curve crosses an axis, what
   it does far away (tail, asymptote), where it is symmetric, whether the total is 1 (bars add up,
   area is 1).
4. **The drawing steps**: mark the points, join or bar them, draw the peak and the tail.
5. **The finished figure** (with `\vfilltrue`), and then one or two sentences on what to see and
   why, and how the picture changes when the parameter moves.

For a series of panels the values are computed for each parameter value, in one table with the
parameter values as columns. If the arithmetic is long, show the pattern for the first value in
full and give the others in the table, with a note that they follow the same steps.

## Formula anatomy: build a formula from its pieces

The most useful V exercise for a formula is a row of panels, one per factor, and then the product,
all on comparable axes. Examples: the Poisson pmf as lambda^k against k!, then lambda^k/k!, then
the pmf (so e^{-lambda} is just the constant that makes the bars add to 1); the Gaussian as the
exponent parabola, then e to the exponent, then the division by sqrt(2 pi); a coin likelihood as
p^6 rising against (1-p)^2 falling, and their product; prior times likelihood equals posterior read
off point by point. Ask the reader to say what each factor does before they see the product.

## Bayes: the box is the default picture

Draw Bayes' rule as a box: the width is the prior, the height is the likelihood, the posterior is
one area divided by the sum of the areas. Ask the reader to draw it for a 30% prior and then a 3%
prior, so they see the thin column. Keep the frequency tree ("out of 10000 people") for the
rare-event case, where the box gets too thin to read.

## Building figures

Only LaTeX, so the one-source rule holds: `pgfplots` for anything that is a formula, plain TikZ
for geometry. No matplotlib, no external image files.

- **Plot the formula, not points typed by hand.** `\addplot {exp(-\l)*\l^x/factorial(x)}`. Then
  the figure cannot disagree with the maths. Discrete distributions use `ycomb` with markers, and
  a continuous density uses a smooth line.
- **Areas that are probabilities** are filled under the curve (`\addplot ... \closedcycle` or
  `fill between`), in the chapter accent colour, lightly.
- **Geometry** (a matrix as a grid transformation, basis vectors, a gradient arrow, a level-set
  picture) uses TikZ with `cm={a,b,c,d,(0,0)}` for linear maps, so the picture is computed from
  the matrix entries.
- **Rare events** (1% sick) make a Bayes area diagram unreadable. Use the frequency form
  (out of 10000 people) as a table or a tree, or draw the box with the small side magnified and
  say so.
- **Colours.** One colour per object, the same in every figure of the chapter (for example the
  likelihood always the chapter colour, the prior always grey, the posterior always pink).
  Hot pink is reserved for V exercises and for what the reader is asked to find.
- **Film strip instead of animation.** A PDF cannot move, so show 3 or 4 frames side by side
  (lambda = 1, 2, 4, 8), same axes, one parameter changing. Keep a strip within one line of the
  page: 3 panels of about 4.9 cm and 3.6 cm.
- **Size and labels.** Small, labelled axes with `\scriptsize` ticks, no titles longer than a
  few symbols, no caption paragraph. The prose in the box already says what the picture shows.
  Turn off ugly scaled tick labels with `scaled y ticks=false`.
- **Where it helps most:** the shape of a distribution and how it moves with its parameters,
  probability as area, likelihood as a curve with a peak, prior times likelihood equals posterior
  as three curves, a matrix as a warped grid, a derivative as a slope or a local linear map, a
  gradient step as a ball on a curve, bias as a histogram whose centre misses the true value.

## Pitfalls found in the first pilot

- **Marker colour on `ycomb`.** `\addplot+[ycomb]` gives blue marker fill. Use
  `\addplot[ycomb,color=vpink,mark=*,mark options={fill=vpink}]` instead.
- **Loops.** A `\foreach` inside an axis breaks `axis cs:\macro`. Put the `\foreach` outside the
  `tikzpicture` and start a new picture per pass.
- **Tick labels.** pgfplots prints labels like 5·10^-2. Add
  `yticklabel style={/pgf/number format/.cd,fixed,precision=3}` to the `mastery` style.
- **Gamma function.** pgfmath has no gamma. For a Beta or Gamma density write the constant by hand,
  `exp(C+(a-1)*ln(x)+...)`, with C computed once in Python from `math.lgamma` and pasted in.
  Check the pasted constant numerically (the density must integrate to 1).
- **Sharing axes.** Likelihoods and densities live on different scales. Scale a likelihood to
  peak 1, or a density to area 1, and say which one in the axis label, so the curves can share
  axes.
- **Match exercises.** See the Match rule above.
- **Layout.** The Theory unit is a stack of sibling boxes (theorybox, workedbox, theorycont) and
  the workedbox is breakable, so a figure inside a worked example can cross a page break. Nested
  breakable boxes do not work in tcolorbox, which is why they are siblings.
- **`\\mid` in options.** Axis options passed through a macro break on `\\mid`. Write `|` in the
  option or set the label outside the macro.
- **Legend space.** The Legend has no spare room for a new badge line. Set the Legend in `\small`
  and drop the item spacing if the V entry pushes it off page 1.

## Template

Preamble additions (they also live in `reference/latex-scaffolding.md`):

```latex
\usepackage{pgfplots}\pgfplotsset{compat=1.16}
\definecolor{vpink}{RGB}{233,30,140}
\newcommand{\Vbadge}{\badge{vpink}{V}}
\pgfplotsset{mastery/.style={width=4.9cm,height=3.6cm,axis lines=left,grid=major,
  grid style={gray!25},tick label style={font=\scriptsize},label style={font=\footnotesize},
  title style={font=\footnotesize},ymin=0,scaled y ticks=false,
  yticklabel style={/pgf/number format/.cd,fixed,precision=3},every axis plot/.append style={thick}}}
```

A V exercise with blank axes in the question and the curves inside the solution:

```latex
\def\pA{\begin{tikzpicture}\begin{axis}[mastery,title={$\lambda=3$},xlabel={$k$},
  xmin=-0.5,xmax=18,ymax=0.65,xtick={0,5,10,15}]
\ifvfill\addplot[ycomb,color=vpink,mark=*,mark options={fill=vpink},mark size=1.4pt,
  domain=0:18,samples=19]{exp(-3)*3^x/factorial(x)};\fi
\end{axis}\end{tikzpicture}}
\needspace{12\baselineskip}
\item[\extag{\Vbadge}] Sketch $P(K=k)$ for $\lambda=3$.
\begin{center}\pA\end{center}
\sol{\vfilltrue\begin{center}\pA\end{center}
The peak sits at about $\lambda$ and ... (what to see and why, one or two sentences).}
```

## Checking a figure

1. Build both PDFs. The questions PDF must show the empty axes, the answers PDF the curves.
2. Render the page to a PNG (`pdftoppm -r 80 -png`) and look at it. Check the axes ranges, that
   nothing is clipped, that the labels are readable and the colours are consistent.
3. Check the key features numerically in plain Python or in `pgfmath`: where the peak is, that a
   density integrates to 1, that the mean sits where the figure puts it.
4. Keep every panel of a film strip on the same axes.
