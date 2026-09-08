# Academic Paper Reviewer

The multi-perspective review engine of the suite. Consumes a complete paper and produces a structured review with an Editorial Decision Letter, priority/severity-tagged comments, and a Revision Roadmap.

A panel of reviewers (default 5) covering methodology, novelty, clarity, significance, and reproducibility, with optional cross-model verification at the two irreversible decision checkpoints.

## When to use this skill

Use when the work is reviewing a completed paper: structured peer review, re-review after revision, focused methodology audit, or guided review dialogue with the author. The manuscript exists in near-final or final form.

## Modes

| Mode | Purpose |
|---|---|
| `full` | Standard 5-reviewer multi-perspective review. Default. |
| `re-review` | Re-review after the author has revised. Stands up against the previous round. |
| `quick` | Fast single-pass review. |
| `methodology-focus` | Methodology-only deep audit. |
| `guided` | Socratic review that engages the author in dialogue. Use when the author wants to learn from the review. |
| `calibration` | Opt-in LLM-as-judge calibration (FNR / FPR / balanced-accuracy). |

For `full` vs `guided`: if the author wants to learn from the review and engage with it, use `guided`. If the author needs a structured review report, use `full`.

## Key rules

- Reviewer outputs use categorical criterion judgements, never free-form prose-only verdicts.
- Per-finding author disposition is required for revision claims.
- Reviewer comments are priority/severity-tagged so the author can triage.
- AI disclosure is included in the review packet.
- Re-review rounds run against the previous round review plus the author response.

## Inputs and outputs

**Expects**: a complete paper (markdown or text), optionally the previous round review packet and the author response (for `re-review`).

**Produces**:
- Editorial Decision Letter
- Per-reviewer detailed comments (priority/severity-tagged)
- Revision Roadmap
- Review Panel Provenance (when cross-model track is engaged)

**Hands off to `academic-paper` (revision mode)**: the Editorial Decision Letter + Revision Roadmap.

## Routing

Routing across the 4 academic skills is documented in `academic-pipeline/docs/SKILL_GUIDE.md` "Routing Discipline." This skill assumes routing has already settled on `academic-paper-reviewer`.

## Related skills

- `academic-deep-research` — upstream research engine.
- `academic-paper` — produces the paper this skill reviews, and consumes this skill outputs for revision.
- `academic-pipeline` — full orchestrator that chains all three.
