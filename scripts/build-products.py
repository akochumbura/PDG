"""Product pages for the energy system (scripts/product_pages.py): B141050 battery, CM13600S charger, GC4000+ station.
Each page: photo (own photo or the XAG logo), Georgian name + original name, manufacturer code, price, quantity, cart,
WhatsApp question, and the official XAG specs from scripts/p150_specs.py ('power' group). Georgian goes into
scripts/page-bodies.html (between <!--product-pages--> and <!--/product-pages-->), ka/en/ru texts into content.js (pd_*).
Run by scripts/build.py after build-shop.py and build-specs.py, before build-pages.py.
"""
import csv, html, json, re, sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import p150_specs as S
import product_pages as P

cj = ROOT / 'dist/assets/js/content.js'
c = json.loads(cj.read_text(encoding='utf-8').split('=', 1)[1].strip().removesuffix(';'))
for lang in ('ka', 'en', 'ru'):
    for k in [k for k in c[lang] if k.startswith('pd_')]:
        del c[lang][k]

T = {'pd_more': ('მახასიათებლები', 'Specifications', 'Характеристики'),
     'pd_code': ('მწარმოებლის კოდი', 'Manufacturer code', 'Код производителя'),
     'pd_specs': ('მახასიათებლები', 'Specifications', 'Характеристики'),
     'pd_source': ('წყარო: XAG-ის ოფიციალური მახასიათებლები (xa.com, XAG P150 MAX).', 'Source: official XAG specifications (xa.com, XAG P150 MAX).',
                   'Источник: официальные характеристики XAG (xa.com, XAG P150 MAX).'),
     'pd_ask': ('კითხვა WhatsApp-ით', 'Ask on WhatsApp', 'Вопрос в WhatsApp'),
     'pd_back': ('← მაღაზია', '← Shop', '← Магазин'),
     'pd_fits': ('XAG P150 MAX-ის ენერგოსისტემა', 'XAG P150 MAX power system', 'Система питания XAG P150 MAX'),
     'pd_vat': ('ფასი დღგ-ს ჩათვლით', 'Price incl. VAT', 'Цена с НДС')}


def tri(v):
    return v if isinstance(v, tuple) else (v, v, v)


def put(key, v):
    for lang, s in zip(('ka', 'en', 'ru'), tri(v)):
        c[lang][key] = s


for k, v in T.items():
    put(k, v)


def label(tag, key, v, extra=''):
    ka, en, ru = tri(v)
    if ka == en == ru:
        return f'<{tag}{extra}>{html.escape(ka)}</{tag}>'
    put(key, v)
    return f'<{tag}{extra} data-i18n="{key}">{html.escape(ka)}</{tag}>'


def value(key, v):
    ka, en, ru = tri(v)
    if '\n' not in ka:
        return label('dd', key, v)
    lines = list(zip(ka.split('\n'), en.split('\n'), ru.split('\n')))
    return '<dd>' + ''.join(label('span', f'{key}_{i}', ln, ' class="spec-line"') for i, ln in enumerate(lines)) + '</dd>'


power = next(g for g in S.SPECS if g['id'] == 'power')['blocks']
rows = {r['sku']: r for r in csv.DictReader(open(ROOT / 'scripts/catalog.csv', encoding='utf-8'))}
PHOTOS = ROOT / 'dist/assets/img/products'
out = []
for p in P.PAGES:
    r = rows.get(p['sku'])
    if not r or not (r.get('gel') or '').strip() or (r.get('avail') or '') == 'quote':
        raise SystemExit(f'product page {p["slug"]}: {p["sku"]} is not a priced price-list item in catalog.csv')
    sku, pid = p['sku'], p['slug'].replace('-', '_')
    head, specs = power[p['block']]
    name_en = html.escape(r['name'], quote=True)
    gel = int(r['gel'])
    for k in ('title', 'intro'):
        put(f'pd_{pid}_{k}', p[k])
    own = PHOTOS / f'{sku}.webp'
    if own.is_file():
        from PIL import Image
        w, h = Image.open(own).size
        pic = f'<div class="product-photo pd-photo"><img src="/assets/img/products/{sku}.webp" width="{w}" height="{h}" alt="{name_en}" decoding="async"></div>'
    else:
        pic = ('<div class="product-photo product-logo pd-photo"><img class="logo-light" src="/assets/img/xag-logo.svg" alt="XAG" width="69" height="25">'
               '<img class="logo-dark" src="/assets/img/xag-logo-white.svg" alt="" width="69" height="25"></div>')
    pn = 'pn_' + re.sub(r'[^A-Za-z0-9]', '_', sku)  # Georgian / English / Russian product name (written by build-shop.py)
    wa = 'https://wa.me/995550004333?text=' + quote(f'გამარჯობა! მაინტერესებს {r["name"]} ({sku}).')
    dl = ''.join(f'<div>{label("dt", f"pd_{pid}_{i}l", lab)}{value(f"pd_{pid}_{i}v", val)}</div>' for i, (lab, val) in enumerate(specs))
    title_ka = html.escape(p['title'][0] + ' | საქართველოს პრემიუმ დრონები', quote=True)
    out.append(
        f'<template data-page="{p["slug"]}.html" data-ka-title="{title_ka}" data-title="pd_{pid}_title" data-description="pd_{pid}_intro">\n'
        f'  <section class="page-hero pd-hero"><div class="container"><a class="back-link" href="/shop.html#parts" data-local data-i18n="pd_back">← მაღაზია</a>'
        f'<p class="eyebrow" data-i18n="pd_fits">XAG P150 MAX-ის ენერგოსისტემა</p>'
        f'<h1 data-i18n="{pn}">{html.escape(r["name_ka"])}</h1><p class="product-orig">{html.escape(r["name"])}</p>'
        f'<p class="page-intro" data-i18n="pd_{pid}_intro">{html.escape(p["intro"][0])}</p></div></section>\n'
        f'  <section class="section pd-main"><div class="container pd-grid">{pic}'
        f'<article class="product pd-buybox" data-cat="{r["group"]}" data-avail="in_stock">'
        f'<p class="product-sku"><span data-i18n="pd_code">მწარმოებლის კოდი</span>: {sku}</p>'
        f'<p class="product-stock" data-i18n="in_stock">საწყობშია</p>'
        f'<p class="pd-price"><span class="product-price">₾{gel:,}</span> <span class="pd-vat" data-i18n="pd_vat">ფასი დღგ-ს ჩათვლით</span></p>'
        f'<div class="buy-actions"><div class="qty-stepper" data-for="{sku}"><button type="button" class="qty-btn" data-step="-1" aria-label="რაოდენობის შემცირება" data-i18n-aria="qty_less">−</button>'
        f'<input class="qty-input" type="number" inputmode="numeric" min="1" step="1" value="1" aria-label="რაოდენობა" data-i18n-aria="qty_label">'
        f'<button type="button" class="qty-btn" data-step="1" aria-label="რაოდენობის გაზრდა" data-i18n-aria="qty_more">+</button></div>'
        f'<button type="button" class="add-btn" data-sku="{sku}" data-name="{name_en}" data-price="{gel}" data-i18n="add_to_cart">კალათაში</button></div>'
        f'<a class="button button-line pd-ask" href="{html.escape(wa, quote=True)}" target="_blank" rel="noopener noreferrer"><span data-i18n="pd_ask">კითხვა WhatsApp-ით</span></a>'
        f'</article></div></section>\n'
        f'  <section class="section pd-specs" id="specifications" aria-labelledby="pd-specs-title"><div class="container">'
        f'<div class="section-heading"><h2 id="pd-specs-title"><span data-i18n="pd_specs">მახასიათებლები</span></h2></div>'
        f'<div class="spec-block pd-spec-block">{label("h3", f"pd_{pid}_head", head)}<dl>{dl}</dl></div>'
        f'<p class="small-note"><a href="https://www.xa.com/en/p150max/p150maxspecs" target="_blank" rel="noopener noreferrer" data-i18n="pd_source">{html.escape(T["pd_source"][0])}</a></p>'
        f'</div></section>\n</template>\n')

pb = ROOT / 'scripts/page-bodies.html'
t = pb.read_text(encoding='utf-8')
if '<!--product-pages-->' not in t:
    t = t.rstrip('\n') + '\n<!--product-pages-->\n<!--/product-pages-->\n'
t = re.sub(r'<!--product-pages-->\n.*?<!--/product-pages-->', lambda m: '<!--product-pages-->\n' + ''.join(out) + '<!--/product-pages-->', t, count=1, flags=re.S)
pb.write_text(t, encoding='utf-8')
cj.write_text('window.PDG_CONTENT = ' + json.dumps(c, ensure_ascii=False, indent=2) + ';\n', encoding='utf-8')
print(f'product pages: {len(out)} ({", ".join(p["slug"] for p in P.PAGES)})')
