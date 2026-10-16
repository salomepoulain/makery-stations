"""Convert a session-mode mastery chapter (.tex) into the clickable HTML version.

Usage: python3 tex2html.py <chapter-folder> <out.html>
Reads <name>.tex and <name>-answers.aux in the folder, and website-template.html + chapter.css next to this script.
Figures (tikz/pgfplots) are compiled with pdflatex into one PDF, one figure per page, and embedded as SVG.
"""
import base64, html, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
FOLDER = os.path.abspath(sys.argv[1])
OUT = sys.argv[2]
NAME = os.path.basename(FOLDER)
TEX = open(os.path.join(FOLDER, NAME + '.tex')).read()
AUX = open(os.path.join(FOLDER, NAME + '-answers.aux')).read()
TPL = open(os.path.join(HERE, 'website-template.html')).read()

# ---------------------------------------------------------------- low-level LaTeX reading
def strip_comments(s):
    return re.sub(r'(?<!\\)%[^\n]*', '', s)

def skipws(s, i):
    while i < len(s) and s[i] in ' \t\n':
        i += 1
    return i

def group(s, i, o='{', c='}'):
    """s[i] must be o; return (content, index after closing)."""
    assert s[i] == o, (s[i:i + 40])
    d, j = 0, i
    while j < len(s):
        ch = s[j]
        if ch == '\\':
            j += 2
            continue
        if ch == o:
            d += 1
        elif ch == c:
            d -= 1
            if d == 0:
                return s[i + 1:j], j + 1
        j += 1
    raise ValueError('unbalanced ' + s[i:i + 60])

def arg(s, i):
    i = skipws(s, i)
    if i < len(s) and s[i] == '{':
        return group(s, i)
    return s[i], i + 1  # single token

def optarg(s, i):
    j = skipws(s, i)
    if j < len(s) and s[j] == '[':
        return group(s, j, '[', ']')
    return None, i

def env_end(s, i, name):
    """i just after \\begin{name}; return (content, index after \\end{name})."""
    d, j = 1, i
    pat = re.compile(r'\\(begin|end)\{' + re.escape(name) + r'\}')
    while True:
        m = pat.search(s, j)
        if not m:
            raise ValueError('no end for ' + name)
        d += 1 if m.group(1) == 'begin' else -1
        if d == 0:
            return s[i:m.start()], m.end()
        j = m.end()

def split_top(s, word):
    """Split s at top-level occurrences of \\word (not inside braces or nested environments)."""
    parts, d, envd, j, last = [], 0, 0, 0, 0
    while j < len(s):
        ch = s[j]
        if ch == '\\':
            if s.startswith('\\begin{', j):
                envd += 1
            elif s.startswith('\\end{', j):
                envd -= 1
            elif d == 0 and envd == 0 and s.startswith('\\' + word, j) and not s[j + 1 + len(word):j + 2 + len(word)].isalpha():
                parts.append(s[last:j])
                last = j + 1 + len(word)
            j += 2
            continue
        if ch == '{':
            d += 1
        elif ch == '}':
            d -= 1
        j += 1
    parts.append(s[last:])
    return parts

def esc_math(m):
    return m.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

# ---------------------------------------------------------------- state
B1, B2, PB = '\x01', '\x02', '\x03'   # block start, block end, paragraph break
st = {'ex': 0, 'prior': 0, 'diag': 0, 'terms': set(), 'figs': [], 'reviews': {}, 'para': None}
FIGDEFS = []
DOCSTART = TEX.index('\\begin{document}')
DEFNAMES = set()
for m in re.finditer(r'\\def\\([A-Za-z]+)', TEX[DOCSTART:]):  # figure macros defined in the body, e.g. \def\bbox#1{...}
    st0 = DOCSTART + m.start()
    body, e = group(TEX, TEX.index('{', st0 + 4))
    FIGDEFS.append(TEX[st0:e]); DEFNAMES.add(m.group(1))

def block(h):
    return B1 + h + B2

def paras(h):
    out = []
    for k, seg in enumerate(re.split('(' + B1 + '.*?' + B2 + ')', h, flags=re.S)):
        if seg.startswith(B1):
            out.append(seg[1:-1])
            continue
        for p in seg.split(PB):
            p = p.strip()
            if p:
                out.append('<p>' + p + '</p>')
    return '\n'.join(out)

def key(t):
    return re.sub(r'\s+', '', re.sub(r'<[^>]+>', '', t)).lower()

# ---------------------------------------------------------------- figures
def figure(src, vfill):
    st['figs'].append(('\\vfilltrue ' if vfill else '\\vfillfalse ') + src.strip())
    return block('<div class="fig">@@FIG%d@@</div>' % (len(st['figs']) - 1))

def build_figs():
    if not st['figs']:
        return []
    bd = os.path.join(FOLDER, 'html-build')
    os.makedirs(bd, exist_ok=True)
    pre = TEX[:TEX.index('\\begin{document}')]
    doc = pre + '\\begin{document}\\setchapter{%s}\\gdef\\thischap{%s}\n' % (CHAP, CHAP) + '\n'.join(FIGDEFS) + '\n'
    doc += '\\hoffset=-1in \\voffset=-1in \\newbox\\fb\n\\def\\emitfig#1{\\setbox\\fb\\vbox{\\kern3pt\\hbox{\\kern3pt#1\\kern3pt}\\kern3pt}\\pdfpagewidth=\\wd\\fb \\pdfpageheight=\\dimexpr\\ht\\fb+\\dp\\fb\\relax \\shipout\\box\\fb}\n'
    for f in st['figs']:
        doc += '\\emitfig{' + f + '}\n'
    doc += '\\end{document}\n'
    open(os.path.join(bd, 'figs.tex'), 'w').write(doc)
    env = dict(os.environ, TEXINPUTS=FOLDER + '//:' + os.environ.get('TEXINPUTS', ''))
    r = subprocess.run(['pdflatex', '-interaction=nonstopmode', 'figs.tex'], cwd=bd, env=env, capture_output=True, text=True)
    if not os.path.exists(os.path.join(bd, 'figs.pdf')):
        sys.exit('figure build failed:\n' + r.stdout[-2000:])
    out = []
    for i in range(len(st['figs'])):
        svgp = os.path.join(bd, 'fig%d.svg' % i)
        subprocess.run(['pdftocairo', '-svg', '-f', str(i + 1), '-l', str(i + 1), 'figs.pdf', svgp], cwd=bd, check=True)
        svg = open(svgp).read()
        w = re.search(r'width="([\d.]+)(pt)?"', svg).group(1)
        out.append('<img alt="figure" style="width:%spt" src="data:image/svg+xml;base64,%s">' % (w, base64.b64encode(svg.encode()).decode()))
    return out

# ---------------------------------------------------------------- text conversion
INLINE = {'textbf': ('<b>', '</b>'), 'extitle': ('<b>', '</b>'), 'emph': ('<i>', '</i>'), 'textit': ('<i>', '</i>'),
          'mbox': ('', ''), 'text': ('', ''), 'small': ('', ''), 'upshape': ('', '')}
DROP0 = {'noindent', 'smallskip', 'medskip', 'bigskip', 'clearpage', 'nopagebreak', 'centering', 'relax',
         'ignorespaces', 'protect', 'itshape', 'raggedright', 'vfillfalse', 'priortitle', 'mbtight'}
DROP1 = {'needspace', 'pagecolor', 'label', 'hspace', 'vspace', 'hypersetup', 'setchapter'}
SYM = {'S': '&sect;', 'enspace': '&ensp;', 'quad': '&emsp;', 'qquad': '&emsp;&emsp;', 'ldots': '&hellip;',
       'dots': '&hellip;', '%': '%', '&': '&amp;', '_': '_', '#': '#', ',': '&thinsp;', ' ': ' ', '\\': '<br>',
       '{': '{', '}': '}', '$': '$', 'par': PB}

def conv(s, ctx):
    o, i, n = [], 0, len(s)
    vfill = ctx.get('vfill', False)
    while i < n:
        ch = s[i]
        if s.startswith('\\(', i):
            j = s.index('\\)', i)
            o.append(esc_math(s[i:j + 2])); i = j + 2; continue
        if s.startswith('\\[', i):
            j = s.index('\\]', i)
            o.append(block('<div class="disp">' + esc_math(s[i:j + 2]) + '</div>')); i = j + 2; continue
        if ch == '\\':
            m = re.match(r'\\([A-Za-z@]+)\*?|\\(.)', s[i:])
            name = m.group(1) or m.group(2)
            i += m.end()
            if name in SYM:
                o.append(SYM[name]); continue
            if name in DROP0:
                continue
            if name in DROP1:
                _, i = arg(s, i); continue
            if name in INLINE:
                if name in ('small', 'upshape'):
                    continue
                a, i = arg(s, i)
                o.append(INLINE[name][0] + conv(a, ctx) + INLINE[name][1]); continue
            if name == 'addtocontents':
                _, i = arg(s, i); _, i = arg(s, i); continue
            if name == 'gdef':
                _, i = arg(s, i); _, i = arg(s, i); continue
            if name == 'def':
                j = s.index('{', i); _, i = group(s, j); continue
            if name == 'vfilltrue':
                vfill = ctx['vfill'] = True; continue
            if name == 'newterm':
                a, i = arg(s, i); t = conv(a, ctx); k = key(t)
                idattr = '' if k in st['terms'] else ' id="term-%s"' % k
                st['terms'].add(k)
                o.append('<b class="newterm"%s>%s</b>' % (idattr, t)); continue
            if name == 'secref':
                a, i = arg(s, i); o.append('<a href="#sec%s">&sect;%s</a>' % (a, a)); continue
            if name == 'thyref':
                a, i = arg(s, i); b, i = arg(s, i)
                o.append('<a href="#th-%s">&sect;%s Theory %s</a>' % (b, a, b)); continue
            if name == 'pthyref':
                a, i = arg(s, i); o.append('<a href="#th-P%s">Prior knowledge Theory %s</a>' % (a, a)); continue
            if name == 'scenario':
                a, i = arg(s, i); o.append(PB + conv(a, ctx) + PB); continue
            if name == 'priorgroup':
                a, i = arg(s, i); o.append(block('<div class="pgroup">%s</div>' % conv(a, ctx))); continue
            if name == 'priorfrom':
                a, i = arg(s, i); o.append(block('<div class="pfrom">%s</div>' % conv(a, ctx))); continue
            if name == 'sumhead':
                a, i = arg(s, i); o.append(block('<h3 class="sumhead">%s</h3>' % conv(a, ctx))); continue
            if name == 'sol':
                a, i = arg(s, i); o.append(block(solution(a, dict(ctx)))); continue
            if name == 'hint':
                a, i = arg(s, i); o.append(block(hint(a, ctx))); continue
            if name == 'review':
                args = []
                for _ in range(4):
                    a, i = arg(s, i); args.append(a)
                st['reviews'][args[0]] = args[1:]
                o.append(block('<div class="review"><div class="rv-t">Review</div>%s</div>' % review_body(args[1:], False, ctx))); continue
            if name == 'rvsummary':
                a, i = arg(s, i); h, i = arg(s, i); src, i = arg(s, i)
                o.append(block('<div class="rvsum"><h3 class="sumhead">%s</h3><p>Source: %s</p>%s</div>' % (conv(h, ctx), conv(src, ctx), review_body(st['reviews'][a], True, ctx)))); continue
            if name == 'begin':
                e, i = arg(s, i)
                h, i = environment(e, s, i, ctx)
                o.append(h); continue
            if name in ('workedheading', 'workedanswer', 'wpart'):
                o.append({'workedheading': '', 'workedanswer': '', 'wpart': '<br>'}[name]); continue
            if name in DEFNAMES:
                continue
            if name == 'qa':
                q, i = arg(s, i); a, i = arg(s, i)
                st['qa'] = st.get('qa', 0) + 1
                o.append(block('<div class="qa" id="qa-%d"><div class="qa-head"><button class="lnk qa-toggle" type="button" aria-expanded="true"><b>Question.</b> <i>%s</i></button><button class="lnk qa-del" type="button" title="Remove this question">remove</button></div><div class="qa-body">%s</div></div>' % (st['qa'], conv(q, ctx), paras(conv(a, ctx)))))
                continue
            o.append('\\' + name)  # unknown: keep visible so it gets noticed
            continue
        if ch == '\n':
            m = re.match(r'\n[ \t]*\n\s*', s[i:])
            if m:
                o.append(PB); i += m.end(); continue
        if ch == '~':
            o.append('&nbsp;'); i += 1; continue
        if s.startswith('``', i):
            o.append('&ldquo;'); i += 2; continue
        if s.startswith("''", i):
            o.append('&rdquo;'); i += 2; continue
        if s.startswith('---', i):
            o.append('&mdash;'); i += 3; continue
        if s.startswith('--', i):
            o.append('&ndash;'); i += 2; continue
        if ch in '{}':
            i += 1; continue
        o.append(html.escape(ch, quote=False)); i += 1
    return ''.join(o)

def environment(e, s, i, ctx):
    opt, i = optarg(s, i)
    if e in ('theorybox', 'priorbox'):
        t, i = arg(s, i); k, i = arg(s, i)
    body, i = env_end(s, i, e)
    if e in ('theorybox', 'priorbox'):
        letter = t.split(':')[0].strip()
        hid = ('th-P' if e == 'priorbox' else 'th-') + letter
        word = 'Prior' if e == 'priorbox' else 'Theory'
        return block('<div class="thy" id="%s"><div class="thy-t">%s %s</div>%s</div>' % (hid, word, conv(t, ctx), paras(conv(body, ctx)))), i
    if e == 'theorycont':
        return block('<div class="thy cont">%s</div>' % paras(conv(body, ctx))), i
    if e == 'recipebox':
        return block('<div class="recipe">%s</div>' % paras(conv(body, ctx))), i
    if e == 'workedbox':
        q, _, a = body.partition('\\workedanswer')
        q = q.replace('\\workedheading', '')
        return block('<div class="worked"><b>Worked example</b><div class="wq">%s</div><hr>%s</div>' % (paras(conv(q, ctx)), paras(conv(a, ctx)))), i
    if e == 'center':
        if 'tikzpicture' in body or (DEFNAMES and re.search(r'\\(' + '|'.join(DEFNAMES) + r')\b', body)):
            return figure(body, ctx.get('vfill', False)), i
        return block('<div class="center">%s</div>' % paras(conv(body, ctx))), i
    if e == 'itemize':
        items = [x for x in split_top(body, 'item')[1:]]
        return block('<ul>%s</ul>' % ''.join('<li>%s</li>' % paras(conv(x, ctx)) for x in items)), i
    if e == 'enumerate':
        if opt:  # a plain numbered list (recipe steps)
            items = split_top(body, 'item')[1:]
            return block('<ol class="steps">%s</ol>' % ''.join('<li>%s</li>' % paras(conv(x, ctx)) for x in items)), i
        return exercises(body, ctx), i
    if e == 'summarybox':
        return block('<div class="sumcols">%s</div>' % paras(conv(body, ctx))), i
    if e in ('cases', 'tikzpicture', 'axis'):
        return block('<div class="disp">%s</div>' % esc_math(body)), i
    return paras(conv(body, ctx)), i

# ---------------------------------------------------------------- exercises
BADGE = re.compile(r'\\([PODTVECR])badge')

def exercises(body, ctx):
    level = ctx.get('level', 0)
    items = split_top(body, 'item')
    out = []
    for k, it in enumerate(items[1:]):
        opt, j = optarg(it, 0)
        content = it[j:]
        c2 = dict(ctx, level=level + 1)
        if level == 0:
            out.append(exercise(opt or '', content, c2))
        else:
            out.append(part(chr(ord('a') + k), content, c2))
    return block('\n'.join(out))

def exercise(opt, content, ctx):
    src, tag, label = None, '', ''
    m = re.match(r'\\extags\{([^}]*)\}', opt)
    if m:
        src = m.group(1)
    b = BADGE.search(opt)
    if b:
        st['ex'] += 1
        n, t = st['ex'], b.group(1)
        hid = 'ex-%d' % n
        pill = '<span class="pill %s"><span class="l">%s</span><span class="n">%d</span></span>' % (t, t, n)
        tag = '<span class="tag">%s</span>' % (('<span class="cap"><span class="s">%s</span>%s</span>' % (html.escape(src), pill)) if src else pill)
        label = src or 'Ex %d' % n
    elif 'priornum' in opt:
        st['prior'] += 1
        hid = 'ex-P%d' % st['prior']
        tag = '<span class="pnumber">%d</span>' % st['prior']
        label = 'Prior %d' % st['prior']
    else:  # diagnum / diagnums
        st['diag'] += 1
        m = re.match(r'\\diagnums\{([^}]*)\}', opt)
        hid = 'ex-Z%d' % st['diag']
        tag = '<span class="pnumber diag">%d</span>' % st['diag']
        if m:
            tag = '<span class="tag"><span class="chev">%s</span></span>' % html.escape(m.group(1)) + tag
        label = 'Diag %d' % st['diag']
    inner, mc = mcq(content, ctx)
    return '<div class="ex%s" id="%s" data-id="%s"%s>%s%s</div>' % (' mc' if mc else '', hid, html.escape(label), mc, tag, inner)

def part(letter, content, ctx):
    arrow = ''
    m = re.match(r'\s*\\srcref\{([^}]*)\}', content)
    if m:
        arrow = '<span class="srcarrow"><span class="chev">%s</span></span>' % html.escape(m.group(1))
        content = content[m.end():]
    inner, mc = mcq(content, ctx)
    return '<div class="part%s"%s>%s<span class="lbl">(%s)</span>%s</div>' % (' mc' if mc else '', mc, arrow, letter, inner)

def mcq(content, ctx):
    """Exercise or part text; when it has \\opt options, stack them and make them checkable."""
    if '\\opt{' not in content:
        return paras(conv(content, ctx)), ''
    first = content.index('\\opt{')
    stops = [p for p in (content.find('\\hint{', first), content.find('\\sol{', first)) if p >= 0]
    end = min(stops) if stops else len(content)
    stem, opts, rest = content[:first], content[first:end], content[end:]
    oh = []
    for piece in opts.split('\\opt{')[1:]:
        letter, txt = piece.split('}', 1)
        oh.append('<p class="opt" data-k="%s"><span class="mark"></span><span class="ol">(%s)</span>%s</p>' % (letter, letter, conv(txt.strip(), ctx)))
    correct = None
    ms = re.search(r'\\sol\{', rest)
    if ms:
        sol, _ = group(rest, ms.end() - 1)
        head = re.split(r'\\par|\n\s*\n|\.\s', sol, maxsplit=1)[0]
        letters = re.findall(r'\(([a-f])\)', head)
        if letters:
            correct = letters
        elif re.search(r'\bnone\b', head, re.I):
            correct = []
    h = paras(conv(stem, ctx)) + '\n<div class="opts">' + ''.join(oh) + '</div>\n'
    rh = paras(conv(rest, dict(ctx, mc=correct is not None)))
    if correct is None:
        return h + rh, ''
    return h + rh, ' data-correct="%s"' % ','.join(correct)

def hint(a, ctx):
    pieces = [p.strip() for p in re.split(r'(?=\(\d\)\s)', a) if p.strip()]
    hs = [conv(p, ctx) for p in pieces]
    data = json.dumps(hs, ensure_ascii=False).replace('&', '&amp;').replace("'", '&#39;')
    return '<div class="hint" data-hints=\'%s\'><div class="ht" hidden><i>Hint.</i><span class="hs"></span></div><button class="hbar nexthint" type="button"></button></div>' % data

# ---------------------------------------------------------------- solutions as step chains
REL = re.compile(r'^\s*(=|\\approx|\\le\b|\\ge\b|\\ne\b|<|>|\\propto|\\Rightarrow|\\Longrightarrow|\\iff)')

def split_rel(m):
    if REL.match(m):
        return '', m.strip()
    d, j = 0, 0
    while j < len(m):
        ch = m[j]
        if ch == '\\':
            if d == 0 and re.match(r'\\(approx|propto)\b', m[j:]):
                return m[:j].strip(), m[j:].strip()
            j += 2; continue
        if ch in '{(':
            d += 1
        elif ch in '})':
            d -= 1
        elif ch == '=' and d == 0:
            return m[:j].strip(), m[j:].strip()
        j += 1
    return '', m.strip()

def last_sentence(t):
    """Split text into (visible part, final sentence). Math spans are protected."""
    masked = re.sub(r'\\\(.*?\\\)', lambda x: 'M' * len(x.group(0)), t, flags=re.S)
    cut = 0
    for m in re.finditer(r'[.?!]\)?\s+(?=[A-Z`]|\\\()|\\par|\n\s*\n|\\end\{[a-z]+\}', masked):
        cut = m.end()
    return t[:cut], t[cut:]

def solution(a, ctx):
    segs = re.split(r'(\\\[.*?\\\])', a, flags=re.S)
    out, rows = [], []

    def flush():
        if rows:
            out.append(block('<div class="chain">' + ''.join(rows) + '</div>'))
            rows.clear()
    for k, seg in enumerate(segs):
        if k % 2 == 0:
            t = seg
            nxt = k + 1 < len(segs)
            if nxt and t.strip().endswith(':') and '\\textbf{+' not in last_sentence(t)[1]:
                vis, reason = last_sentence(t)
                if vis.strip():
                    flush(); out.append(conv(vis, ctx) + PB)
                pending = conv(reason.strip(), ctx).replace(PB, ' ')
            else:
                if t.strip():
                    flush(); out.append(conv(t, ctx) + PB)
                pending = None
            segs[k] = pending
        else:
            m = seg[2:-2].strip()
            lhs, rhs = split_rel(m)
            r = ''
            if lhs:
                r += '<span class="lhs">\\(\\displaystyle %s\\)</span>' % esc_math(lhs)
            r += '<span class="rhs">\\(\\displaystyle %s\\)</span>' % esc_math(rhs)
            reason = segs[k - 1]
            if reason:
                r += '<button class="lnk why" type="button">why</button><span class="reason" hidden>%s</span>' % reason
            rows.append(r)
    flush()
    body = paras(''.join(out))
    if ctx.get('mc'):
        bar = '<button class="bar check" type="button" title="Check my answer" aria-label="Check my answer"></button>'
    else:
        bar = '<button class="bar soltoggle" type="button" aria-expanded="false" title="Show solution" aria-label="Show solution"></button>'
    return '<div class="solwrap">%s<div class="sol" hidden>%s</div></div>' % (bar, body)

# ---------------------------------------------------------------- reviews
def review_body(a, summary, ctx):
    terms, formulas, recipes = a
    th = []
    for m in re.finditer(r'\\t([mn])(\[[^\]]*\])?\{([^}]*)\}\{((?:[^{}]|\{[^{}]*\})*)\}', terms):
        kind, disp, k, f = m.groups()
        label = conv((disp or '')[1:-1] or k, ctx)
        if kind == 'm':
            label = '<a class="tl" href="#term-%s">%s</a>' % (key(conv(k, ctx)), label)
        th.append('<span class="rvt">%s%s</span>' % (label, (' <span class="tf">[\\(%s\\)]</span>' % esc_math(f)) if f else ''))
    fl = ''.join('<li>%s</li>' % conv(x.strip(), ctx) for x in split_top(formulas, 'item')[1:])
    rh = []
    for m in re.finditer(r'\\recipe\{', recipes):
        nm, e = group(recipes, m.end() - 1)
        steps, _ = group(recipes, e)
        ss = ''.join('<span class="rs"><b>%d.</b> %s</span> ' % (q + 1, conv(x.strip(), ctx)) for q, x in enumerate(split_top(steps, 'item')[1:]))
        rh.append('<div class="rvr%s"><b>%s</b><div>%s</div></div>' % (' sum' if summary else '', conv(nm, ctx), ss))
    return ('<div class="rv-h">Terms</div><p class="rvterms">%s.</p><div class="rv-h">Formulas</div><ul class="rvf">%s</ul><div class="rv-h">Recipes</div>%s'
            % (', '.join(th), fl, ''.join(rh)))

# ---------------------------------------------------------------- the document
body = strip_comments(TEX[TEX.index('\\begin{document}') + 16:TEX.index('\\end{document}')])
ti = body.index('\\chaptertitle')
targs, j = [], ti + len('\\chaptertitle')
for _ in range(4):
    a, j = arg(body, j); targs.append(a)
CHAP = targs[1].strip()
intro = body[j:body.index('\\begingroup', j)]
intro = re.sub(r'\\ifshowanswers.*?\\fi', '', intro, flags=re.S)
rest = body[body.index('\\begin{priorsection}'):]

sheets = []
cur = {'cls': 'prior', 'id': 'prior', 'band': '<div class="band prior">Prior knowledge</div>', 'src': ''}

def close(c):
    sheets.append('<div class="sheet %s" id="%s">%s\n%s\n</div>' % (c['cls'], c['id'], c['band'], paras(conv(c['src'], {}))))

pos = 0
for m in re.finditer(r'\\parasection\{(\d+)\}\{([^}]*)\}|\\frontsection\{(Summary|Diagnostic check)\}', rest):
    cur['src'] += rest[pos:m.start()]
    close(cur)
    if m.group(1):
        cur = {'cls': '', 'id': 'sec' + m.group(1), 'band': '<div class="band"><span class="num">&sect;%s</span>%s</div>' % (m.group(1), conv(m.group(2), {})), 'src': ''}
    elif m.group(3) == 'Summary':
        cur = {'cls': 'summary', 'id': 'summary', 'band': '<div class="band">Summary</div>', 'src': ''}
    else:
        cur = {'cls': 'diag', 'id': 'diagnostic', 'band': '<div class="band">Diagnostic check</div>', 'src': ''}
    pos = m.end()
cur['src'] += rest[pos:]
close(cur)
content = '\n'.join(sheets)
content = content.replace('\\begin{priorsection}', '').replace('\\end{priorsection}', '')

figs = build_figs()
content = re.sub(r'@@FIG(\d+)@@', lambda m: figs[int(m.group(1))], content)

# ---------------------------------------------------------------- Contents from the .aux
groups = {}
order = []
for p, t, k in re.findall(r'\\exentry\{([^}]*)\}\{([^}]*)\}\{([^}]*)\}', AUX):
    if p not in groups:
        groups[p] = []; order.append(p)
    if t in 'QL' or not groups[p]:
        groups[p].append([])
    groups[p][-1].append(t + '/' + k)
titles = {'0': ('Prior knowledge', 'prior')}
for m in re.finditer(r'\\parasection\{(\d+)\}\{([^}]*)\}', rest):
    titles[m.group(1)] = ('\u00a7%s: %s' % (m.group(1), m.group(2).replace("'", '\u2019')), 'sec' + m.group(1))
toc = [['Legend', 'legend', '']]
for p in order:
    if p in titles:
        toc.append([titles[p][0], titles[p][1], '|'.join(','.join(g) for g in groups[p])])
letters = ','.join('L/' + c.split('/')[1] for p in order if p in titles and p != '0' for g in groups[p] for c in g if c.startswith('L/'))
toc.append(['Summary', 'summary', 'S:' + letters])
diag = [p for p in order if p.startswith('D')]
toc.append(['Diagnostic check', 'diagnostic', 'Z:' + '|'.join(','.join(c for g in groups[p] for c in g) for p in diag)])
toc_js = 'var TOC = ' + json.dumps(toc, ensure_ascii=False) + ';'

# ---------------------------------------------------------------- assemble with the template
def mix(rgb, p):  # xcolor "c!p": p percent of the colour, the rest white
    return '#%02x%02x%02x' % tuple(round(p / 100 * c + (1 - p / 100) * 255) for c in rgb)
cm = re.search(r'\\definecolor\{chcolor%s\}\{RGB\}\{(\d+),(\d+),(\d+)\}' % CHAP, TEX)
rgb = tuple(int(x) for x in cm.groups()) if cm else (183, 28, 28)
KEY = re.sub(r'[^a-z0-9]+', '-', NAME.lower())
colours = ':root { --chap: %s; --chap22: %s; --chap35: %s; --chap10: %s; --chapdome: rgba(%d, %d, %d, .3); }' % (
    '#%02x%02x%02x' % rgb, mix(rgb, 22), mix(rgb, 35), mix(rgb, 10), *rgb)
head = TPL[:TPL.index('<!--FRONT-->')].replace('@@TITLE@@', html.unescape(re.sub(r'<[^>]+>|\\\(.*?\\\)', '', conv(targs[2], {}))).strip())
head = head.replace('</style>', open(os.path.join(HERE, 'chapter.css')).read() + '\n' + colours + '\n</style>')
legend = TPL[TPL.index('<!--FRONT-->') + 12:TPL.index('<!--CONTENT-->')].replace('@@N@@', CHAP)
k = [0]
def swatch(m):
    k[0] += 1
    return '<span class="cur" style' if str(k[0]) == CHAP else m.group(0)
legend = re.sub(r'<span style(?=="background:#[0-9a-f]{6}">\d</span>)', swatch, legend)
tail = TPL[TPL.index('<!--CONTENT-->') + 14:].replace('@@KEY@@', KEY)
tail = re.sub(r'var TOC = \[.*?\n  \];', lambda m: toc_js, tail, flags=re.S)
front = ('<div class="sheet" id="top">\n  <div class="titleband"><div class="t">%s: CHAPTER %s&ensp;%s</div><div class="s">%s</div><div class="c">Created with the write-mastery-chapter skill</div></div>\n'
         '  <p style="text-indent:15pt">%s Solutions open with a click on the blue bar.</p>\n'
         '  <div class="tools" style="margin:6pt 0 0"><button class="lnk" id="allSol" type="button">Open all solutions</button> <button class="lnk" id="allWhy" type="button">Show all reasons</button> <span class="donecount" id="doneCount"></span> <span class="flagcount" id="flagCount"></span></div>\n'
         '  <div class="band" id="contents" style="margin-top:14pt">Contents</div>\n  <div class="toc" id="toc"></div>\n</div>\n'
         % (targs[0], targs[1], conv(targs[2], {}), conv(targs[3], {}), conv(intro, {}).replace(PB, ' ').strip()))
out = head + '\n' + front + legend + content + tail
leftover = sorted(set(re.findall(r'\\[A-Za-z]+', re.sub(r'\\\(.*?\\\)|\\\[.*?\\\]|<script.*?</script>|data-hints=\'[^\']*\'|src="data:[^"]*"', '', out, flags=re.S))))
open(OUT, 'w').write(out)
print('exercises', st['ex'], 'prior', st['prior'], 'diag', st['diag'], 'figures', len(figs), 'bytes', len(out))
print('unhandled macros in text:', leftover)
