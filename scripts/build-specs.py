"""Fill the full "მახასიათებლები" (specifications) section of the P150 MAX page from scripts/p150_specs.py.
Georgian goes into scripts/page-bodies.html; ka/en/ru texts go into dist/assets/js/content.js (keys ps_*).
Multi-line values become one <span class="spec-line"> per line. Run by scripts/build.py before build-pages.py.
"""
import html, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import p150_specs as S

cj = ROOT / 'dist/assets/js/content.js'
c = json.loads(cj.read_text(encoding='utf-8').split('=', 1)[1].strip().removesuffix(';'))
for lang in ('ka', 'en', 'ru'):
    for k in [k for k in c[lang] if k.startswith('ps_')]:
        del c[lang][k]


def tri(v):
    return v if isinstance(v, tuple) else (v, v, v)


def put(key, v):
    for lang, s in zip(('ka', 'en', 'ru'), tri(v)):
        c[lang][key] = s


def same(v):
    ka, en, ru = tri(v)
    return ka == en == ru


def label(tag, key, v, extra=''):
    if same(v):
        return f'<{tag}{extra}>{html.escape(tri(v)[0])}</{tag}>'
    put(key, v)
    return f'<{tag}{extra} data-i18n="{key}">{html.escape(tri(v)[0])}</{tag}>'


def value(key, v):
    ka, en, ru = tri(v)
    if '\n' not in ka:
        return label('dd', key, v)
    lines = list(zip(ka.split('\n'), en.split('\n'), ru.split('\n')))
    spans = ''.join(label('span', f'{key}_{i}', ln, ' class="spec-line"') for i, ln in enumerate(lines))
    return f'<dd>{spans}</dd>'


put('ps_heading', S.HEADING)
put('ps_intro', S.INTRO)
put('ps_note', S.NOTE)
out = ['  <section class="section spec-full-section" id="specifications" aria-labelledby="specs-full-title"><div class="container">',
       f'<div class="section-heading"><h2 id="specs-full-title"><span data-i18n="ps_heading">{html.escape(S.HEADING[0])}</span></h2></div>',
       f'<p class="page-intro" data-i18n="ps_intro">{html.escape(S.INTRO[0])}</p>',
       '<div class="spec-full">']
SPEC_IMG = {'platform': 'platform/platform-front', 'revospray': 'platform/platform-field', 'revocast': 'products/09-023-00145',
            'revosling': 'products/05-002-02682', 'power': 'products/09-017-00073'}
for i, g in enumerate(S.SPECS):
    gid = g['id']
    out.append(f'<details class="spec-cat"{" open" if i == 0 else ""}><summary>{label("span", f"ps_{gid}", g["title"])}</summary><div class="spec-cat-body">')
    if g['id'] in SPEC_IMG:
        out.append(f'<figure class="spec-fig"><img src="/assets/img/{SPEC_IMG[g["id"]]}.webp" alt="" loading="lazy" decoding="async" width="1200" height="900"></figure>')
    for b, (sub, rows) in enumerate(g['blocks']):
        out.append('<div class="spec-block">' + (label('h3', f'ps_{gid}_{b}', sub) if sub else '') + '<dl>')
        for r, (lab, val) in enumerate(rows):
            out.append(f'<div>{label("dt", f"ps_{gid}_{b}_{r}l", lab)}{value(f"ps_{gid}_{b}_{r}v", val)}</div>')
        out.append('</dl></div>')
    out.append('</div></details>')
out += ['</div>', f'<p class="small-note" data-i18n="ps_note">{html.escape(S.NOTE[0])}</p>', '</div></section><!--/specifications-->']
block = '\n'.join(out)

pb = ROOT / 'scripts/page-bodies.html'
t = pb.read_text(encoding='utf-8')
t, n = re.subn(r'  <section class="section spec-full-section" id="specifications".*?<!--/specifications-->', lambda m: block, t, count=1, flags=re.S)
if n != 1:
    raise SystemExit('P150 MAX specifications section (id="specifications" ... <!--/specifications-->) not found')
pb.write_text(t, encoding='utf-8')
cj.write_text('window.PDG_CONTENT = ' + json.dumps(c, ensure_ascii=False, indent=2) + ';\n', encoding='utf-8')
print(f'specs: {sum(len(r) for g in S.SPECS for _, r in g["blocks"])} rows in {len(S.SPECS)} groups')
