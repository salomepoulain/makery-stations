# Third-Party Notices

This directory (`.claude/skills/`) contains a mix of original, project-specific skills and
skills sourced from or based on third-party repositories. This file records provenance and
license obligations for the latter, determined by diffing each active `SKILL.md` against
reference copies of the upstream repositories.

---

## mattpocock/skills

- Source: https://github.com/mattpocock/skills
- License: MIT
- License text: https://opensource.org/licenses/MIT
- Copyright holder: Matt Pocock

```
MIT License

Copyright (c) Matt Pocock

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
```

Skills in this repo sourced from mattpocock/skills (verified byte-identical `SKILL.md` against
the upstream copy):

- `code-review`
- `codebase-design`
- `diagnosing-bugs`
- `domain-modeling`
- `grill-with-docs`
- `grilling`
- `improve-codebase-architecture`
- `prototype`
- `setup-matt-pocock-skills`
- `to-tickets`
- `tdd` (matches the mattpocock/skills version of `tdd`, not the backnotprop/pstack version, which has different content under the same name)

---

## backnotprop/pstack

- Source: https://github.com/backnotprop/pstack (probable original; several forks exist)
- License: MIT
- License text: https://opensource.org/licenses/MIT
- Copyright holder: Lauren Tan

```
MIT License

Copyright (c) Lauren Tan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
```

Skills in this repo sourced from backnotprop/pstack:

- `unslop` (matches the backnotprop/pstack version; a differently-content `unslop` also exists
  under mattpocock/skills-adjacent collections but was not used here)

Note: `tdd` in this repo does **not** come from pstack, despite pstack also having a skill
named `tdd` with different content — see the mattpocock/skills section above for which version
is actually in use.

---

## obra/superpowers

- Source: https://github.com/obra/superpowers
- License: MIT
- License text: https://opensource.org/licenses/MIT
- Copyright holder: Jesse Vincent

```
MIT License

Copyright (c) Jesse Vincent

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
```

Skills in this repo built on the obra/superpowers framework:

- `write-skills` — its `SKILL.md` explicitly requires `superpowers:test-driven-development` as
  background and references superpowers-only assets (`../using-superpowers/references/
  codex-tools.md`, `gemini-tools.md`), confirming it is adapted from the superpowers
  documentation-writing skill even though no local byte-identical reference copy exists to diff
  against.
- `systematic-debugging` — no local reference copy exists to diff against directly, but
  `write-skills/SKILL.md` names `superpowers:systematic-debugging` as a sibling skill in the
  same framework, and the content ("Iron Law", "NO FIXES WITHOUT ROOT CAUSE INVESTIGATION
  FIRST", phase-gated debugging process) matches the superpowers house style. Classified as
  sourced from obra/superpowers on this basis; flagged for a closer diff against the upstream
  repo before publishing if a copy becomes available.

---

## Imbad0202/academic-research-skills

- Source: https://github.com/Imbad0202/academic-research-skills
- License: CC BY-NC 4.0
- License text: https://creativecommons.org/licenses/by-nc/4.0/
- Copyright holder: Cheng-I Wu
- Required attribution line: "Based on Academic Research Skills by Cheng-I Wu,
  https://github.com/Imbad0202/academic-research-skills"

Skills in this repo built on Imbad0202/academic-research-skills:

- `academic-deep-research`
- `academic-paper`
- `academic-paper-reviewer`
- `academic-pipeline`

These four skills are heavily modified/expanded from the upstream repo (custom agent
pipelines, contracts, schemas), but their internal JSON schema files still declare
`"$id": "https://github.com/Imbad0202/academic-research-skills/..."` as their canonical
namespace (125-126 files per skill), and `academic-deep-research/shared/
collaboration_depth_rubric.md` explicitly names `Imbad0202/academic-research-skills` as its
canonical upstream location. This is a clear, first-party declaration of lineage from the
skills themselves, not an inference from file names — attribution is required.

### Related but not directly attributed

- `academic-graphlookup` It operates downstream of `academic-deep-research`'s output
  (`docs/academic-research/corpus/`, `passport.yaml`, `citegraph.html`) but has its own
  independent `config.json`, its own citation-crawling logic (OpenAlex + Semantic Scholar), and
  its own SQLite-backed scripts (`crawl.py`, `classify_relevance.py`, `export_graph_data.py`,
  `record_citation_count.py`). Treated as the user's own derivative work built to extend
  `academic-deep-research`'s output format, not a direct copy or adaptation of upstream
  academic-research-skills content. Because it consumes data produced by a skill that does
  carry CC BY-NC obligations, a courtesy attribution line pointing back to
  `academic-deep-research`'s notice would not hurt, but is not treated as strictly required
  here — flagged for the user's own judgment call before publishing.

---

## affaan-m/ECC

- Source: https://github.com/affaan-m/ECC (skills live under its `skills/` directory)
- License: MIT
- License text: https://opensource.org/licenses/MIT
- Copyright holder: Affaan Mustafa (2026)

```
MIT License

Copyright (c) 2026 Affaan Mustafa

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
```

Skills in this repo sourced from affaan-m/ECC:

- `python-patterns`
- `python-testing`

---

## blader/humanizer

- Source: https://github.com/blader/humanizer
- License: MIT
- License text: https://opensource.org/licenses/MIT
- Copyright holder: Siqi Chen (2025)

```
MIT License

Copyright (c) 2025 Siqi Chen

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

Skills in this repo built on blader/humanizer:

- `humanizer`

This skill was renamed from `humanizer` to `humanize`
---


## blader/humanizer

- Source: https://github.com/brigealong/scihub-dl
- License: MIT
- License text: https://opensource.org/licenses/MIT
- Copyright holder: brigealong (2026)

```
MIT License

Copyright (c) 2026 brigealong

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

Skills in this repo built on blader/scihub-dl:

- `academic-scihub-dl`

The skill was renamed to contain the word `academic` and a prompt was injected to have more succes when calling it.

---
