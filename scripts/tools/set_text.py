"""Set a UI text in all three languages: Georgian in the HTML sources (dist/index.html, scripts/page-bodies.html),
English and Russian (and Georgian, when the key is kept there) in dist/assets/js/content.js.
Usage from Python: from set_text import setk, save; setk(key, ka, en, ru); save()"""
import json, re, html
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
CJ = ROOT / 'dist/assets/js/content.js'
SRC = [ROOT / 'dist/index.html', ROOT / 'scripts/page-bodies.html']
_c = json.loads(CJ.read_text(encoding='utf-8').split('=', 1)[1].strip().removesuffix(';'))
_src = {p: p.read_text(encoding='utf-8') for p in SRC}


def setk(key, ka, en, ru, need_html=True):
    hits = 0
    for p, s in _src.items():
        s2, n = re.subn(r'(data-i18n="%s"[^>]*>)([^<]*)(<)' % re.escape(key), lambda m: m.group(1) + html.escape(ka, quote=False) + m.group(3), s)
        _src[p] = s2
        hits += n
    if need_html and not hits and key not in _c['ka']:
        raise SystemExit(f'{key}: no Georgian element found')
    if key in _c['ka']:
        _c['ka'][key] = ka
    _c['en'][key], _c['ru'][key] = en, ru
    return hits


def drop(key):
    for l in ('ka', 'en', 'ru'):
        _c[l].pop(key, None)


def save():
    for p, s in _src.items():
        p.write_text(s, encoding='utf-8')
    CJ.write_text('window.PDG_CONTENT = ' + json.dumps(_c, ensure_ascii=False, indent=2) + ';\n', encoding='utf-8')
