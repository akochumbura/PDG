"""Regenerate shop cards and the P150 MAX kit table from scripts/catalog.csv and scripts/pricing.py.

Product photos: a file dist/assets/img/products/<SKU>.webp is used automatically when it exists.
Parts without a photo get a clean category tile (never a photo of a different product).
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
    'field': ('field-ready.webp', 1280, 960, '50% 60%'),
    'detail': ('drone-detail.webp', 1280, 960, '50% 45%'),
    'transport': ('transport.webp', 960, 1280, '50% 55%'),
}

# Line icons (48x48, stroke) for parts that do not have their own photo yet.
ICON = {
    'power': '<rect x="9" y="14" width="27" height="21" rx="2"/><path d="M36 21h3v7h-3"/><path d="M24 17l-5 8h6l-4 8"/>',
    'spray': '<path d="M20 7h8v8l4 6H16l4-6z"/><path d="M18 29l-2 4M24 29v5M30 29l2 4M15 37l-1 3M24 38v3M33 37l1 3"/>',
    'control': '<rect x="9" y="18" width="30" height="20" rx="4"/><circle cx="18" cy="28" r="3"/><circle cx="30" cy="28" r="3"/><path d="M15 18l-3-9M33 18l3-9"/>',
    'acc': '<path d="M24 7l14 8v17l-14 8-14-8V15z"/><path d="M10 15l14 8 14-8M24 23v17"/>',
    'spare': '<path d="M31 9a8 8 0 0 0-9.5 10.5L10 31a3 3 0 0 0 4.2 4.2l11.5-11.5A8 8 0 0 0 36 14l-5 5-4.5-1.2L25.3 13z"/>',
}
CAT_KEY = {'power': ('cat_power', 'აკუმულატორები და დატენვა'), 'spray': ('cat_spray', 'შეწამვლა და გაფანტვა'),
           'control': ('cat_control', 'მართვა და RTK'), 'acc': ('cat_acc', 'აქსესუარები'), 'spare': ('cat_spare', 'სათადარიგო ნაწილები')}


CONTENTS = [('drones', 'kit_drone', 'დრონი P150 MAX'), ('batteries', 'kit_batteries', 'აკუმულატორები'),
            ('chargers', 'kit_chargers', 'დამტენები'), ('rtk', 'kit_rtk', 'RTK სადგური'),
            ('generators', 'kit_generators', 'გენერატორები')]
HOME_PARTS = ['09-017-00083', '09-017-00069', '09-017-00065', '05-002-02311', '09-016-00083']


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
    if kit:
        fb, w, h, pos = KIT_IMG[r.get('image') or 'flight']
        return (f'<div class="product-photo"><img src="/assets/img/{fb}" width="{w}" height="{h}" alt="{n}" '
                f'style="object-position:{pos}" loading="lazy" decoding="async"></div>')
    key, ka = CAT_KEY[r['group']]
    return (f'<div class="product-photo product-tile tile-{r["group"]}"><svg viewBox="0 0 48 48" width="56" height="56" fill="none" '
            f'stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICON[r["group"]]}</svg>'
            f'<span class="tile-label" data-i18n="{key}">{ka}</span></div>')


def card(r):
    kit = r['group'] == 'kit'
    n = html.escape(r['name'], quote=True)
    s = r['sku']
    p = price(r, kit)
    return (f'<article class="product{" product-kit" if kit else ""}" data-cat="{r["group"]}">{photo(r, kit)}'
            f'<div class="product-body"><p class="product-sku">{s}</p><h3>{n}</h3>{contents(r) if kit else ""}'
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
kits = [r for r in rows if r['group'] == 'kit']
parts = [r for r in rows if r['group'] != 'kit']
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
                      (r'(<div class="shop-grid home-parts" id="homeParts">).*?(</div>\s*<!--/homeParts-->)', '\n' + ''.join(card(by_sku[s]) for s in HOME_PARTS if s in by_sku))]:
    ht, n = re.subn(pattern, lambda m: m.group(1) + body + m.group(2), ht, count=1, flags=re.S)
    if n != 1:
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
