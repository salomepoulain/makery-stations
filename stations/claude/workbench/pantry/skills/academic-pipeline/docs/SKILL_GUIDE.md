# Academic Pipeline

The full pipeline orchestrator. Coordinates `academic-deep-research` to `academic-paper` to integrity checks to `academic-paper-reviewer` to revision to final integrity to finalization, with the AI Self-Reflection Report at the end.

The only one of the 4 academic skills that owns the cross-skill routing discipline. The other three are the building blocks; this one chains them and runs the integrity gates between stages.

## When to use this skill

Use when the work spans multiple stages: research and writing and review. If the user only needs a single function (just research, just write, just review), trigger the corresponding skill directly without the pipeline.

## What the pipeline runs

```
deep-research (socratic/full)
  to academic-paper (plan/full)
    to integrity check (Stage 2.5)
      to academic-paper-reviewer (full/guided)
        to academic-paper (revision)
          to academic-paper-reviewer (re-review, max 2 loops)
            to final integrity check (Stage 4.5)
              to academic-paper (format-convert, then final output)
                to Process Summary + AI Self-Reflection Report
```

The pipeline runs the two MANDATORY integrity gates (Stage 2.5 and Stage 4.5) and the optional cross-model verification at the irreversible decision checkpoints. It also emits the compliance audit trail and the AI Self-Reflection Report at the end.

## Handoff protocol between the three skills

- **deep-research to academic-paper**: RQ Brief, Methodology Blueprint, Annotated Bibliography, Synthesis Report, INSIGHT Collection.
- **academic-paper to academic-paper-reviewer**: complete paper text. The field analyst auto-detects domain and configures reviewers.
- **academic-paper-reviewer to academic-paper (revision)**: Editorial Decision Letter, Revision Roadmap, per-reviewer detailed comments.

## Routing Discipline (v3.9.2)

This section runs before any agent classification. Once it settles on a destination, the per-skill rules apply inside that skill.

### Step 0: Escape hatch

If the user first message begins with `[direct-mode]` (case-insensitive, byte-0 token, optional surrounding whitespace), record this fact, strip the prefix and surrounding whitespace, and skip directly to Step 1 explicit-intent handling on the stripped content. The literal `[direct-mode]` is not passed through to the dispatched agent. If the stripped message itself has no clear skill named, Step 1 falls through to Step 3 clarification (the escape hatch bypasses cross-phase clarification (Step 2), not all routing).

### Step 1: Explicit clear intent

The user invokes a specific skill via `/ars-*` slash command, or uses an unambiguous trigger keyword that maps to a single skill (e.g., "lit-review this", "review my paper", "draft an abstract"). Route directly; no clarification, no orchestrator detour.

### Step 2: Cross-phase materials

The user provides artifacts spanning two or more pipeline phases without naming a specific skill (e.g., pre-written abstract + pre-collected literature; full draft + reviewer comments + bibliography). Clarify. Do not auto-route to a single-phase agent. List candidate workflows as a-d options in the markdown body (not via AskUserQuestion tool). See `shared/references/intent_clarification_protocol.md` for the message template.

Reason: clarification is the safest action when materials do not unambiguously identify intent.

### Step 3: Ambiguous intent, no materials

The user provides no artifacts and no clear request. Clarify per `shared/references/intent_clarification_protocol.md`.

### Anti-pattern

Receiving ambiguous cross-phase materials and silently auto-routing to a single-phase agent based on which phase the materials "look closest to." This bypasses orchestrator-level reconciliation and lets the subagent inherit the full ambiguity.

## Per-skill routing rules

1. **academic-pipeline vs individual skills**: pipeline = full chain. Single function = trigger the corresponding skill directly.
2. **deep-research vs academic-paper**: complementary. deep-research is upstream; academic-paper is downstream. Recommended flow: deep-research to academic-paper.
3. **deep-research socratic vs full**: socratic = guided RQ clarification. full = direct production. When the RQ is unclear, suggest socratic.
4. **academic-paper plan vs full**: plan = Socratic chapter planning. full = direct production. When the user wants to think through structure, suggest plan.
5. **academic-paper-reviewer guided vs full**: guided = Socratic dialogue. full = standard multi-perspective report. When the author wants to learn, suggest guided.
6. **rebuttal-audit vs revision-coach (input-shape gate)**: route by input shape, not verbs. Use `rebuttal-audit` only when the user supplies both reviewer comments AND an existing rebuttal/response draft. Use `revision-coach` when only reviewer comments are present. If unclear, clarify rather than guess.
7. **real-committee correspondence vs peer review**: route to the `revision-coach` committee-correspondence variant only when the user explicitly identifies a real committee or institutional review office. Formal tone alone does not establish authority.

## Key rules

- All claims carry citations; evidence hierarchy respected.
- Contradictions disclosed with evidence quality comparison.
- AI disclosure in all reports.
- Default output language matches user input (English, 繁體中文, 한국어).

## Related skills

- `academic-deep-research` — upstream research engine.
- `academic-paper` — downstream paper writing.
- `academic-paper-reviewer` — multi-perspective review.
