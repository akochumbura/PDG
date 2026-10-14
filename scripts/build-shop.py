"""Regenerate shop cards and the P150 MAX kit table from scripts/catalog.csv and scripts/pricing.py.

Product photos: a file dist/assets/img/products/<SKU>.webp is used automatically when it exists.
Parts without a photo get a text card with their category (never a photo of a different product,
never a grey placeholder).
"""
import csv, html, re, sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import pricing

RATE = Decimal(pricing.RATE)
PHOTOS = ROOT / 'dist/assets/img/products'


def gel(usd, mark):
    return int((Decimal(str(usd)) * Decimal(mark) * RATE).quantize(Decimal('1'), ROUND_HALF_UP))


# Real PDG photos of the P150 MAX, used for drone kits only (every kit contains the drone).
KIT_IMG = {
    'flight': ('p150-max-flight-1200.webp', 1200, 500, '50% 62%'),
    'field': ('field-ready.webp', 1280, 600, '50% 70%'),
    'detail': ('drone-detail.webp', 1280, 960, '50% 45%'),
    'transport': ('transport.webp', 960, 1280, '50% 55%'),
}

# Line icons (48x48, stroke) for parts that do not have their own photo yet.
ICON = {
    'power': '<rect x="9" y="14" width="27" height="21" rx="2"/><path d="M36 21h3v7h-3"/><path d="M24 17l-5 8h6l-4 8"/>',
    'spray': '<path d="M20 7h8v8l4 6H16l4-6z"/><path d="M18 29l-2 4M24 29v5M30 29l2 4M15 37l-1 3M24 38v3M33 37l1 3"/>',
    'control': '<rect x="9" y="18" width="30" height="20" rx="4"/><circle cx="18" cy="28" r="3"/><circle cx="30" cy="28" r="3"/><path d="M15 18l-3-9M33 18l3-9"/>',
    'acc': '<path d="M24 7l14 8v17l-14 8-14-8V15z"/><path d="M10 15l14 8 14-8M24 23v17"/>',
    'drone': '<path d="M24 20v8M14 24h20"/><circle cx="10" cy="14" r="5"/><circle cx="38" cy="14" r="5"/><circle cx="10" cy="34" r="5"/><circle cx="38" cy="34" r="5"/>',
    'spare': '<path d="M31 9a8 8 0 0 0-9.5 10.5L10 31a3 3 0 0 0 4.2 4.2l11.5-11.5A8 8 0 0 0 36 14l-5 5-4.5-1.2L25.3 13z"/>',
}
CAT_KEY = {'power': ('cat_power', 'აკუმულატორები და დატენვა'), 'spray': ('cat_spray', 'შეწამვლა და გაფანტვა'),
           'control': ('cat_control', 'მართვა და RTK'), 'acc': ('cat_acc', 'აქსესუარები'), 'spare': ('cat_spare', 'სათადარიგო ნაწილები'),
           'drone': ('cat_drone', 'დრონები')}


CONTENTS = [('drones', 'kit_drone', 'დრონი P150 MAX'), ('batteries', 'kit_batteries', 'აკუმულატორები'),
            ('chargers', 'kit_chargers', 'დამტენები'), ('rtk', 'kit_rtk', 'RTK სადგური'),
            ('generators', 'kit_generators', 'გენერატორები')]
# Home page 'Parts and energy system': B141050 battery, GC4000+, CM13600S charger, 6 kW parallel charging kit, cooling tower, XRTK7.
HOME_PARTS = ['P000088274', 'P000089806', 'P000087889', 'P000088239', 'P000087484', 'P000088079']


def contents(r, cls='kit-contents'):
    """Package contents from the catalog columns batteries / chargers / generators (empty = not shown)."""
    parts = [f'<div><dt data-i18n="{key}">{ka}</dt><dd>{r.get(col, "").strip()}</dd></div>'
             for col, key, ka in CONTENTS if (r.get(col) or '').strip()]
    return f'<dl class="{cls}">{"".join(parts)}</dl>' if parts else ''


def price(r, kit):
    """A fixed GEL price in the catalog wins; otherwise Agrifuture USD x markup x rate."""
    if (r.get('gel') or '').strip():
        return int(Decimal(r['gel'].strip()))
    return gel(r['usd'], pricing.MARKUP_KITS if kit else pricing.MARKUP_PARTS)


def photo(r, kit):
    s = r['sku']
    own = PHOTOS / f'{s}.webp'
    n = html.escape(r['name'], quote=True)
    if own.is_file():
        try:
            from PIL import Image
            w, h = Image.open(own).size
        except Exception:
            w, h = 1200, 900
        return f'<div class="product-photo"><img src="/assets/img/products/{s}.webp" width="{w}" height="{h}" alt="{n}" loading="lazy" decoding="async"></div>'
    # Owner, 14 Oct 2026: until his product photos arrive, every product (packages too) shows the XAG logo.
    return ('<div class="product-photo product-logo">'
            '<img class="logo-light" src="/assets/img/xag-logo.svg" alt="XAG" width="69" height="25" loading="lazy">'
            '<img class="logo-dark" src="/assets/img/xag-logo-white.svg" alt="" width="69" height="25" loading="lazy"></div>')


def cat(r):
    if r['group'] == 'kit':
        return ''
    key, ka = CAT_KEY[r['group']]
    return f'<p class="product-cat" data-i18n="{key}">{ka}</p>'


def pkey(sku):
    return 'pn_' + re.sub(r'[^A-Za-z0-9]', '_', sku)


def title(r):
    """Parts: the Georgian/Russian name first (per language), the original XAG name under it. Kits: the original name."""
    n = html.escape(r['name'])
    if not (r.get('name_ka') or '').strip():
        return f'<h3>{n}</h3>'
    return f'<h3 data-i18n="{pkey(r["sku"])}">{html.escape(r["name_ka"])}</h3><p class="product-orig">{n}</p>'


def part_row(r):
    """Compact row for the home page 'Parts and energy system' list."""
    n = html.escape(r['name'], quote=True)
    s = r['sku']
    p = price(r, False)
    return (f'<li class="part-row"><div class="part-row-name"><span class="part-row-title">{html.escape(r["name"])}</span>'
            f'<span class="product-sku">{s}</span></div><span class="part-row-price">₾{p:,}</span>'
            f'<button type="button" class="add-btn" data-sku="{s}" data-name="{n}" data-price="{p}" data-i18n="add_to_cart">კალათაში</button></li>\n')


def card(r):
    kit = r['group'] == 'kit'
    n = html.escape(r['name'], quote=True)
    s = r['sku']
    p = price(r, kit)
    return (f'<article class="product{" product-kit" if kit else ""}" data-cat="{r["group"]}">{photo(r, kit)}'
            f'<div class="product-body">{cat(r)}<p class="product-sku">{s}</p>{title(r)}{contents(r) if kit else ""}'
            f'<p class="product-stock" data-i18n="in_stock">საწყობშია</p>'
            f'<div class="product-buy"><span class="product-price">₾{p:,}</span>'
            f'<button type="button" class="add-btn" data-sku="{s}" data-name="{n}" data-price="{p}" data-i18n="add_to_cart">კალათაში</button></div></div></article>\n')


def kit_row(r):
    n = html.escape(r['name'], quote=True)
    s = r['sku']
    p = price(r, True)
    short = re.sub(r'^XAG P150 Max\s*', '', r['name']).strip() or r['name']
    return (f'<li class="kit-row"><div class="kit-row-name"><span class="kit-row-title">{html.escape(short)}</span>{contents(r, "kit-contents kit-contents-inline")}</div>'
            f'<span class="kit-row-price">₾{p:,}</span>'
            f'<button type="button" class="add-btn" data-sku="{s}" data-name="{n}" data-price="{p}" data-i18n="add_to_cart">კალათაში</button></li>\n')


rows = list(csv.DictReader(open(ROOT / 'scripts/catalog.csv', encoding='utf-8')))
import json as _json
_cj = ROOT / 'dist/assets/js/content.js'
_c = _json.loads(_cj.read_text(encoding='utf-8').split('=', 1)[1].strip().removesuffix(';'))
for _lang in ('en', 'ru', 'ka'):
    for _k in [k for k in _c[_lang] if k.startswith('pn_')]:
        del _c[_lang][_k]
for r in rows:
    if (r.get('name_ka') or '').strip():
        _c['en'][pkey(r['sku'])] = r['name']
        _c['ru'][pkey(r['sku'])] = (r.get('name_ru') or '').strip() or r['name']
_cj.write_text('window.PDG_CONTENT = ' + _json.dumps(_c, ensure_ascii=False, indent=2) + ';\n', encoding='utf-8')
kits = [r for r in rows if r['group'] == 'kit']
parts = [r for r in rows if r['group'] != 'kit']
# Shop order: drone, energy, control/RTK, spraying/spreading, accessories, spare parts; most expensive first in each group.
ORDER = ['drone', 'power', 'control', 'spray', 'acc', 'spare']
parts.sort(key=lambda r: (ORDER.index(r['group']) if r['group'] in ORDER else 99, -price(r, False), r['name']))
for r in rows:
    if r['group'] not in {'kit', *ICON}:
        raise SystemExit(f'Unknown group {r["group"]!r} for {r["sku"]}')

pb = ROOT / 'scripts/page-bodies.html'
t = pb.read_text(encoding='utf-8')
subs = [
    (r'(<div class="shop-grid kit-grid">\n).*?(</div></div></section>)', ''.join(card(r) for r in kits)),
    (r'(<div class="shop-grid" id="partsGrid">\n).*?(</div></div></section>)', ''.join(card(r) for r in parts)),
    (r'(<ul class="kit-table">\n).*?(</ul>)', ''.join(kit_row(r) for r in kits)),
]
home = ROOT / 'dist/index.html'
ht = home.read_text(encoding='utf-8')
by_sku = {r['sku']: r for r in rows}
for pattern, body in [(r'(<div class="shop-grid kit-grid" id="homePackages">).*?(</div>\s*<!--/homePackages-->)', '\n' + ''.join(card(r) for r in kits)),
                      (r'(<ul class="part-list" id="homeParts">).*?(</ul>\s*<!--/homeParts-->)', '\n' + ''.join(part_row(by_sku[s]) for s in HOME_PARTS if s in by_sku))]:
    ht, n = re.subn(pattern, lambda m: m.group(1) + body + m.group(2), ht, count=1, flags=re.S)
    if n != 1 and 'homePackages' in pattern:
        raise SystemExit('Home page marker not found: ' + pattern[:50])
home.write_text(ht, encoding='utf-8')
for pattern, body in subs:
    t, n = re.subn(pattern, lambda m: m.group(1) + body + m.group(2), t, count=1, flags=re.S)
    if n != 1:
        raise SystemExit(f'Template marker not found: {pattern[:40]}')
pb.write_text(t, encoding='utf-8')
own = sum((PHOTOS / f'{r["sku"]}.webp').is_file() for r in rows)
print(f'shop: {len(rows)} products ({len(kits)} kits), {own} with their own photo')

# Keep the AI summary (dist/llms.txt) in step with the catalog prices.
llms = ROOT / 'dist/llms.txt'
if llms.is_file():
    def line(r):
        what = ', '.join(f"{r[c]} {'RTK station' if c == 'rtk' else c}" for c in ('batteries', 'chargers', 'rtk', 'generators') if (r.get(c) or '').strip())
        return f"- {r['name']}: {price(r, True):,} GEL" + (f" ({what})" if what else '')
    extra = [r for r in parts if (r.get('gel') or '').strip()]
    block = '## Packages (prices in GEL)\n' + '\n'.join(line(r) for r in kits) + '\n' + \
            '\n'.join(f"- {r['name']}: {price(r, False):,} GEL" for r in extra) + '\n\n'
    text = llms.read_text(encoding='utf-8')
    text = re.sub(r'## Packages \(prices in GEL\)\n.*?\n\n', lambda m: block, text, flags=re.S)
    llms.write_text(text, encoding='utf-8')

# Payment worker (Cloudflare Pages advanced mode): server-side prices from this same catalog.
sys.path.insert(0, str(ROOT / 'scripts'))
import json, site_config
cat = {r['sku']: [r['name'], price(r, r['group'] == 'kit')] for r in rows}
tpl = (ROOT / 'scripts/worker.template.js').read_text(encoding='utf-8')
rules = {'threshold': site_config.PAYMENTS['threshold'], 'depositPercent': site_config.PAYMENTS['deposit_percent']}
# Knowledge for the AI chat: business facts (llms.txt), every product with its price, payment rules, terms, FAQ.
CATN = {'kit': 'P150 MAX package', 'drone': 'drone', 'power': 'batteries and charging', 'spray': 'spraying and spreading', 'control': 'control and RTK',
        'acc': 'accessories', 'spare': 'spare parts'}
cdata = json.loads((ROOT / 'dist/assets/js/content.js').read_text(encoding='utf-8').split('=', 1)[1].strip().removesuffix(';'))['en']
know = [(ROOT / 'dist/llms.txt').read_text(encoding='utf-8').strip(), '', '## All products in stock (prices in GEL, from the website shop)']
for r in rows:
    extra = ', '.join(f"{r[c]} {c}" for c in ('drones', 'batteries', 'chargers', 'rtk', 'generators') if (r.get(c) or '').strip())
    local = f" [ka: {r['name_ka']}; ru: {r['name_ru']}]" if (r.get('name_ka') or '').strip() else ''
    know.append(f"- {r['name']}{local} (code {r['sku']}, {CATN[r['group']]}): {price(r, r['group'] == 'kit'):,} GEL" + (f" — contains {extra}" if extra else ''))
know += ['', '## Buying and payment',
         f"Online payment (card, Apple Pay, Google Pay via Bank of Georgia) is being set up and may not be live yet. Planned rule: orders under {rules['threshold']:,} GEL are paid in full online; from {rules['threshold']:,} GEL the customer pays a {rules['depositPercent']}% deposit online and the rest by bank transfer.",
         'Today orders are placed from the cart by WhatsApp or email; PDG confirms stock and delivery.', '', '## Terms']
know += [f"- {cdata[f'terms_h{i}']}: {cdata[f'terms_p{i}']}" for i in range(1, 8)]
know += ['', '## FAQ'] + [f"Q: {cdata[f'faq_q{i}']}\nA: {cdata[f'faq_a{i}']}" for i in range(1, 5)]
know += ['', '## PDG Academy', cdata['academy_description'], cdata['academy_section_text'], '', '## Service', cdata['service_page_p1'], cdata['service_page_p2']]
knowledge = '\n'.join(know)
for marker, value in (('__CATALOG__', json.dumps(cat, ensure_ascii=False)), ('__RULES__', json.dumps(rules)), ('__KNOWLEDGE__', json.dumps(knowledge, ensure_ascii=False))):
    if tpl.count(marker) != 1:
        raise SystemExit('worker template marker missing: ' + marker)
    tpl = tpl.replace(marker, value)
(ROOT / 'dist/_worker.js').write_text(tpl, encoding='utf-8')
(ROOT / 'dist/_routes.json').write_text(json.dumps({'version': 1, 'include': ['/api/*'], 'exclude': []}) + '\n', encoding='utf-8')
pc = ROOT / 'dist/assets/js/payments-config.js'
pc.write_text('/* Generated by scripts/build-shop.py from scripts/site_config.py (PAYMENTS). Online payment turns on by itself\n'
              '   once the Bank of Georgia keys are saved in Cloudflare (see docs/07-payments.md). */\n'
              f'window.PDG_PAY={{endpoint:"/api",threshold:{rules["threshold"]},depositPercent:{rules["depositPercent"]}}};\n', encoding='utf-8')
print(f'payments: worker with {len(cat)} prices; full payment under GEL {rules["threshold"]:,}, {rules["depositPercent"]}% deposit above')
