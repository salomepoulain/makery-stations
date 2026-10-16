# The pedagogy cycle

A subject-agnostic distillation of a worked-example-driven mastery method: every new idea gets
a short derivation, an explicit recipe if it's procedural, a fully worked example phrased
exactly like the exercises that follow, then exercises that ramp in difficulty and are tagged
by cognitive purpose, not just by number.

This is adapted from an existing analysis of a real, published mastery-mathematics textbook.
That analysis lives at `.vault/wiki/summaries/ml1-getal-en-ruimte-exercise-pedagogy.md` in the
project this skill was first built in, if you want the full source-book evidence behind each
rule below. The rules themselves don't depend on that source and apply to any subject.

## Baseline knowledge and ground-up notation

The one assumption this whole method rests on: **the reader knows Dutch VWO
mathematics (wiskunde B) and what the earlier chapters of the same course taught, and nothing else.** Read that as Dutch VWO mathematics, wiskunde B: algebra and equations, functions and their graphs, powers, exponential and logarithmic functions, trigonometry, differentiation with the product, quotient and chain rule, basic integration, and geometry and vectors in the plane. It does not include matrices, partial derivatives, series, or probability and statistics, so those are taught in the chapter's own Theory (see `vwo-wiskunde-b.md` for the list). If you are not sure a topic is in that
course, it is not assumed. Treat it as new and teach it. That is the floor. Don't re-derive
anything at or below it in the body of the chapter, and don't assume anything above it either,
not even material that feels "obvious" or "standard" in the subject. If it's past that floor,
it's new to this reader until this chapter has introduced it.

**Write for a reader who needs a hand on every step.** Assume the reader is bright but has
never seen this material and gets lost easily. Never write "clearly", "obviously", "it follows
that" or "one can show". Never skip a line of algebra because it is easy. Say why each step is
allowed, in one plain sentence, the first few times a move appears. Spell out every
substitution. Restate a definition when it is used again after a gap, in a short clause. When a
result is surprising or a step is a common trip-up, stop and say so. If you catch yourself
thinking "the reader can fill this in", write it out. Too much help costs the reader a few
lines. Too little costs them the whole block.

**What Prior knowledge is.** Prior knowledge is everything the rest of the chapter's theory builds on, and nothing more. It has two sources: concepts
from **wiskunde B** (the list in `vwo-wiskunde-b.md`) and concepts from **earlier chapters** of the same course. It is found by dependency, not by
topic: go through the chapter's Theory blocks, worked examples and exercises, and every skill that is *used before this chapter teaches it* is Prior
knowledge. A skill that this chapter teaches itself (for example tanh, the sigmoid and the ReLU, which are not wiskunde B) is new material and goes in
the Theory, not in Prior knowledge. Earlier chapters are not repeated wholesale: only the concepts this chapter actually reuses, and they may come from
any earlier chapter, not only the previous one. Chapter 1 has no earlier chapters, so its Prior knowledge is wiskunde B only. **Earlier chapters are looked up, not assumed:** find and read the project's
earlier chapters of the same course (`<course>-chap<M>-*-chapter.tex`, M below this chapter's number) and take what they taught from their Theory titles and Reviews. A block
from an earlier chapter carries a pointer, `\priorfrom{Taught in chapter M, Theory X}`.

**Prior knowledge gets more drilling, not less.** The opening Prior knowledge section is where
the floor above is made fluent, so it is the one place where extra exercises are always welcome.
Cover every skill that the chapter's Theory builds on, one Prior block per skill, and give
each one a generous set of drills: several plain exercises, each with 5-8 lettered sub-parts,
plus a checkpoint. When unsure between adding a drill and leaving it out, add it.

Everything above that floor gets built from the ground up, piece by piece, with no exceptions.
Any new term or notation this chapter introduces (a symbol, an operator, a name for a concept,
a convention the reader hasn't seen before) gets its own Theory section before it's ever used
in a derivation, an exercise, or another Theory box's prose. Never introduce a symbol or a term
by using it and letting the reader infer its meaning from context; that's exactly the kind of
ungrounded assertion the presentation convention below exists to prevent. If a later Theory
block needs a new piece of notation to even state its result, that notation earns its own
preceding Theory block first, however small (a short definition and one concrete example is
enough; it doesn't need a full exercise run of its own). This is what "ground up" means in
practice: nothing appears on the page before the reader has been handed the piece it's built
from.

**Make every first appearance visually obvious.** The first time this chapter uses a new term
or symbol, wrap it in `\newterm{...}` (bold, colored, defined in
`reference/latex-scaffolding.md`) and explain it in plain language right there, not just a
formal definition. Every subsequent use of that same term is ordinary text, no styling; the
point is to mark the single moment a reader needs to stop and actually learn something new, not
to decorate the word everywhere it appears. If a term never gets a `\newterm{...}` moment
somewhere in the chapter before it's used, that's a sign the ground-up rule above was broken
and a Theory section is missing.

## Solutions: how extensive

Every solution is written for a reader who needs a hand on every step. A solution is never a bare answer, in any exercise type. The standard:
1. **Name the rule or fact** that is used, in words ("product rule", "the inner sizes must match").
2. **Substitute** the given numbers or expressions into it, visibly, before any simplifying.
3. **One atomic move per line.** Each algebra or arithmetic step gets its own line (an `align*` line or a list item). The first few times a move appears, say in
   one plain sentence why it is allowed. Never combine two moves in one line, and never write "similarly" or "the rest is the same": every part gets its own
   working.
4. **State the result** in words as well as symbols, and where it is cheap add a check (substitute back, compare shapes, evaluate at a point).
5. **Say where the mistake usually is** when a step is a common trip-up.

Minimum by type (a floor, not a target; when unsure, write more):
- **O, T, Prior**: rule, substitution, every step, result. At least 2 to 3 lines even for a short exercise.
- **D (drill)**: rule, substitution, result. A part with more than one move shows each move on its own line. A part with one move (for example "give the
  shape") still gives the reason in a sentence.
- **E, C**: the full argument, every step on its own line, the result and a check.
- **R**: a complete explanation in sentences, with a small example when it helps.
- **V**: how to get the picture (the key points, the slope, the shape) and then the picture.
- **Diagnostic**: like E, and for a homework question the same route as the source solution.
- **Worked example**: the model for all of the above. Steps are numbered in the text ("Step 1", "Step 2") and every display line is on its own line.

`reference/check-chapter.py` measures every solution and lists short ones per type. Run it
before reporting, but treat the list as a review signal rather than a character-count target.
Inspect every bare answer, every E/C/Diagnostic solution that omits a required step, and any
block whose median Drill answer is a bare line. A compact atomic Drill or shape answer is
acceptable when it states the rule or reason and gives the result; do not pad it mechanically.

## Source questions and solutions are mandatory, not optional

If the project provides example material for the subject (homework sets, practice sets, past
exams, lecture exercises, with or without solutions), every question in it that falls under the
chapter's learning goals **must appear in the chapter. No exceptions, no "covered in spirit".**
Before writing, list every such source question part by part and mark each as in scope
(same topic as one of the chapter's Theory blocks, or a step toward one) or out of scope (a
different topic, e.g. it belongs to another chapter). Every in-scope part goes in. Nothing in
scope may be dropped because it seems redundant with a drill you wrote yourself.

- **Wording.** Use the source question's own wording and its own part letters, verbatim or with
  only the changes needed to compile. Tag it with `\srcref{...}`. Place it where its Theory
  block has been taught, as an exercise of the normal cycle. Homework-set questions that the
  chapter builds toward also go verbatim into the Diagnostic check.
- **Solutions.** When the source has a solution, the chapter's own solution must match it well
  enough that a reader comparing the two sees the same method, the same key steps and the same
  final answer, in the same notation. Add more intermediate lines (this method always
  spells out more) but do not change the route, and do not present a different final form
  without saying it is the same thing. If your derivation disagrees with the source solution,
  find out which is right and say so.
- **No source solution** (for example a homework set with no official solutions): write your
  own, and check it numerically where you can.
- **Inventory first.** Before choosing anything, list every file in the input folders the user names (and in the project's vault folders for the
  subject), open every one completely (PDFs page by page, nothing skimmed) and record the file, its type, its page count and the number of question parts in it.
  A file that was not opened is a gap, and it is reported as one.
- **Audit.** Every chapter comes with a coverage file, `<name>-coverage.md`, next to the chapter: the inventory, then one table row per source question part
  (`| source part | in or out | where in the chapter | solution compared | reason |`). The first cell is the label used in the chapter's `\srcref{...}`. An
  out-of-scope row needs a reason that names the chapter or topic it belongs to, "seems redundant" is never a reason. `reference/check-chapter.py <name>-chapter.tex
  <name>-coverage.md` checks every in-scope row against the chapter and every chapter label against the table. A missing row or a listed problem means the chapter is
  not finished.

## The core design principle: repetition before escalation

This is the piece to treat as central, not as one entry in a taxonomy. It holds at every scale:

- **Within a single exercise**: sub-parts (a) through (f) are near-identical in structure, not a
  progression: same move, different numbers. Pure repetition before anything changes.
- **Within one Theory block's exercise run**: a checkpoint exercise (repeats the Worked
  example's exact task) → 3-6 plain exercises (same task, numbers vary) → only then a capstone
  and a harder-framing exercise. The difficulty jump is backloaded to the last item or two of
  the run, not spread evenly across it.
- **Within the chapter**: a "Prior knowledge" block exists specifically to re-drill a
  skill the theory builds on (from wiskunde B or an earlier chapter), with heavy repetition, before a single unit of new content is introduced.
  Nothing new is taught until the old is fluent.
- **Across the whole chapter/course**: a closing interleaved-review set, placed after every
  paragraph, mixes the now-familiar core skills across topics instead of introducing anything
  new. At that scale, escalation comes from combination and context-switching, not harder
  mechanics.

Get the core skill drilled flat first, escalate late and rarely, and let mastered material come
back later as the "given" for something harder rather than disappearing once it's been tested
once.

In practice, this means a Drill exercise should often look boring at first glance and powerful
after doing it. It is not a mixed quiz. It is one move explored across several nearby
situations, so the reader's eye learns what stays invariant while the surface changes. The
sub-parts should feel like "same muscle, new surface": different numbers, different dimensions,
a zero or identity case, a sign change, a symbolic version after numeric versions, a reversed
case near the end, or a near-mistake that exposes a common misunderstanding. If the parts look
interesting because they are all different tasks, the drill is probably wrong. If they look
almost the same but each removes one possible misunderstanding, it is doing its job.

## The paragraph cycle

A paragraph (`\parasection`) is a sequence of lettered Theory blocks, each followed by its own
exercises, closed by a Review. A Theory block is the actual repeating unit:

1. **Theory [letter]: [name]**, a short derivation or definition, usually starting from a
   concrete case before stating the general rule. Live inside one merged box (Theory + Recipe +
   Worked example) per `reference/latex-scaffolding.md`; never split these into visually
   separate colored regions.
2. **Recipe** (only for procedural content, not every block), a numbered, imperative step list,
   nested inside the same box. This separates *why* (the Theory prose) from *how* (an algorithm
   you can follow without re-deriving it).
3. **Worked example**, immediately after, no exceptions. One fully worked example, phrased with
   the exact verb and format the upcoming exercises use, solved step by step. The example is a
   template for the exercise, not just a demo.
4. **Exercises**, tagged (see taxonomy below), increasing in difficulty within the run.

Diagrams, worked micro-steps, and warnings that support a Theory block live inside that same
box (see "Callouts" below), never as a separate floating box between it and its exercises.

## How much goes in one Theory block

A Theory block states and derives one named claim, not everything the paragraph eventually needs
about the surrounding topic. The test is the same one used for paragraphs, one level down: can
you name the block in four or five words, and would a second named concept sitting in the same
box make the reader ask "wait, why is this here too?" A block that states the Jacobian and also
works out the gradient, the directional derivative and contours has picked up three claims, not
one; each of those gets its own block, right after the one it follows from.

Small bridge concepts count as real claims. Do not compress a notation, object shape, algebraic
convention, or visual model into a parenthetical just because it feels small to the author. If a
student must learn it before the source question makes sense, it usually gets its own Theory
block, worked example and drills. In ML/math chapters, common bridge concepts include reading
matrix entries and shapes, transposes, Sigma notation, matrix-vector products, matrix-matrix
products, Kronecker-delta filtering, the fact that a scalar equals its transpose, local linear
maps and Jacobian shape, inverse-matrix assumptions, positive definite versus semidefinite, and
row/column convention translations. These are not filler; they are the bridge from the named
baseline to the course's notation.

Pedagogically, the rule is not "make a new block for every small mathematical fact." The rule is:
turn hidden steps into teachable moments. A Theory block is a learning step, not an encyclopedia
entry. Before writing one, name the obstacle it removes for the reader: the notation habit, shape
habit, convention, visual model, or recurring wrong move that would otherwise make a source
question feel like magic. If that habit will be reused across the chapter, teach it as its own
Theory block. If it only prevents one mistake inside the current claim, keep it inside the current
Theory block as a named teaching beat: a tiny example, shape check, counterexample, or "wrong move"
paragraph followed by a little practice.

Use the source questions to find these moments. If a source solution uses a step such as "this
quantity is a scalar, so it equals its transpose," "differentiate one component and then assemble
the Jacobian," "the row/column convention changes the shape," or "positive definite Hessian means
minimum," the chapter must teach that habit before the source question asks for it. It may be a
full Theory block or a teaching beat inside the block that needs it, but it cannot appear for the
first time inside the solution to the source question.

Write Theory titles as learner actions when possible, not as encyclopedia headings. Prefer titles
like "Put every partial derivative in the right slot," "See why \(A+A^\top\) appears," or "Check
when a stationary point is a minimum" over titles that only name a broad object. The title should
make clear what the reader can do after the block that they could not do before.

Ballpark for a single-concept block: under about 350 words and one figure. A block that reaches
roughly double that, or that ends up with two or three figures for two or three different things
being shown, has almost always picked up a second claim. Split it there, in the same paragraph,
rather than trimming sentences to force it back under the line: the point is one idea per box,
not a word count. A worked example that needs two short parts to show a contrast (for example,
the same map estimated then compared with the exact value) stays in the one block it belongs to;
that is one claim shown twice, not two claims.

Material that is adjacent to a block's topic but not required to derive it (a lecture's recap of
a neighbouring idea, a 3Blue1Brown video that touches the same picture from a different angle,
see "Find the 3Blue1Brown material first" and the lecture-slide instructions) is a candidate for
its own block or its own paragraph, never an automatic addition to the block it happens to sit
near. Say in the plan, block by block, when something adjacent was left out and why, so the
decision is visible before any LaTeX is written.

## Every named case gets its reasoning, a table never stands in for it

When a Theory block states a rule and then shows it on a short list of cases (three kinds of
function, four special values, two limits), each case gets its own sentence connecting the
general rule to that specific instance: not just the result, but why the rule gives that result
here. "A quadratic form has gradient $(\vv A+\vv A^\top)\vv w$, so its Hessian is $\vv A+\vv A^\top$"
is written out. "$\vv w^\top\vv A\vv w \to \vv A+\vv A^\top$" in a bare table row is not: it
states a fact without the one line that lets the reader rebuild it.

A table is still useful, as a reference the reader returns to after the reasoning has already
been shown in prose for every row it contains, not as a shorter replacement for that reasoning.
If a block needs a table because it has grown past four or five cases, that is itself a sign the
block should split (see above), not a reason to compress the missing cases into an unexplained
row. The same holds for a Recipe box: it names the steps of a procedure the Theory prose already
derived, it does not carry derivation that appears nowhere else in the block.

## Where to cut a chapter into paragraphs

A paragraph is one idea the reader can hold in their head at once, and the split points come
from the subject, not from a count. The test: can you say in one short phrase what this
paragraph is about, and would the reader agree that the next block starts something new? If a
cut makes them ask "why did that stop here?", it is in the wrong place.

The sizes below are a rough guide for spotting trouble, not a rule. Break them whenever the topic
calls for it, and say why in the plan.

- **Typical size:** 3 to 6 Theory blocks, roughly 10 to 20 pages.
- **7 or more blocks:** check whether the paragraph hides two ideas (for example discrete
  versus continuous, or a method versus its analysis). If so, split at that seam. If it really
  is one idea, leave it long.
- **1 or 2 blocks:** check whether the topic leads straight into its neighbour (Bayes' rule
  after conditional probability, a chain rule after the derivatives it applies to). If so, merge
  it there. If it is a genuinely separate idea that happens to be short, leave it short.
- **Short chapters** (fewer than about 8 Theory blocks in total) can have paragraphs of 1 or 2
  blocks.
- **Uneven is fine, arbitrary is not.** A long paragraph next to a short one is acceptable when
  each holds together. Unevenness that comes from the split being drawn in the wrong place is
  the thing to fix.

In the plan, list the number of Theory blocks per paragraph next to each title, so lopsided
splits are visible before any LaTeX is written.

## Callouts: three distinct jobs, not one

A short embedded note inside a Theory box earns its place by doing one of three specific jobs,
not by being generically helpful:

- **Misconception or sign warning.** Flags a common error before the reader makes it, paired
  with a small concrete counter-example that shows the rule in miniature (e.g. a two-line
  numeric check that a sign flips under a specific operation) before it's used at full
  complexity.
- **Notation translation.** Flags that two phrasings or two pieces of notation mean the same
  thing, because the exercises will use both interchangeably and an unwarned reader would think
  they're different tasks.
- **Worked micro-step.** Pulls one easy-to-fumble mechanical step out and shows it in isolation
  (a single substitution or simplification that's easy to state but easy to get wrong), when
  that step is exactly the kind of thing a reader gets the concept right but trips on anyway.

Add one wherever a mechanical trip-up is actually likely, not wherever there's spare space in
the box. Not every Theory block needs one.

## Exercise taxonomy

| Tag | What it does | Where it sits |
|---|---|---|
| P (Prior knowledge) | Something the reader is assumed to know, recapped where it is first needed, with an exercise that makes it fluent before new material builds on it. Own numbering in the opening Prior knowledge section (no tag), or a P-tagged exercise after a short refresher box inside a paragraph | Opening section, or right before the first use |
| O (Orient) | A concrete probe the reader can already solve, so that the general rule feels earned and does not arrive cold | Before its Theory block in the text; after the Theory cell in the Contents pill |
| T (Test) | A gate-check right after the worked example: the same task with smaller numbers, 3 lettered parts that mirror the worked example step by step. It shows whether the reader is ready to move on, and it drills a little too | Right after the worked example |
| D (Drill) | The bulk of the practice: one numbered exercise is one named family of the same move, with a bold title and usually 5 to 8 lettered parts (ordinary cases, then special cases, then the reversed direction). 3 to 4 families per Theory block, chosen from the variation map. Nothing new is asked. A good D family has one invariant task and several surface variations | After T |
| V (Visualize) | Predict or sketch a picture: how a curve, area or grid changes when a parameter moves. Same axes in every panel. The question shows empty axes, the solution shows the working and the finished figure. See `reference/visual-intuition.md` | After the drills |
| E (Exam) | The level the course expects: 3 to 5 chained parts, no recipe named, no hints, may combine earlier blocks. The solution is a full argument. The course's own questions appear here in their own wording, with source tags | After V |
| C (Challenge) | Harder than the course asks: an unusual framing, an edge case, a proof the course never requires. Skipped on a first pass | After E |
| R (Reflect) | A short question that asks why: it revisits and generalizes a step, answered in words. Course-required proofs are not R. It closes the run | Last |

**Order inside a block's run:** T, D, V, E, C, R, with O before the Theory block. The exam path is T, D, V and E. Never
hard-code the number of "the last exercise"; point to it by its tag and block. The Worked example is a model problem of the
same type as the E questions. The course's own questions go to E.

**Variation map.** Before writing a block's run, list along which dimensions its idea can vary: inputs (numbers), roles (which
quantity is unknown, the reverse direction), special cases, representation (formula, picture, table, words), parameter
dependence, neighbouring methods (which tool applies), assumption limits. Every dimension needs an exercise: D covers inputs,
roles and special cases, V covers pictures and parameter dependence, E covers which method applies, C and R cover assumption
limits and meaning in words.

For every D family, name the invariant before writing the parts. Ask: "What is the one thing
the reader is practising here?" Then keep that invariant fixed. Vary only surface features:
the numbers, labels, dimensions, signs, location of a zero, whether a matrix is square, whether
the expression is numeric or symbolic, or whether the final part asks for the same move in
reverse. If a part needs a new rule, a new setup, or a new explanation before the reader can
attempt it, it does not belong in that D family. Make it a later family, an E question, a C
question, or a new Theory block.

(In the rest of this section, "plain practice" means the D drills.)

**The plain-practice row is not a suggestion, and it is not several separate exercise
numbers.** Put several sub-parts, lettered (a) through (f), (g), (h) or so, under *one*
exercise number, the same way a real textbook's "opgave 4" has parts a-f rather than being
opgaven 4 through 9. Four parts is often the bare minimum for a narrow move; six to eight parts
is normal for a core mechanical skill; nine is fine when the variations are still genuinely the
same task. One number with many near-identical sub-parts drills exactly as much as many separate
numbers would, and reads as one coherent drill instead of a wall of similar-looking exercises.
Each sub-part should still vary in some real way (different magnitudes, a repeated value in one
sub-part but not another, a slightly different phrasing) so working through all of them doesn't
feel like filling in a template; the move stays the same, the specifics don't. Before closing
out a Theory block's exercise run, look at the sub-parts inside every plain-practice item. A
family with only two or three parts is usually not a finished drill; it is a quick check. Either
extend it with more nearby situations or admit in the plan why the move cannot support more
repetition.

**Every consolidated exercise (T-badge or plain) sticks to one theme across all its
sub-parts.** "One theme" means the same task applied to different numbers, not different
tasks that happen to touch the same topic. If a sub-part would introduce a genuinely new
wrinkle (a changed assumption, a shifted domain, a different setup that needs its own
sentence of setup before the reader can even attempt it), it doesn't belong lettered inside
the drill; give it its own exercise number instead, positioned wherever it earns its place
(often right before the Reflect or Challenge item it feeds into). A drill that quietly
changes what it's asking partway through stops feeling like repetition and starts feeling
like a pop quiz.

Bad Drill family, because the invariant changes each part:

```latex
\item[\extag{\Dbadge}] \extitle{Multivariate calculus.}
\item[(a)] Compute a partial derivative.
\item[(b)] Give a Jacobian shape.
\item[(c)] Prove a minimum.
\item[(d)] Derive the softmax Jacobian.
```

Good Drill family, because the invariant is "freeze one variable and differentiate with
respect to the other":

```latex
\item[\extag{\Dbadge}] \extitle{Freeze one variable.} Find both partial derivatives.
\item[(a)] \(f(x_1,x_2)=x_1^2x_2\).
\item[(b)] \(f(x_1,x_2)=x_1x_2^2\).
\item[(c)] \(f(x_1,x_2)=e^{x_1}x_2\).
\item[(d)] \(f(x_1,x_2)=x_1\sin x_2\).
\item[(e)] \(f(x_1,x_2)=x_1^2\cos x_2\).
\item[(f)] \(f(x_1,x_2)=\log x_1+x_1x_2\).
\item[(g)] \(f(x_1,x_2)=x_2\), differentiated with respect to \(x_1\).
\item[(h)] A student says \(\partial(x_1x_2)/\partial x_1=x_1\). Correct the mistake.
```

Good Drill run after a Sigma-notation block, because each family keeps one invariant and
varies the surface:

```latex
\item[\extag{\Dbadge}] \extitle{Expanding a sum.} Write out the terms and compute when possible.
\item[(a)] \(\sum_{i=1}^4 i\).
\item[(b)] \(\sum_{i=1}^3 i^2\).
\item[(c)] \(\sum_{k=0}^3 2^k\).
\item[(d)] \(\sum_{p=1}^5 3\).
\item[(e)] \(\sum_{j=2}^4 (j-1)\).
\item[(f)] \(\sum_{i=1}^3 a_i\), with \(a_1=4,a_2=-1,a_3=2\).

\item[\extag{\Dbadge}] \extitle{Writing a sum with Sigma.}
\item[(a)] \(1+2+3+\cdots+10\).
\item[(b)] \(1+4+9+16+25\).
\item[(c)] \(2+4+6+8\).
\item[(d)] \(x_1y_1+x_2y_2+x_3y_3\).
\item[(e)] \(w_1x_1+w_2x_2+\cdots+w_nx_n\).
\item[(f)] \((y_1-t_1)^2+\cdots+(y_N-t_N)^2\).
```

## The checkpoint (T) exercise

A gate-check right after a Theory block's worked example: attempt it, compare against the
solution, and use the result to gauge whether to move on confidently or slow down on the
plain practice that follows. Like plain practice, it drills, just briefly: 2-3 lettered
sub-parts on one exercise number, same theme, not a single one-shot item. No skip-ahead
mechanic, no item-number cross-references baked into the exercise text; those are fragile
once exercises get renumbered or consolidated; the checkpoint's value is the self-check
itself, not a print-era navigation trick.

## Presentation convention for solutions and derivations

`check-chapter.py` flags this rule directly: any `\sol{...}` over 250 characters with no
`align*`/display line ("Dense solutions" in its output) has almost certainly compressed a
multi-step derivation into one run-on paragraph instead of following the rule below. A chapter
authored without checking this once shipped with 87 such solutions; treat every line in that
list as unfinished work, the same way a flagged short solution or a flagged thin Theory block is.

- Every derivation step gets its own line, via `align*`. Never two `=` signs of real content on
  the same line, even for something that looks trivially simple. A two-term sum like
  `2(4)+(-1)(2)=8-2=6` still gets three lines (substitute, reduce, result), not one.
- Prefer a short prose sentence followed by a separate display equation over folding an
  explanation into the same line as the math. Alternate: a sentence of reasoning, then a display
  block, then the next sentence. Never a display equation with an explanatory clause crammed
  onto its own line.
- This spaciousness rule applies to **Theory-box derivations too, not just worked solutions**.
  Don't compress a Theory derivation just because it isn't inside a `\sol{}` block.
- Solution boxes are a plain shaded background with no border line: soft and spacious, not a
  hard-edged frame.
- This mirrors, at the level of a single step, the same principle that governs a whole exercise
  run: don't compress. Let each atomic move take its own line/item rather than cramming
  multiple moves into one.

Prior knowledge only repeats what the chapter needs, taken from `vwo-wiskunde-b.md` and from earlier chapters, and it stays out of the Summary. See design-system.md, "Prior knowledge".

## Review (paragraph-end)

Closes every paragraph. Zero new problems. It has the same three parts as the Summary: the terms
(each a link back to where it was introduced, with its formula or notation in brackets), the formulas
(one per bullet) and the recipes (numbered steps). It restates what that paragraph's Theory blocks
taught, in the order it was introduced. It's a cheat sheet, not a teaching moment: nothing is explained
here that wasn't already explained in full earlier. The Summary is built from the Reviews, so each part
is written once (see design-system.md, "Review and Summary").

## Summary (chapter-end, immediately before the Diagnostic check)

A chapter-level cheat sheet, one level up from a Review: organized by paragraph, and under each
one listing its terms, its formulas, and its recipes (the how-to procedures count as much as
the facts). Complete enough to redo the chapter's exercises from this page alone; spacious
rather than terse. Zero new problems, same as a Review. A chapter with only one paragraph can skip this (that paragraph's
own Review already does the job) and go straight to the Diagnostic check.

## Diagnostic check (chapter-end)

Not the same thing as a Review, and not optional once a chapter has more than one paragraph.
Where Review has zero new problems, a Diagnostic check is the opposite: genuinely new
self-check problems, one set closing the whole chapter, after the Summary. Rules that make it
a diagnostic and not just more practice:

- **Independent numbering**, its own 1, 2, 3, ..., unrelated to any paragraph's exercise count.
- **Grouped under repeated paragraph sub-headings** ("§1", "§2", ...), so the reader can see
  which paragraph each item checks.
- **No O/T/R/A/D/P tags.** These items aren't part of the tagged cycle; they're a flat
  self-check gate.
- **Roughly even item count per section**, regardless of how many exercises that paragraph's
  body actually had. A paragraph that ran to 20 exercises and one that ran to 6 both get a
  similar-sized diagnostic slice; this samples every paragraph at the same density rather than
  scaling down each paragraph's own practice set.

## Book/course-level closing layer (use only if authoring more than one chapter for a course)

Two layers can close out a whole course, beyond any single chapter's Diagnostic check, if this
skill is ever used to build several chapters for the same course: a final interleaved review
set, pulling already-practiced items from every chapter with nothing new introduced (escalation
here comes purely from context-switching between now-mastered skills, not harder mechanics),
and an optional stretch problem set pitched above the normal D-tier ceiling for readers who want
more. Treat both as real but deferred: don't build either while authoring a single chapter in
Mode A, and don't skip them silently if a later request is clearly asking to tie a whole
course together.

## Cognitive-demand verb ladder

The imperative verb an exercise opens with should track a real difficulty step, not just
phrasing variety: mechanical application ("solve", "compute") → exact/precise variant
("compute exactly", no rounding) → "construct the model" variant ("derive/set up") →
"justify your answer" variant ("explain") → "prove the given claim" variant ("show that").
