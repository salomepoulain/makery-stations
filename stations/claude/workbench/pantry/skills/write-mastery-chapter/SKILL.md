---
name: write-mastery-chapter
description: Use when authoring a new theory-then-practice study chapter for any subject as a LaTeX PDF (with figures and predict-the-picture exercises), or when revising a chapter this skill previously produced because a specific section was confusing during study.
---

# Write mastery chapter

Build a study chapter the way a good worked-example-driven mastery textbook does it:
repetition before escalation, understanding over memorization, every new idea earning its
worked example before the reader is asked to reproduce it alone.

## Overview

One core principle governs everything below: **drill the current core skill flat before
escalating, and escalate late and rarely.** See
[reference/pedagogy-cycle.md](reference/pedagogy-cycle.md) for the full cycle this implies
(Theory → Recipe → Worked example → tagged exercises, the P O T D V E C R taxonomy, the
checkpoint-exercise branch, the Review/end-of-paragraph cheat sheet). Read it before authoring
anything. It is the pedagogical spec this skill exists to enforce, not optional background.

**Default scope: full mastery, not compact exam prep.** Unless the user explicitly asks for a
short version, the chapter is allowed to become long. Do not omit prerequisite steps, edge
cases, counterexamples, boring mechanical drills, or hard variants merely to keep the PDF short.
The chapter's structure gives the reader control over what to skip: T/D/V/E are the core path,
C and R are optional depth, Prior knowledge is for prerequisites. Completeness belongs in the
chapter; selectivity belongs in the exercise tags and reading path.

**Drill means one move across many surfaces.** In Full Mastery mode, a Drill exercise is not a
small mixed quiz. It is one named family of the same move, repeated across several nearby
situations until the reader can recognise the move without thinking. A good Drill family may
have four, six, eight or even nine lettered parts when the invariant is stable: same task,
different numbers, shapes, signs, dimensions, zero/identity cases, symbolic versions, or a
near-mistake at the end. Do not satisfy the D row by writing three tiny unrelated questions.
See `reference/pedagogy-cycle.md` for the bad/good Drill examples; follow those examples when
authoring.

**Bridge concepts are Theory, not glue text.** Completeness also means expanding the small
notation and algebra bridges that make source questions learnable from the baseline. Matrix
shapes, entries, transposes, Sigma notation, matrix products, Kronecker deltas, scalar-transpose
facts, inverse assumptions, definiteness checks and convention translations should become their
own Theory blocks when the chapter relies on them. Do not hide them inside one dense block to
make the outline shorter.

**Turn hidden steps into teachable moments.** Do not treat Theory blocks as mathematical
encyclopedia entries. Treat them as learner obstacles being removed. When a source question needs a
notation habit, shape habit, convention, tiny algebra trick, or common wrong-move correction, teach
that habit before the source question uses it. Reused habits usually deserve their own Theory
block; one-off tripwires can be a named teaching beat inside the current Theory block, with a tiny
example, shape check, or counterexample.

**No compression by hiding skills.** A topic may be compressed only after an explicit
compression audit: list the skills being merged, the first place each is used, the exercises
that drill it, and the edge cases still covered. If a merged block would contain two genuinely
new moves, split it. A mastery chapter should feel like a careful staircase, not a summary with
practice attached.

The exact LaTeX this produces (colors, box structure, numbering, provenance markers,
cross-reference hyperlinks) is fully specified in
[reference/latex-scaffolding.md](reference/latex-scaffolding.md). Follow it exactly, this is
not a style suggestion, it's the house style contract. A chapter that reads well but uses
different macros or colors has not followed this skill.

Two standing assumptions apply to everything authored, both spelled out in
`reference/pedagogy-cycle.md` under "Baseline knowledge": the reader knows only the baseline the
course or user has named, plus what earlier chapters of the same course taught, and nothing
else; the reader needs a hand on every single step. Prior knowledge is everything the chapter's
theory builds on from that baseline or from an earlier chapter, and gets extra drilling, never
less.
Do not put new chapter material into Prior knowledge just because it is convenient to introduce
early. If a concept is not already known from the baseline or an earlier chapter, it gets its
own Theory block in the numbered chapter.

**Design system.** The finished pilot defines the look of the chapter: the margin pills, the headers, the Contents with
clickable pills, the short Legend, breakable solutions, source tags in the margin. Read
[reference/design-system.md](reference/design-system.md) and copy `reference/preamble-visual.tex` as the preamble. Where
`reference/latex-scaffolding.md` disagrees with them, the design system wins.

**Opening contract.** The opening is not just "use the right macros"; it must use the house
order and the house plumbing. The first visible pages are title/introduction plus Contents on
page 1, the same locked Legend page starting on page 2, then Prior knowledge. The Legend is not
authored per chapter: copy the project's `reference/legend-template.tex` verbatim into the
chapter body after the Contents. This template may contain project-local example labels; preserve
them unless the user deliberately creates a new locked template for a different course or
project. Then start `\begin{priorsection}\priortitle` and immediately add
`\addtocontents{toc}{\protect\dcrowflat{0}}`. That last line is what puts the Prior-knowledge
pills into the Contents; omitting it is a structural bug, even if the chapter compiles.

**Visual intuition.** Every chapter has figures and a pink `V` exercise type that makes the reader
predict a picture before seeing it. Read [reference/visual-intuition.md](reference/visual-intuition.md)
before authoring: it says where figures go, what a V exercise asks, how the questions PDF shows
empty axes while the answers PDF shows the curves, and how to build and check a figure.
For any idea that has a visual, geometric, tabular, computational-graph, timeline, state-machine,
number-line, flow, contour, or before/after representation, put that representation inside the
Theory block before or beside the abstraction. If the subject is abstract, make the visual from
a small concrete instance: a table, diagram, trace, grid, annotated expression, or dependency
graph. A V exercise later is not a substitute for visualizing the Theory itself.

**REQUIRED SUB-SKILL:** run `humanize` on every piece of authored prose as the last step of any
invocation, in either mode. No em dashes, no AI-tell phrasing. Run it after the content is
correct, never before: it should polish the prose, not change meaning or math.

## What this skill produces

Everything for one chapter goes into its own subfolder of `lessons/` in the project root (`<project root>/lessons/`, not
inside `.vault/`). Create `lessons/` if it does not exist. The subfolder's name is the chapter's own base name, the same
string every file in it starts with, so the folder and its files always read as one unit:
```
lessons/
  <course>-chap<N>-<topic>-chapter/
    <course>-chap<N>-<topic>-chapter.tex             the only source: preamble, content, Legend, Contents, Summary, Diagnostic check
    <course>-chap<N>-<topic>-chapter-answers.pdf     with every solution
    <course>-chap<N>-<topic>-chapter-questions.pdf   without solutions (blank space where they were, empty axes on V exercises)
    <course>-chap<N>-<topic>-coverage.md             inventory of the input material and one row per source question part
    build-chapter.sh, mastery-breaks.sty             copied in by the first build, so the folder builds by itself
    (per PDF: .aux .log .out .toc                    build leftovers, safe to delete)
  <course>-chap<M>-<other-topic>-chapter/            the next chapter of the same course, its own subfolder the same way
    ...
```
The chapters of one course sit side by side as subfolders of `lessons/`, so the "find the earlier chapters" search in
Mode A step 1 looks for `lessons/<course>-chap<M>-*-chapter/<course>-chap<M>-*-chapter.tex` (M < N). Course-level files that
span more than one chapter (a division plan, a shared study note) go directly in `lessons/`, not inside any single
chapter's subfolder. Only if the user names a different location, use that one.
Figures are pgfplots code inside the `.tex`, so there are no image files. The chapter needs a TeX Live with `tcolorbox`, `pgfplots`, `enumitem`, `microtype` and
`hyperref` (see the Dependencies section of `reference/latex-scaffolding.md`). Build with
`bash <skill>/reference/build-chapter.sh <course>-chap<N>-<topic>-chapter` from inside the folder; it copies `mastery-breaks.sty` and itself next to the chapter.

## Which mode

- No chapter exists yet for this subject, or the user wants one written from scratch →
  **Mode A: author a new chapter**.
- A chapter this skill already produced exists, and the user is pointing at a specific passage
  that confused them (a quote, a screenshot, a description of "this part") →
  **Mode B: confusion-driven update**.

If genuinely unclear which applies (e.g. the user wants both a new topic added to an existing
chapter *and* a specific passage fixed), ask instead of guessing. These two modes have
different gates and a different blast radius.

## Grounding dispatch

Before authoring or rewriting any technical content (a formula, a definition, a claim), check
it's actually correct. If the target project has a vault (a `.vault/` folder, or similar
knowledge base), dispatch a `general-purpose` agent: find and read the vault's own schema file
first, check for existing coverage there before falling back to a web search, and report back
findings/sources/gaps. Restate this guardrail verbatim in every such dispatch:

> This pass is read-only. The agent must never write, move, or delete anything in the vault or
> in any project file. If it finds something worth permanently recording, it reports that as a
> gap for a separate, deliberate follow-up. It does not act on it itself.

For a quick fact-check mid-authoring, use the same dispatch with a narrower question instead of
a broad topic.

## Mode A: author a new chapter

**Language.** Write the chapter's own prose (titles, Legend, Theory, worked examples, exercises,
solutions, Reviews, Summary, Diagnostic check, figure and axis labels, source tags) in the
language the course's own input material uses (its lectures, homework, exams), not the language
of the user's chat request. Names of curricula, exams, institutions and source files stay in
their own language as proper nouns. If the input material is not clearly all in one language,
ask.

1. **Ground the subject and take inventory.** Grounding dispatch (above) on the subject matter itself: what are
   the real first principles, standard framings, common gotchas. Ask the user which folders hold the input material
   (homework, practice sets, past exams, lecture notes, summaries) unless they already said, and also look in the project's vault for the
   subject. **List every file** in those folders and **open every one completely** (a PDF page by page, nothing skimmed). Record file, type, page count and number of
   question parts. Check [examples/](examples/README.md) too. The input material is the highest-signal source for which edge cases actually matter,
   more useful than a generic treatment of the topic. Anything not opened is reported as a gap, never silently skipped.

   **Find the course dependency baseline.** Before deciding Prior knowledge, search `lessons/`
   for course-level planning or baseline files such as `<course>-dependency-baseline.md`,
   `<course>-chapter-division.md`, `<course>-*-chapter-estimate.md`, or similarly named files.
   Read the relevant ones and treat them as the project-local source for the named baseline.
   The skill remains generic; the course repository states what the baseline is.

   **Find the earlier chapters.** Prior knowledge builds on the previous chapters of the same course, so before planning, look for them. Work out this chapter's
   number N (from the request or the file name), then search the project for chapters M < N of the same course: `<project root>/lessons/`, the vault, and
   the file name pattern `<course>-chap<M>-*-chapter/<course>-chap<M>-*-chapter.tex` (see "What this skill produces" above). Read every one you find (its Theory titles, its Review terms and formulas, its Summary): that is what the
   reader has already been taught and may be used without teaching it again. Record them in the inventory (chapter, file, Theory letters and titles). If N > 1 and no earlier
   chapter is found, ask the user whether earlier chapters exist elsewhere before assuming none do. Chapter 1 has no earlier course chapter, so its Prior knowledge comes only from the named baseline.

   **Study exemplars for method, not content.** If the user points to a previous chapter or PDF
   whose pedagogy or visuals they like, inspect it and extract reusable method patterns: how
   Theory moves from concrete picture to formula, how exercises escalate, how edge cases are
   surfaced, and how the Diagnostic check mirrors the chapter. Do not copy subject-specific
   claims unless they are part of the current subject and independently grounded.

2. **Draft a plan and present it in chat**: a paragraph-by-paragraph (`§1`, `§2`, ...) outline,
   each paragraph's Theory-block breakdown, and a rough exercise-tag count per block (how many
   plain items, whether an R/A/D shows up, whether a Prior-knowledge block is needed first).
   The default plan is a **Full Mastery** plan. It must include all in-scope source material and
   all prerequisite bridges needed to make that material learnable from the baseline. A compact
   plan is allowed only when the user explicitly asks for a compact chapter.
   Also give the **dependency list**: for every Prior block, its source (the named course baseline, a baseline reference file when available, or the earlier chapter and its Theory letter,
   which you found and read in step 1) and the Theory blocks
   or exercises that use it before the chapter teaches it. A skill that nothing depends on is not Prior knowledge, and a skill the
   chapter teaches itself is Theory (see "What Prior knowledge is" in `reference/pedagogy-cycle.md`).
   Give an **edge-case and variation map** per Theory block: ordinary case, smallest nontrivial
   case, shape/type/domain boundary, zero/identity/empty or constant case where relevant,
   symmetric/degenerate/singular or non-invertible case where relevant, sign/corner/limit case
   where relevant, and one common wrong move the chapter will explicitly inoculate against.
   Irrelevant categories may be marked "not applicable"; unmentioned categories are treated as
   unplanned, not implicitly absent.
   Also say, per paragraph, which Theory blocks get a figure and which get a V exercise, and how many V exercises the paragraph has
   (2 to 4, fewer only with a stated reason; see visual-intuition.md). For every block give the 3Blue1Brown source of the picture
   (the search step "Find the 3Blue1Brown material first" in visual-intuition.md, done during step 1) and write the "Visual sources" table into `<name>-coverage.md`.
   Also state the **Theory visual hook** for every Theory block: the concrete picture, table,
   graph, diagram, trace, or tiny example that appears inside the Theory before the general
   formula. If a block truly has no meaningful visual hook, say why and include a concrete
   nonvisual representation instead.
   Also give the Theory-block count per paragraph, and cut paragraphs by topic (see "Where to cut
   a chapter into paragraphs" in `reference/pedagogy-cycle.md`; the sizes there are a guideline).
   If the subject is clearly built on the target project's existing material, say what it
   connects to and why.
   Also list every question part in the input material and mark it in scope or out of scope, with a reason for each out of scope (the chapter or topic it belongs to).
   Every in-scope part must end up in the chapter, in its own wording, with a solution that
   matches the source solution's method and result (see "Source questions and solutions are
   mandatory" in `reference/pedagogy-cycle.md`). Put the inventory and this coverage list in the plan, and write them to `<name>-coverage.md` next to the chapter.
   Include a **no-omission declaration**: what would normally be tempting to skip, where it is
   taught instead, and which optional tag lets a rushed reader skip it without removing it from
   the chapter.

3. **Stop and wait for the user's explicit go-ahead before writing anything.** Do not start
   Mode A step 4 until they confirm the plan. This is a hard gate, not a formality. The plan
   is cheap to redirect; 40 pages of LaTeX is not.

**Supervised authoring: steps 4 to 8 are not one unsupervised dispatch.** Once the plan is approved, whoever is running
this skill (the main conversation, or an agent it dispatches to write) stays the orchestrator for the whole build and
checkpoints after every paragraph, even when the user has waived the step-3 plan gate for that run or asked for it to run
straight through without asking again. A single subagent authoring 40 to 200 pages unattended, however good its
instructions, drifts: it satisfies whatever is checked by a script and quietly lets whatever isn't checked slide,
especially the plain-English rules that have no automated check (a chapter authored this way once shipped with a third of
its Drill exercises and a Legend that silently reverted to a stale, wrong template, both invisible until someone actually
opened the PDF). The fix is not to trust the instructions harder, it is to look at the output before it compounds:

- Dispatch (or resume) the authoring agent one stage at a time: the opening (title, Contents, Legend, Prior knowledge),
  then one paragraph at a time. Tell it to build and report after each stage, per step 5 below, exactly as it already does
  for its own progress log.
- After **every** stage, the orchestrator itself (not a claim from the subagent's report) runs
  `reference/check-chapter.py` on the chapter so far and reads all of its tables: EXERCISE RUN per Theory block (every
  block just added needs D >= 3, per "Exercise taxonomy" in `reference/pedagogy-cycle.md`; a block under that is not
  finished, send the same stage back before moving on), VISUALS per paragraph, THEORY BLOCK DENSITY, and LEGEND STRUCTURE.
  A flag anywhere is not a note for later, it is the same stage's work, unfinished; resolve it before dispatching the next
  stage, the same way a real editor reviews a chapter before the next one is drafted, not after the book is bound.
- After the **opening** stage specifically, render the Contents and Legend pages to PNG and read them, don't just trust
  `LEGEND STRUCTURE`'s text-level check. They are written once and never touched again, so a mistake here silently
  affects every later stage.
- After each **paragraph** stage, render and read at least one Theory box, the exercise run of one block, and one V
  exercise's question and solution pages, the way step 7 below describes for the finished chapter, just done per stage
  instead of only at the very end.
- After each **paragraph** stage, run a completeness review against the plan's edge-case and
  variation map. Every edge case promised in the plan must be either taught, drilled, placed in
  C/R, or explicitly deferred to a named later chapter. Do not silently drop edge cases to keep
  the chapter short.
- Only once a stage passes all of this does the orchestrator dispatch the next one. This costs more of the orchestrator's
  own attention than firing one long instruction and waiting, that cost is the point: it is what catches a thin block or a
  reverted template while it is a five-minute fix instead of a full rewrite.

4. **Author one file**, `<name>-chapter.tex` (one source, two PDFs: with and without
   solutions, see "File structure"), exactly per
   [reference/latex-scaffolding.md](reference/latex-scaffolding.md)'s file structure and macro
   set, exactly per [reference/pedagogy-cycle.md](reference/pedagogy-cycle.md)'s cycle and
   presentation convention. Name the file `<course>-chap<N>-<topic>-chapter.tex` (for example
   `ml1-chap1-mvcalc-chapter.tex`), with the chapter number right after the course prefix, so the
   files sort in chapter order. If the target project already has a different chapter naming
   convention (check its vault/docs for other chapters this skill or a
   predecessor produced). Every chapter opens with the title, Contents, locked Legend and Prior
   knowledge in the house order;
   see latex-scaffolding.md's "Required opening" section for the exact structure.

   Author to full mastery depth by default. For each Theory block, include a concrete setup,
   the visual or structural intuition, the formal statement, a worked example with every move
   shown, then the T/D/V/E/C/R run. Challenge exercises are not decorative: they protect edge
   cases, unusual framings and common traps. A chapter with no Challenge exercises needs an
   explicit user-approved reason.

5. **Compile and verify.** Build both PDFs with `reference/build-chapter.sh` (it also lets LaTeX find `reference/mastery-breaks.sty`; three `pdflatex` passes each: hyperref
   needs a second pass to resolve labels, and the table of contents needs a third to reflect page
   numbers that shifted once it was inserted). Confirm zero errors (`grep -c '^!'` the log). Confirm no
   undefined references. Render figure pages to PNG and look at them, in both PDFs. If `tcolorbox`/`hyperref` aren't installed in the target environment,
   see the Dependencies section of `reference/latex-scaffolding.md` for the
   `tlmgr --usermode install` fix. This is a known, solvable hurdle, not a reason to fall back
   to a different box design.

   **Check the Contents fits on page 1** (design-system.md's "Page 1 holds the title, the introduction and the Contents in
   full"), every time, not only for a long chapter: `pdftotext -layout -f 1 -l 1 <name>-chapter-answers.pdf -` and read off
   the page number printed after "Legend" in the Contents listing. It must say 2. Any other number means the Contents
   spilled onto page 2, shorten the introduction per design-system.md's order and rebuild before moving on.

6. **Check the breaks** (rules in `reference/design-system.md`, "Line and page breaks"). In the questions PDF, scan every page break:
   an exercise intro alone at a page bottom, a single part alone at a page top or bottom, a Theory paragraph cut in the middle, a solution
   separated from its part. Look at `Overfull \hbox` in both logs: each one is a long inline formula, turn it into a display. Grep the log for `has no \newterm`: every `\tm` key must be a term introduced in the Theory.

7. **Visually spot-check the actual PDF**, not just the compile log: box seams (Theory and
   Worked example should read as one continuous region with a subtle tone shift, not a visible
   gap), any page break that lands inside a box (should be clean, no duplicated title), that
   cross-reference hyperlinks actually resolve to the right place, and that the Contents (on the title page) lists every `\frontsection` (Legend, Prior knowledge,
   Summary, Diagnostic check). Also count plain exercises per Theory
   block; fewer than 3 means go back and add more before calling a block finished, per
   `reference/pedagogy-cycle.md`.

   Then run the checks: `python3 <skill>/reference/check-chapter.py <name>-chapter.tex <name>-coverage.md`. It lists the solutions that are too short for their
   type (see "Solutions: how extensive" in `reference/pedagogy-cycle.md`: extend them or justify them) and checks the coverage file against the chapter: every
   in-scope source question part appears, in its own wording, and each solution was compared against the source solution.
   Also read the Summary and Diagnostic rows in the rendered Contents. The Summary must show
   the Theory-letter snake, and the Diagnostic check must show its number pills. The Diagnostic
   must mirror the chapter: at least one group per numbered paragraph, with fresh questions
   covering the paragraph's core skills and at least one mixed/capstone group when the chapter
   culminates in source-style or exam-style problems.

8. **Humanize pass** (see Overview) on the authored prose.

9. Report back to the user for judgment. Don't declare success yourself: a clean compile is
   necessary, not sufficient.

## Token-efficient authoring exception

When the user asks for a token-efficient run, checkpoint the opening and then batches of
two or three numbered paragraphs. Use a one-paragraph checkpoint only for unusually risky
material or when the user requests it. After each batch, report only changed files, counts,
hard failures, and unresolved questions, in at most ten lines.

Run the checker after each batch, but show only its summary: exercise and visual counts,
Theory density, opening/Legend status, source-label count, and coverage failures. Treat
missing labels, missing Theory hooks, too few Drill families, malformed structure, coverage
failures, and LaTeX errors as blockers. Treat short-solution listings as review signals:
always fix bare answers and incomplete E/C/Diagnostic arguments, but do not mechanically
pad a compact atomic Drill or shape answer that already states its reason and result.

Render Contents and Legend once after the opening, one Theory page and one V question/solution
pair per later batch, and a selected-page final spot-check. Do not render every page unless
an automated check reports a layout problem. If the user explicitly allows a multi-page
Contents, verify its order, readability, and links instead of forcing it onto one page.

## Mode B: confusion-driven update

A concrete procedure, not vague guidance. This is exactly what manual, successful fixes to a
chapter's source look like in practice:

1. **Locate the exact source location.** From the user's pointer (a quote, a screenshot, "the
   part about X"), grep the chapter body for the nearest heading/label or distinctive phrase,
   then read that section directly to confirm you've found the right spot before touching
   anything.

2. **Classify the confusion into a concrete repair.** Don't default to "explain it better in
   chat"; the fix belongs in the source, so the next reader doesn't hit the same wall:
   - A fact or step was *used* but never *established* → promote it into a proper new Theory
     subsection, built up from a concrete case, not asserted mid-derivation. (For example, a
     derivation leans on "a scalar equals its own transpose" without ever having shown it.
     The fix is a new Theory block deriving that fact from a 1×1-matrix argument, not a
     one-line parenthetical.)
   - A derivation jumped steps → expand it into more `align*` lines, one atomic move per line,
     per the presentation convention.
   - A prerequisite is missing → add a `refreshbox` (pale yellow, amber P badge) with a concise
     recap plus a `\Pbadge` exercise, right before its first use in the paragraph. If the gap is
     big enough that a recap would not do, extend the opening Prior knowledge section instead.
     Anything that is genuinely new material gets a full Theory block, not a refresher.
   - A Worked example is hard to follow because it's doing too much at once → split it: end
     the first stage, write `\workedheading` again with "Worked example (continued)" for the
     next stage, still inside the same `theorybox`, rather than cramming a multi-stage
     derivation into one dense block. (`breakable` handles page-length overflow automatically,
     so this split is about *clarity*, not page fitting.)
   - Something was introduced with no motivation ("why are we even doing this") → add the
     motivating sentence or two before the Theory box, or fold it into the box's own opening,
     not as a floating unstyled paragraph between boxes. Floating prose outside any box is
     itself a smell; every explanation lives inside a box.

3. **Gate structural changes, not small ones.** Inserting a new Theory block or Prior-knowledge
   subsection reflows the `\exnum` stream after it, so confirm the plan with the user first, the
   same way Mode A gates before writing. A small in-place expansion (more `align*` lines, an
   added sentence) doesn't need a gate, just do it.

4. **Edit the `.tex` source directly.** Never respond with only a chat explanation when the
   confusion is about chapter content. The explanation belongs in the file future readers
   (including a future you) will actually read. Note that `\secref`/`\thyref` links elsewhere
   in the chapter stay correct automatically after an insertion, since they're symbolic labels,
   not hardcoded numbers.

5. **Rebuild both PDFs** with `build-chapter.sh`, confirm zero errors.

6. **Humanize pass** on the new/edited prose.

7. Confirm the fix addresses what was actually asked, briefly, without re-explaining the whole
   section back to the user. They asked about one spot, not a summary of the chapter.
