# examples/

This folder is empty on purpose. It's where you (the human) drop reference material before
asking this skill to author a chapter for a new subject: example Theory blocks, worked
examples, or exercise sets that show the tone/level/scope you want, in whatever rough form is
convenient (notes, a snippet of `.tex`, a screenshot description, a link to a source you've
already put in a project's vault).

This skill does not write example content into this folder itself. Only the two `reference/`
files (the LaTeX scaffolding and the pedagogy cycle) are authored by the skill. What you put
here is real source material the skill should ground against and match, the same way a human
author would work from reference examples rather than inventing a style from nothing.

If this folder is empty when the skill is invoked for a new subject, it proceeds using only
`reference/pedagogy-cycle.md` and whatever grounding it can find in the target project's own
vault/docs. Say so plainly in the chapter's plan presentation rather than silently pretending
examples were provided.
