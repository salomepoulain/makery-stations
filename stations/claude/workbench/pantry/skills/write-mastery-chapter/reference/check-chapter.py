#!/usr/bin/env python3
"""Checks a finished chapter .tex against the skill's two hard rules.

usage: python3 check-chapter.py <name>-chapter.tex [<name>-coverage.md]

1. Solutions are extensive. Every \\sol{...} is measured and the short ones are listed by exercise type (see "Solutions: how extensive"
   in pedagogy-cycle.md). A solution below the threshold is not always wrong, but every one on the list must be looked at.
2. Every in-scope source question is in the chapter. The coverage file is a markdown table, one row per source question part:
   | source part | in or out | where in the chapter | solution compared | reason (required when out) |
   The first cell must be the label used in the chapter, exactly as written in \\srcref{...}, \\extags{...} or \\diagnums{...}.
   In-scope rows must have a matching label in the chapter, and every label in the chapter must have a row.
"""
import os, re, sys, statistics

# minimum length (characters of source, whitespace collapsed) below which a solution is listed, per exercise type
THRESH = {'O': 200, 'T': 200, 'D': 150, 'V': 300, 'E': 450, 'C': 450, 'R': 300, 'P': 150, 'Z': 300}
NAMES = {'O': 'Orient', 'T': 'Test', 'D': 'Drill', 'V': 'Visualize', 'E': 'Exam', 'C': 'Challenge', 'R': 'Reflect', 'P': 'Prior', 'Z': 'Diagnostic'}


def group(t, k):
    d = 0
    for j in range(k, len(t)):
        c = t[j]
        if c == '{' and t[j - 1] != '\\':
            d += 1
        elif c == '}' and t[j - 1] != '\\':
            d -= 1
            if d == 0:
                return j
    return len(t) - 1


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    src = open(sys.argv[1]).read()
    body = src[src.index('\\begin{document}'):]
    structural_problems = 0
    cur = '?'
    sols = []
    for m in re.finditer(r'\\item\[([^\]\n]*)\]|\\sol\{', body):
        if m.group(0).startswith('\\sol'):
            e = group(body, m.end() - 1)
            raw = body[m.end():e]
            text = re.sub(r'\s+', ' ', raw)
            sols.append((cur, body.count('\n', 0, m.start()) + 1, len(text), text, raw))
        else:
            lab = m.group(1)
            b = re.search(r'\\([A-Z])badge', lab)
            if b:
                cur = b.group(1)
            elif 'priornum' in lab:
                cur = 'P'
            elif 'diagnum' in lab:
                cur = 'Z'
    print('SOLUTIONS')
    flagged = []
    for k in 'OTDVECRPZ':
        L = [s for s in sols if s[0] == k]
        if not L:
            continue
        lens = [s[2] for s in L]
        short = [s for s in L if s[2] < THRESH[k]]
        flagged += short
        print('  %-10s %4d solutions, median %4d characters, %4d under %d' % (NAMES[k], len(L), statistics.median(lens), len(short), THRESH[k]))
    print('  Only a bare final answer (under 40 characters): %d' % sum(1 for s in sols if s[2] < 40))
    print('  Solutions listed for review (under the threshold of their type): %d of %d' % (len(flagged), len(sols)))
    for k, line, n, text, raw in flagged[:40]:
        print('    line %5d  %s  %3d  %s' % (line, k, n, text[:70]))
    if len(flagged) > 40:
        print('    ... %d more' % (len(flagged) - 40))

    # dense solutions: long enough to be a real multi-step derivation, but no align*/display line break at all
    # (pedagogy-cycle.md, "Presentation convention for solutions and derivations": every step gets its own line)
    DENSE_FLOOR = 250
    dense = [s for s in sols if s[2] > DENSE_FLOOR and not re.search(r'align\*|\\\[|\$\$', s[4])]
    print('  Dense solutions (over %d characters, no align*/display line break): %d of %d' % (DENSE_FLOOR, len(dense), len(sols)))
    for cur, line, n, text, raw in dense[:20]:
        print('    line %5d  %s  %3d  %s' % (line, cur, n, text[:70]))
    if len(dense) > 20:
        print('    ... %d more' % (len(dense) - 20))

    # visuals per paragraph: V exercises (rule: 2 to 4) and tikz pictures
    paras = [(m.start(), m.group(1), m.group(2)) for m in re.finditer(r'\\parasection\{(\d+)\}\{([^}]*)\}', body)]
    if paras:
        print('\nVISUALS per paragraph')
        for i, (pos, num, title) in enumerate(paras):
            seg = body[pos:paras[i + 1][0] if i + 1 < len(paras) else len(body)]
            nv = len(re.findall(r'\\item\[[^\]\n]*\\Vbadge', seg))
            nf = len(re.findall(r'\\begin\{tikzpicture\}', seg))
            print('  section %s %-44s %2d V exercises, %2d pictures%s' % (num, title[:44], nv, nf, '   <-- under 2 V: the plan must give the reason' if nv < 2 else ''))

    # Theory block density: one claim per block (see "How much goes in one Theory block" in pedagogy-cycle.md)
    blocks = [(m.start(), m.group(1), m.group(2)) for m in re.finditer(r'\\begin\{theorybox\}\{([A-Z]): ([^}]*)\}', body)]
    if blocks:
        print('\nTHEORY BLOCK DENSITY')
        for i, (pos, letter, title) in enumerate(blocks):
            e = body.find('\\end{theorybox}', pos)
            if e == -1:
                continue
            e = body.find('\n', e) if body.find('\n', e) != -1 else len(body)
            seg = body[pos:e]
            nw = len(seg.split())
            nf = len(re.findall(r'\\begin\{tikzpicture\}', seg))
            flag = nw > 700 or nf > 2
            print('  Theory %s %-40s %4d words, %d pictures%s' % (letter, title[:40], nw, nf, '   <-- check for a second claim' if flag else ''))

    # exercise run per Theory block: the taxonomy floor (pedagogy-cycle.md, "Exercise taxonomy" and
    # "The plain-practice row is not a suggestion"), not just the V floor. A block's run is measured from
    # its \begin{theorybox} to the next one (or the paragraph's Review), so it includes the run after the box.
    if blocks:
        print('\nEXERCISE RUN per Theory block  (floor: D >= 3 families, pedagogy-cycle.md "3 to 4 per Theory block"; O and C are used where the block calls for them, not every block)')
        blocks_without_c = []
        for i, (pos, letter, title) in enumerate(blocks):
            e = blocks[i + 1][0] if i + 1 < len(blocks) else len(body)
            seg = body[pos:e]
            tags = re.findall(r'\\extag\{\\([A-Z])badge\}|\\extags\{[^}]*\}\{\\([A-Z])badge\}', seg)
            flat = [a or b for a, b in tags]
            cnt = {k: flat.count(k) for k in 'OTDVECR'}
            flag = cnt['D'] < 3
            if cnt['C'] == 0:
                blocks_without_c.append((letter, title))
            print('  Theory %s %-40s O%d T%d D%d V%d E%d C%d R%d%s' % (
                letter, title[:40], cnt['O'], cnt['T'], cnt['D'], cnt['V'], cnt['E'], cnt['C'], cnt['R'],
                '   <-- D under 3: not a finished exercise run' if flag else ''))
        allflat = [a or b for a, b in re.findall(r'\\extag\{\\([A-Z])badge\}|\\extags\{[^}]*\}\{\\([A-Z])badge\}', body)]
        if allflat.count('C') == 0:
            print('  BUG: chapter has 0 Challenge (C) exercises total; full mastery needs edge-case/depth exercises unless the user explicitly waived them')
            structural_problems += 1
        elif len(blocks_without_c) > max(2, len(blocks) // 2):
            print('  REVIEW: %d of %d Theory blocks have no Challenge exercise; check edge cases were not skipped' % (len(blocks_without_c), len(blocks)))

    print('\nMASTERY DEPTH')
    prior_blocks = [(m.start(), m.group(1), m.group(2)) for m in re.finditer(r'\\begin\{priorbox\}\{([A-Z]): ([^}]*)\}', body)]
    if prior_blocks:
        for i, (pos, letter, title) in enumerate(prior_blocks):
            e = prior_blocks[i + 1][0] if i + 1 < len(prior_blocks) else (paras[0][0] if paras else len(body))
            seg = body[pos:e]
            np = len(re.findall(r'\\item\[\\priornum\]', seg))
            print('  Prior %s %-40s %2d practice items%s' % (
                letter, title[:40], np, '   <-- under 3: prerequisite may not be fluent' if np < 3 else ''))
    else:
        print('  no Prior boxes found')
    if blocks:
        no_visual = []
        for pos, letter, title in blocks:
            e = body.find('\\end{theorybox}', pos)
            if e == -1:
                continue
            seg = body[pos:e]
            has_visual = bool(re.search(r'\\begin\{tikzpicture\}|\\begin\{axis\}|\\begin\{center\}|\\includegraphics|\\gridpic|\\.*pic\{', seg))
            if not has_visual:
                no_visual.append((letter, title))
        if no_visual:
            print('  REVIEW: %d Theory blocks have no detectable in-Theory visual/concrete diagram hook' % len(no_visual))
            print('    ' + ', '.join('%s:%s' % (letter, title[:22]) for letter, title in no_visual[:12]))
            if len(no_visual) > 12:
                print('    ... %d more' % (len(no_visual) - 12))
        else:
            print('  OK: every Theory block has a detectable visual/concrete hook')

    # Legend structure: the taxonomy transcription must match latex-scaffolding.md's canonical template exactly,
    # not a paraphrase and not the old stale template it replaced.
    m = re.search(r'\\frontsection\{Legend\}(.*?)\\clearpage', body, re.S)
    if m:
        leg = m.group(1)
        print('\nLEGEND STRUCTURE')
        letters = re.findall(r'\\legletter\{\\c([A-Z])\}\{([A-Z])\}', leg)
        expected = list('POTDVECR')
        got = [b for _, b in letters]
        if got == expected:
            print('  OK: all 8 badges present via \\legletter, in order P O T D V E C R')
        else:
            print('  MISMATCH: found %s via \\legletter, expected %s' % (''.join(got) or '(none)', ''.join(expected)))
            print('  <-- the Legend must use \\legletter{\\cX}{X} for all eight badges, in this order; it must not be a')
            print('      \\begin{description}\\item[\\Xbadge ...] list (that is the old, stale structure)')
        if '\\Abadge' in leg:
            print('  BUG: \\Abadge used (undefined macro, leftover from the old stale template)')
        if 'no badge' in leg.lower():
            print('  BUG: "(no badge)" text found (leftover from the old stale template; Drill uses \\Dbadge)')
        for needed in ['\\legchap', '\\pillgroup', '\\legpnum', '\\legpage', '\\legbox']:
            if needed not in leg:
                print('  missing %s (part of the canonical template in latex-scaffolding.md)' % needed)
        canonical_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'legend-template.tex')
        if os.path.exists(canonical_path):
            chapter_legend = m.group(0)
            chapter_legend = re.sub(r'\s+', ' ', chapter_legend).strip()
            chapter_legend = re.sub(r'\s*\\clearpage\s*$', '', chapter_legend).strip()
            canonical = open(canonical_path).read()
            canonical = re.sub(r'\s+', ' ', canonical).strip()
            if chapter_legend == canonical:
                print('  OK: Legend matches reference/legend-template.tex exactly apart from whitespace')
            else:
                print('  BUG: Legend differs from reference/legend-template.tex; copy the locked Legend verbatim')
                structural_problems += 1
    else:
        print('\nLEGEND STRUCTURE: no \\frontsection{Legend}...\\clearpage found, could not check')
        structural_problems += 1

    print('\nOPENING STRUCTURE')
    opening_marks = [
        ('chapter title', body.find('\\chaptertitle')),
        ('Contents', body.find('\\tableofcontents')),
        ('Legend', body.find('\\frontsection{Legend}')),
        ('Prior knowledge', body.find('\\begin{priorsection}')),
    ]
    missing = [name for name, pos in opening_marks if pos == -1]
    if missing:
        print('  MISSING: %s' % ', '.join(missing))
        structural_problems += len(missing)
    elif not (opening_marks[0][1] < opening_marks[1][1] < opening_marks[2][1] < opening_marks[3][1]):
        print('  BUG: expected order is title/introduction, Contents, Legend, Prior knowledge')
        structural_problems += 1
    else:
        print('  OK: title, Contents, Legend, Prior knowledge are in the house order')

    toc_wrapper = re.search(r'\\begingroup\s*\\hypersetup\{linkcolor=black\}\s*\\tableofcontents\s*\\endgroup', body)
    if toc_wrapper:
        print('  OK: Contents uses the black-link wrapper')
    else:
        print('  BUG: Contents must be wrapped in \\begingroup \\hypersetup{linkcolor=black} ... \\endgroup')
        structural_problems += 1

    ppos = body.find('\\begin{priorsection}')
    if ppos != -1:
        prior_opening = body[ppos:ppos + 800]
        if '\\priortitle' not in prior_opening:
            print('  BUG: Prior knowledge starts without \\priortitle')
            structural_problems += 1
        if '\\addtocontents{toc}{\\protect\\dcrowflat{0}}' in prior_opening:
            print('  OK: Prior knowledge registers its Contents pills with \\dcrowflat{0}')
        else:
            print('  BUG: Prior knowledge must add \\addtocontents{toc}{\\protect\\dcrowflat{0}} after \\priortitle')
            structural_problems += 1
    spos = body.find('\\frontsection{Summary}')
    if spos != -1:
        summary_opening = body[spos:spos + 500]
        if '\\addtocontents{toc}{\\protect\\dcsnake}' in summary_opening:
            print('  OK: Summary registers its Theory-letter snake with \\dcsnake')
        else:
            print('  BUG: Summary must add \\addtocontents{toc}{\\protect\\dcsnake} after \\frontsection{Summary}')
            structural_problems += 1
    dpos = body.find('\\frontsection{Diagnostic check}')
    if dpos != -1:
        diag_opening = body[dpos:dpos + 600]
        if re.search(r'\\addtocontents\{toc\}\{\\protect\\dcdiagrow\{D\d+(?:,D\d+)*\}\}', diag_opening):
            print('  OK: Diagnostic check registers its number pills with \\dcdiagrow{...}')
        else:
            print('  BUG: Diagnostic check must add \\addtocontents{toc}{\\protect\\dcdiagrow{D1,...}} after its heading')
            structural_problems += 1

    # pointers to earlier chapters
    import glob
    pf = re.findall(r'\\priorfrom\{[^}]*chapter (\d+), Theory ([A-Z])', body)
    if pf:
        print('\nEARLIER CHAPTERS')
        d = os.path.dirname(os.path.abspath(sys.argv[1]))
        for mch, letter in sorted(set(pf)):
            cands = [f for f in glob.glob(os.path.join(d, '*-chap%s-*chapter.tex' % mch)) if os.path.abspath(f) != os.path.abspath(sys.argv[1])]
            ok = any(re.search(r'\\begin\{theorybox\}\{%s:' % letter, open(f).read()) for f in cands)
            print('  chapter %s, Theory %s: %s' % (mch, letter, 'found' if ok else 'NOT FOUND in ' + (', '.join(os.path.basename(f) for f in cands) or 'no earlier chapter file next to this one')))

    # source labels used in the chapter
    used = set(re.findall(r'\\srcref\{([^}]*)\}', body)) | set(re.findall(r'\\extags\{([^}]*)\}', body)) | set(re.findall(r'\\diagnums\{([^}]*)\}', body))
    print('\nSOURCE LABELS in the chapter: %d distinct' % len(used))
    problems = 0
    if len(sys.argv) > 2:
        rows = {}
        for line in open(sys.argv[2]):
            if not line.startswith('|'):
                continue
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            if len(cells) < 3 or set(cells[0]) <= set('-: '):
                continue
            if cells[0].lower() in ('source part', 'source', 'part'):
                continue
            rows[cells[0]] = cells
        print('COVERAGE FILE: %d rows' % len(rows))
        for key, c in rows.items():
            scope = c[1].lower()
            if scope.startswith('in'):
                if key not in used:
                    print('  MISSING in the chapter: %s' % key)
                    problems += 1
                if len(c) > 3 and c[3].lower() in ('', 'no', 'not yet'):
                    print('  SOLUTION NOT COMPARED: %s' % key)
                    problems += 1
            else:
                if len(c) < 5 or not c[4]:
                    print('  OUT OF SCOPE WITHOUT A REASON: %s' % key)
                    problems += 1
        for key in sorted(used - set(rows)):
            print('  IN THE CHAPTER BUT NOT IN THE COVERAGE FILE: %s' % key)
            problems += 1
        print('  coverage problems: %d' % problems)
    else:
        print('(no coverage file given: the source coverage was not checked)')
    if structural_problems:
        print('STRUCTURAL PROBLEMS: %d' % structural_problems)
    sys.exit(1 if problems or structural_problems else 0)


main()
