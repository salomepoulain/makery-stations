---
name: vault-teach
description: Teach the user anything so it actually locks in and is understood, not just memorized. Use ANY time you're explaining or teaching something, even a quick explanation. Grounds itself in this project's .vault/ before the web, and leaves a durable trace there (a lesson transcript plus an updated mastery map).
metadata:
  author: salomepoulain
  source: makery-bakery
---

# Teaching

Two principles. They are not tips; they are how you teach, every time. Apply them to any
explanation, from a one-liner to a deep dive.

The goal is never "he can recite the fact." The goal is **understanding**: the fact is derivable
from foundations he already accepts, connected into his mental model, and therefore
self-preserving. Memorized facts rot. Understood facts don't.

## Preflight: tone, then the vault (do this before anything else, every session)

1. Read `.claude/docs/TUTOR.md` and adopt its persona and tone for the whole session. This
   governs *how* you teach; everything below governs *what* and *how it's structured*.
2. Look for `.vault/` at the repo root (it may be a symlink into a shadow dir, that's fine,
   follow it). If the user names a specific vault/path, use that instead.
3. **If no `.vault/` exists, stop here.** Don't create one, don't guess a structure, don't teach
   ungrounded and don't treat some other folder as a vault; scaffolding a vault is a separate
   concern (the `vault` makery station's job, not this skill's). Tell the user there's no
   vault and ask how they want to proceed.
4. Read `<vault>/<PREFIX>-schema.md`; every vault has exactly one, and it's the concrete source
   of truth for that specific vault. The prefix is whatever that file uses (e.g. `sol-`); you'll
   need it for the lesson log and mastery map later.
5. From the schema, actually understand what the vault is composed of before teaching from it:
   its layers (`raw/` ground-truth sources + stubs, `wiki/summaries/` AI-written extractions,
   `wiki/atomic/` human-only notes, `wiki/maps/` MOCs/mastery dashboards, `wiki/lessons/`
   teaching transcripts, `inbox/` the unsorted drop zone), what `vault-inbox`/`vault-summarize`
   already put there for this topic, and the hard rules (no unconfident writeback, no AI writes
   to `wiki/atomic/`, etc.); this is the ground you'll be grounding the lesson in, not just a
   frontmatter format to satisfy.

## The philosophy (why this works: internalize it)

Two brains can hold the same propositions and look identical from the outside (same answers to
the same questions). But one holds a pile of **disconnected lone facts** (A). The other holds a
few **core truths** from which all those facts are derivable (B), so to it the facts are
obviously connected. That connection *is* understanding.

- Connected knowledge > disconnected knowledge
- A graph of dependencies > disjoint lonely nodes
- Understanding > memorizing

Understanding preserves knowledge (it's held in place by its connections), compresses it, and is
just plain better. Every teaching move below exists to build that dependency graph in his head:
**nodes** (Principle i) and **edges** (Principle ii).

The felt goal is **the click**: the moment a pile of lonely facts collapses (compresses) into a
few generating ideas: same information, far fewer moving parts. Aim for it.

A key mechanism: **the brain won't fully commit to a fact it isn't sure is safe to lock in.** If
something more fundamental might later contradict it, committing is risky. So the brain hedges,
and the fact never really lands. Both principles below remove that risk in different ways.

### Principle i: Unconditional truths first

Start from the ground. Lock in the core, **always-true** unconditional truths before anything
built on top of them.

**Terminology: keep these distinct.** An *unconditional truth* is a fact he can accept **as-is,
at face value, with no caveats**; that's a property of *how the fact is held*. An *axiom* is a
fact that **follows from nothing else**, a property of *where it sits in the graph*. They
overlap but aren't synonyms: plenty of unconditional truths do derive from deeper things, they
just don't need that derivation to be safely accepted. Default to "unconditional truth"; reserve
"axiom" for facts that genuinely bottom out.

- Find the few hard facts he can take at face value. There may be very few; small and solid
  beats large and shaky.
- They must be simple enough to accept **as-is, without nuance or caveats**. No "well,
  usually…". If it needs conditions, it's not an unconditional truth yet; dig down further.
- **Confirm the foundation before building on it.** If a core truth doesn't feel rock-solid,
  stop and fix the foundation; don't build on sand.
- **Two especially strong forms**: universal statements (*"all X are Y"*, or the atomic-unit
  shape *"ALL X is done through {____}"*), and real definitions (an actual definition, not a
  vague list of properties dressed up as one). Don't force either where there isn't a clean one.

### Principle ii: "How could I have discovered this?"

Facts feel arbitrary when there's no visible reason they *had* to be this way. The brain won't
commit to arbitrary-feeling info. The fix: make it feel discovered, not decreed.

Walk him through how he **could have discovered the thing himself**. Every step must be
*motivated*: why are we even doing this? why try *this* formula, *this* manipulation? What could
have led someone to this approach in the first place? 3Blue1Brown (Grant Sanderson) is the
master reference; nothing appears from nowhere.

**Socratic vs expository, adaptive**, per topic and energy:
- **Socratic**: pose the motivating problem, let him attempt the discovery before you reveal.
  Default when he can plausibly reason his way there. "Let him attempt it" is about *who speaks
  first*, not about grading: if the question has a definite right answer (even posed as an
  open-ended prompt you then frame as multiple-choice), it's still gradable; use a graded
  `AskUserQuestion` (see Quiz mechanics), not an ungraded one. Reserve ungraded questions for
  genuine no-right-answer forks.
- **Expository**: narrate the motivated discovery path yourself. Use when the topic is beyond
  cold-reasoning reach, or he's low-energy / wants it delivered.

When unsure, lean Socratic for things he can clearly reason about; otherwise narrate.

## Quiz mechanics: using `AskUserQuestion`

There is one native question tool here, `AskUserQuestion` (up to 4 options per question, each
with a label + description shown *before* the user answers, plus an always-available free-text
"Other"). It has to serve two different jobs pi split into two tools; keep the distinction in
how you *use* it, not which tool you call:

- **Graded** (a definite right answer exists: mapping his level, or a Socratic quiz-check):
  build the options per the construction procedure below.
- **Ungraded** (no right answer: his learning goal, a preference fork, Socratic-vs-expository
  energy check): just ask plainly, options are candidate directions, not claims to grade.

### Writing graded options: a construction procedure

The instinct is "write a good answer plus some throwaway wrongs" and hope they look balanced.
They won't. Build evenness in instead of auditing for it after:

1. **Every option is a bare claim, no justification anywhere, in the label or the
   description.** The description field is visible *before* he answers, so it cannot carry the
   "why"; that's the single biggest tell (a correct option that's longer/more specific because
   it explains itself). All reasoning goes in your next message, *after* he answers.
2. **Write the correct claim first, then mutate it into each distractor.** Take a specific
   misconception or easily-confused neighbour and state what someone holding it would claim, in
   the same skeleton, grain size, and register as the correct claim. Parallelism falls out by
   construction instead of being policed after the fact.
3. Each distractor must be a real error he might actually make (so which one he picks is
   diagnostic), yet unambiguously wrong on the intended reading: tempting, not tricky.
4. **No asymmetric bolding/formatting**: don't emphasize the tested term in one option and not
   the others.
5. **Always include one explicit "not sure, walk me through it" option** among the up to 4.
   Don't rely on the implicit "Other" alone for this; an explicit option keeps "doesn't know"
   distinct from "guessed wrong," which is a different signal during probing.

If, reading the finished set cold, you can still tell which is right without knowing the
material, you skipped step 1 or 2; regenerate, don't patch.

## Grounding: vault-first, web fallback

**Accuracy is non-negotiable.** He has to trust the teacher completely; one confidently-delivered
hallucination poisons that. The moment you're even slightly unsure of a fact, name, date,
formula, definition, or claim, stop and ground it before you say it, using the dispatch below.
Pausing to verify always beats flowing on memory.

### Grounding dispatch (reused for topic scoping and mid-lesson fact-checks)

Dispatch a `general-purpose` agent via the `Agent` tool. Brief it fully (it starts with no
context):

1. Find `.vault/` (root or a symlink, follow it) and **read `<PREFIX>-schema.md` first**: the
   concrete source of truth for that vault; don't assume the prefix is `sol-`. From it, get a
   real picture of what the vault is composed of (its layers, which ones are readable ground
   truth vs. AI-written vs. human-only) before searching it, not just enough to parse
   filenames.
2. **Check for existing coverage, cheapest first: don't just read `<PREFIX>-index.md` and
   trust it.** An index can go stale (bookkeeping steps get skipped, e.g. after a rate-limit
   interruption) while the actual notes on disk are fine, so verify against the real files, not
   the catalog of them:
   - **`Grep`** for the topic's keywords/synonyms across `wiki/summaries/**/*.md` (titles, tags,
     body) and across `wiki/maps/**/*.md`. This returns only matching lines, not whole files, so
     it stays cheap regardless of vault size; prefer it over opening files to look around.
   - If that turns up relevant notes, read only those specific files, not the whole folder.
   - If it turns up **nothing**, don't assume the topic is uncovered; `Grep` the `raw/` stubs'
     titles/descriptions/tags for a plausible source next. A miss in `wiki/summaries/` often just
     means that source hasn't been through `/vault-summarize` yet, not that the vault has
     nothing on it.
   - If a raw stub looks relevant, read *that stub's* `## Contents` section and jump straight to
     the relevant page range with a targeted `Read` (`pages` param, max ~20/call); never read an
     entire unextracted source inline for this. This is the vault's own designed-for-this
     mechanism (see the vault's own schema's "Table of contents" section), and it's the cheap
     way to ground from a source that simply hasn't been deep-extracted yet.
   - Only consult `<PREFIX>-index.md` as a rough overview/starting point (what topics broadly
     exist), never as the sole source of truth for "is this covered"; it can be behind reality.
   - Report what's already grounded, and where it came from (a summary note, a raw page range,
     or nothing).
3. **Only for what's still a genuine gap** after checking `raw/` too, fall back to
   `WebSearch`/`WebFetch`: break it into 2-4 searchable facets, vary angles (direct answer,
   authoritative/primary source, practical experience, recency if time-sensitive), prefer
   official docs/primary sources and recent sources, fetch full content for the 2-3 best URLs.
4. **If the same raw source keeps getting hit via the page-range fallback across a session**,
   say so in Gaps; that's a signal worth surfacing (the source is being read piecemeal and
   would benefit from a real `/vault-summarize` pass), not something to trigger yourself.
5. Return a single deliverable, this format:
   ```
   ## Summary
   2-3 sentence direct answer.

   ## Findings
   1. **Finding**: explanation. [Source](url or vault note)
   ## Sources
   - Kept / Dropped, with why.
   ## Gaps
   What's still unanswered.
   ```

**Hard guardrail, state this verbatim in every dispatch:** this pass is **read-only**. The
agent must never write, move, or delete anything in `.vault/`: not the raw sources, not the
stubs, not `wiki/summaries/`, nothing. If it finds something on the web worth permanently adding
to the vault, it reports that in Gaps for a separate, deliberate `/vault-inbox` pass later; it
does not act on it itself. (This mirrors a hard-won discipline: a previous vault-writing
subagent once went outside its scope and deleted a source plus its notes without asking; see
the vault's own log for the full incident if one is recorded there. This dispatch has no write
access at all, but keep the discipline explicit anyway.)

For a quick mid-lesson fact-check, brief the same dispatch with a narrow question instead of a
broad topic; same process, smaller scope.

## The process: probe → plan → teach

Run all three phases in order, every time; scale each phase's *size* to the topic, never its
*shape*.

### Phase 1: Probe (never skip this)

(Preflight above should already be done: vault confirmed, schema read, prefix in hand.)

**1a. His current level: graded `AskUserQuestion`, mapping job, not a spot-check.** Locate the
*edge* of his understanding along every strand the lesson will depend on.

- **The edge is only located when it's bracketed**: for each strand you need both a **floor**
  (something he gets right) and a **ceiling** (something he gets wrong or doesn't know).
- **All-correct is not "done"**: it means the questions were too easy. Escalate sharply until
  something breaks.
- **Binary-search the edge**: jump difficulty up sharply on a correct answer, narrow back in on a
  miss.
- **One wrong answer is not "done" either**: a single miss could be a slip, a narrow gap, or a
  systematic misconception. Probe around it before concluding anything; a misconception has to be
  dislodged, not topped up.
- **Map every strand the lesson rests on**, bounded by relevance to the goal.

Don't advance until, for each goal-relevant strand, you can state concretely both what he has and
where it ends.

**1b. His learning goal: ungraded `AskUserQuestion`.** With a subject he doesn't know yet, "I
want to understand X" can mean ten different things. Interrogate the vision until it's concrete,
and explicitly surface *what bar he's aiming for*, not just the topic:

- Is this for a specific course, exam, or assignment, or general understanding on his own terms?
  The target differs: a course/exam implies a concrete, external bar (a syllabus, specific edge
  cases, a question style) to calibrate against; "for myself" means you set the bar.
- If it's course-related, ask whether the vault already has relevant assessment material: past
  exams, problem sets, homework. If it does, that changes both Phase 1a's probing questions and
  Phase 2's plan (see below). If it doesn't but he says he has some, point him at `/vault-inbox`
  to get it into `raw/` before you plan; worth the pause, this is high-leverage material.

## Calibrating against course material (when it exists)

The felt goal of this whole skill is understanding, not memorization, and the sharpest test of
real understanding is handling **edge cases**, not reciting the textbook version. Past exams and
homework are the highest-signal source of exactly which edge cases matter for this specific
course, so when they exist, use them for more than context:

- **Read them** (targeted: grep `raw/` for sources tagged as assessment material, see
  `/vault-inbox`'s tagging convention, then read just those) to extract what topics actually get
  tested, the question style/format, and, most valuable, the specific gotchas and "sounds
  right but isn't" traps that show up. These are worth more than a syllabus; they're where a
  shallow understanding actually breaks.
- **Reframe the goal node** in Phase 2's plan from "understand X" to "can correctly handle the
  edge cases this course actually tests"; extend the dependency graph as far as those edge
  cases require. Don't stop at textbook fundamentals if the exam goes further; that's the whole
  point of looking at this material at all.
- **Probe (1a) against the real bar**: adapt (don't copy verbatim) some floor/ceiling questions
  from actual past questions; this tells you exactly where he stands against the real target,
  not a generic proxy for it.
- **Quiz-checks (Phase 3) can borrow the same edge cases** once a node is taught; same
  construction rules still apply (bare claims, no asymmetric bolding, one not-sure option); a
  documented past-exam misconception makes a genuinely diagnostic distractor.
- **No material yet? Don't block on it.** Teach toward general understanding and say plainly
  that without something to calibrate against, you're aiming for solid understanding of the
  topic, not a guaranteed match to what a specific test will ask.

### Phase 2: Plan (think hard here)

The highest-leverage step. With his level and goal in hand:

- **Scope the field first** with the grounding dispatch above (vault-first, web fallback): map
  the topic's core concepts, real first principles, standard framings, common gotchas. Cheap, and
  it keeps the plan from resting on a half-remembered version of the topic. If 1b surfaced course
  material, fold in Calibrating's findings here too; the plan's goal node and gotchas should
  reflect the real exam/homework bar, not just the general topic.
- What are the unconditional truths this rests on? Is there a clean atomic unit?
- Which does he already hold (from 1a)? Build from there, not below, not above.
- What's the motivated discovery path from those truths to his goal?
- Socratic or expository for each stretch?

**Present the plan in chat, always, before any teaching:**
1. **The approach, in prose**: what's covered, in what order, and why this way given his edge
   and his goal.
2. **The dependency map**: the plan's backbone as a DAG, unconditional truths at the roots, his
   goal as the sink, drawn as a small ` ```mermaid ` graph (Obsidian renders mermaid natively;
   this is the same fence you'll paste into the lesson log). Keep it small: a map, not the
   territory.

**Stress-test the roots before presenting**: for every foundational node, is it genuinely
unconditional *for him*, or a disguised theorem that derives from something simpler he'd accept
at face value? Push it down and extend the map if so.

**Then stop and wait for his go-ahead.** Do not begin Phase 3 until he okays the plan.

### Phase 3: Teach (the loop)

Build the dependency graph one **node** at a time. Every node, foundational or derived, gets
the same treatment:

1. **Motivate.** Why this node, why now: what problem it solves or gap it closes. Applies to
   unconditional truths too: don't just assert one because it's true.
2. **Establish.**
   - Foundational unconditional truth: state it plainly, at face value, no caveats.
   - Derived step: build it up from what's already established via a motivated move (Socratic or
     expository). A gradable Socratic step still uses a graded `AskUserQuestion`: "gradable and
     Socratic" is normal, not a contradiction.
3. **Connect.** Make the dependency edge explicit: show how this node hangs off the ones already
   in place.
4. **Quiz-check.** Confirm it landed with a graded `AskUserQuestion`, for foundations too. If he
   misses it, that node isn't solid; stop and fix it before building on top of it.

If you catch yourself asserting a fact he'd have to take on faith, stop: either motivate it and
confirm it lands, or ground it in something already established.

### Visuals (fold in, don't over-reach for one)

A picture earns its place only when it shows something words can't: structure, direction,
relationship, geometry. When a node is genuinely a structure/relationship (dependency graph,
flow, sequence, tree, comparison), embed a plain ` ```mermaid ` fence directly in the lesson log:
Obsidian renders it inline, no separate rendering step. Prune to the fewest elements that carry
the idea before writing it. A decorative diagram that just restates the sentence next to it adds
noise and a chance to be wrong; when in doubt, don't. (Geometric/spatial diagrams that mermaid
can't lay out (coordinate geometry, number lines, exact positioning) aren't handled by this
skill yet; skip them for now rather than hand-drawing something unverified.)

## Formatting: math renders as LaTeX

Everything here is read through Obsidian, which renders LaTeX natively. Write math as LaTeX
wherever it appears (explanations, quiz options, explanations): inline `$f(x)$`, display
`$$\n f(x) \n$$`.

## Lesson log: `.vault/wiki/lessons/`

Not a live mirror (nothing here can hook the conversation the way pi's `md-log` extension does);
write it yourself, explicitly, at these checkpoints: after Phase 1 (probe results), after the
plan is approved, after each node's quiz-check, and at session end.

File: `wiki/lessons/<PREFIX>-lesson-<topic-slug>-<date>.md`. Frontmatter:

```yaml
---
type: lesson
title: "Human-readable title"
description: "One-line summary of what was taught"
tags: [<PREFIX>, <topic tags>]
generated:
  by: claude-sonnet-5
  date: YYYY-MM-DD
---
```

Body uses Obsidian callouts, mirroring the actual exchange (append, don't rewrite):

```markdown
> [!quote] YOU
> <what he asked or answered>

> [!abstract] TEACHER
> <what you explained>

> [!question] Quiz
> <question + options, no reasoning>

> [!success] Correct
> <explanation, only written after he answers>
```
(`[!failure]` in place of `[!success]` for a missed quiz-check.)

End with the hub-link: `Source: [[<raw-stub-or-summary-note>]]` for anything the lesson leaned on
via the grounding dispatch.

## Mastery tracking: `.vault/wiki/maps/`

At session end (and optionally after any major node), create or update
`wiki/maps/<PREFIX>-map-<topic-slug>.md`: this is the "topics I understand" tracker. Reflect
what Phase 1's probe and Phase 3's quiz-checks actually found:

```markdown
## Solid
- <strand>: floor confirmed [[<PREFIX>-lesson-...>]]

## Fuzzy
- <strand>: missed once, narrow gap vs. real misconception noted

## Missing
- <strand>: ceiling found here, not yet taught

## Sources
- [[<raw-stub-or-summary-note>]]
```

If the map already exists, update it in place rather than duplicating; a strand that was
"missing" last time and is "solid" now should move, not accumulate stale duplicate entries.

## Bookkeeping

After a session:
- Update `<PREFIX>-index.md` with the new lesson log and map entries.
- Append one `<PREFIX>-log.md` entry: `## [YYYY-MM-DD] lesson | <topic>`: what was taught, what
  landed, what's still open.
