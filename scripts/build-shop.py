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
    'legacy': '<path d="M24 20v8M14 24h20"/>',
    'spare': '<path d="M31 9a8 8 0 0 0-9.5 10.5L10 31a3 3 0 0 0 4.2 4.2l11.5-11.5A8 8 0 0 0 36 14l-5 5-4.5-1.2L25.3 13z"/>',
}
CAT_KEY = {'power': ('cat_power', 'აკუმულატორები და დატენვა'), 'spray': ('cat_spray', 'შეწამვლა და გაფანტვა'),
           'control': ('cat_control', 'მართვა და RTK'), 'acc': ('cat_acc', 'აქსესუარები'), 'spare': ('cat_spare', 'სათადარიგო ნაწილები'),
           'drone': ('cat_drone', 'დრონები'), 'legacy': ('cat_legacy', 'წინა თაობის მოდელი')}


# Package contents (owner, 14 Oct 2026, exact): catalog column, content key, Georgian label. en/ru labels in KIT_LABELS.
CONTENTS = [('drones', 'kit_drone', 'XAG P150 MAX (RevoSpray 5)'),
            ('remotes', 'kit_remote', 'XAG SRC5 მართვის პულტი'),
            ('batteries', 'kit_batteries', 'XAG B141050 აკუმულატორი'),
            ('chargers', 'kit_chargers', 'XAG CM13600S დამტენი'),
            ('towers', 'kit_towers', 'XAG აკუმულატორის გამაგრილებელი ავზი'),
            ('rtk', 'kit_rtk', 'XAG XRTK7 მობილური RTK სადგური'),
            ('generators', 'kit_generators', 'XAG GC4000+ გენერატორი')]
KIT_LABELS = {'kit_drone': ('XAG P150 MAX (RevoSpray 5)', 'XAG P150 MAX (RevoSpray 5)'),
              'kit_remote': ('XAG SRC5 remote controller', 'Пульт управления XAG SRC5'),
              'kit_batteries': ('XAG B141050 battery', 'Аккумулятор XAG B141050'),
              'kit_chargers': ('XAG CM13600S charger', 'Зарядное устройство XAG CM13600S'),
              'kit_towers': ('XAG battery cooling tank', 'Охлаждающий бак для аккумуляторов XAG'),
              'kit_rtk': ('XAG XRTK7 mobile RTK station', 'Мобильная RTK-станция XAG XRTK7'),
              'kit_generators': ('XAG GC4000+ charging station', 'Зарядная станция XAG GC4000+')}
# Home page 'Parts and energy system': B141050 battery, GC4000+, CM13600S charger, 6 kW parallel charging kit, cooling tank, XRTK7.
import product_pages
HOME_PARTS = ['09-017-00073', '09-017-00109', '09-017-00069', '05-002-02311', '09-017-00065', '09-016-00083']


def contents(r, cls='kit-contents'):
    """Package contents from the catalog columns batteries / chargers / generators (empty = not shown)."""
    # package cards (23 Oct 2026): the RTK row is always shown, '—' when not included, so the three cards compare line by line
    parts = [f'<div><dt data-i18n="{key}">{ka}</dt><dd>{r.get(col, "").strip()}</dd></div>' if (r.get(col) or '').strip()
             else f'<div class="is-none"><dt data-i18n="{key}">{ka}</dt><dd><span aria-hidden="true">—</span><span class="visually-hidden" data-i18n="cmp_none">არ შედის</span></dd></div>'
             for col, key, ka in CONTENTS if (r.get(col) or '').strip() or (col == 'rtk' and r.get('group') == 'kit')]
    return f'<dl class="{cls}">{"".join(parts)}</dl>' if parts else ''


def price(r, kit):
    """A fixed GEL price in the catalog wins; otherwise Agrifuture USD x markup x rate.
    None = no approved price (quote-only part or previous-generation model): never sold at ₾0."""
    if (r.get('gel') or '').strip():
        return int(Decimal(r['gel'].strip()))
    if (r.get('usd') or '').strip():
        return gel(r['usd'], pricing.MARKUP_KITS if kit else pricing.MARKUP_PARTS)
    return None


def status(r):
    """in_stock = invoice/price-list item (as shown on the site so far; remaining quantity not verified),
    quote = part from the XAG parts catalogues, not on the packing list: not in stock, price on request,
    out = previous-generation model (not in stock, consultation only)."""
    if r['group'] == 'legacy':
        return 'out'
    return 'in_stock' if price(r, r['group'] == 'kit') is not None and (r.get('avail') or '') != 'quote' else 'quote'


# Stock (owner, 15 Oct 2026): scripts/stock.csv = quantities from the NIK Electronics packing list, nothing sold yet.
STOCK = {r['sku']: int(r['qty']) for r in csv.DictReader(open(ROOT / 'scripts/stock.csv', encoding='utf-8'))}
KIT_PARTS = {'drones': '09-007-00188', 'remotes': '05-002-02725', 'batteries': '09-017-00073', 'chargers': '09-017-00069',
             'towers': '09-017-00065', 'rtk': '09-016-00083', 'generators': '09-017-00109'}


def stock_max(r):
    """Verified stock limit: parts = packing-list quantity; a package = how many complete sets the stock allows."""
    if r['group'] == 'kit':
        lim = [STOCK.get(KIT_PARTS[k], 0) // int(r[k]) for k in KIT_PARTS if (r.get(k) or '').strip() and int(r[k])]
        return min(lim) if lim else 0
    return STOCK.get(r['sku'], 0)


def stepper(s, n, mx=0):
    """Quantity selector (positive whole numbers). data-max is set only when a verified stock limit exists."""
    mxa = f' max="{mx}"' if mx else ''
    return (f'<div class="qty-stepper" data-for="{s}"><button type="button" class="qty-btn" data-step="-1" aria-label="რაოდენობის შემცირება" data-i18n-aria="qty_less">−</button>'
            f'<input class="qty-input" type="number" inputmode="numeric" min="1"{mxa} step="1" value="1" aria-label="რაოდენობა" data-i18n-aria="qty_label">'
            f'<button type="button" class="qty-btn" data-step="1" aria-label="რაოდენობის გაზრდა" data-i18n-aria="qty_more">+</button></div>')


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
    page = product_pages.url(s)
    t = html.escape(r["name"])
    if page:
        t = f'<a href="{page}" data-local>{t}</a>'
    return (f'<li class="part-row"><div class="part-row-name"><span class="part-row-title">{t}</span>'
            f'<span class="product-sku">{s}</span></div><span class="part-row-price">₾{p:,}</span>'
            f'<button type="button" class="add-btn" data-sku="{s}" data-name="{n}" data-price="{p}" data-i18n="add_to_cart">კალათაში</button></li>\n')


def search_k(r):
    """The full price-list name stays searchable in the shop filter after the display name was shortened."""
    full = r.get('name_ka_full') or ''
    return f' data-k="{html.escape(full, quote=True)}"' if full and full != r.get('name_ka') else ''


def card(r):
    kit = r['group'] == 'kit'
    n = html.escape(r['name'], quote=True)
    s = r['sku']
    p = price(r, kit)
    st = status(r)
    page = product_pages.url(s)
    pic, ttl = photo(r, kit), title(r)
    more = ''
    if page and st == 'out':  # previous model: photo and name open its gallery page
        pic = f'<a class="product-link" href="{page}" data-local>{pic}</a>'
        ttl = f'<a class="product-link" href="{page}" data-local>{ttl}</a>'
    elif page:  # own product page with the official specs: the photo and the name open it
        pic = f'<a class="product-link" href="{page}" data-local>{pic}</a>'
        ttl = f'<a class="product-link" href="{page}" data-local>{ttl}</a>'
        mk, mt = ('pd_pk_more', 'შემადგენლობა და ფოტოები') if kit else ('pd_more', 'მახასიათებლები')
        more = f'<a class="text-link product-more" href="{page}" data-local><span data-i18n="{mk}">{mt}</span><span aria-hidden="true">→</span></a>'
    head = (f'<article class="product{" product-kit" if kit else ""}{" product-out" if st == "out" else ""}" data-cat="{r["group"]}" data-avail="{st}"{search_k(r)}>{pic}'
            f'<div class="product-body">{cat(r)}<p class="product-sku">{s}</p>{ttl}{contents(r) if kit else ""}{more}')
    if st == 'out':  # previous-generation model: no price, no purchase, consultation instead
        spec = LEGACY_SPECS.get(s)
        return (head + (f'<p class="product-specs" data-i18n="{pkey(s)}_spec">{html.escape(spec[0])}</p>' if spec else '')
                + '<p class="product-stock is-out" data-i18n="out_of_stock">არ არის მარაგში</p>'
                + '<div class="product-buy"><a class="button button-line consult-btn" href="/consultation" data-local><span data-i18n="consult_cta">კონსულტაცია</span></a></div><a class="text-link model-newer" href="/p150-max" data-local><span data-i18n="lg_newer">ახალი თაობა: XAG P150 MAX</span><span aria-hidden="true">→</span></a></div></article>\n')
    if st == 'quote':  # no approved price: ask for a quote, never add to the cart at ₾0
        # Owner, 14 Oct 2026: a part that is not on the packing list is not in stock.
        return (head + '<p class="product-stock is-out" data-i18n="out_of_stock">არ არის მარაგში</p>'
                + '<div class="product-buy"><span class="product-price product-price-quote" data-i18n="price_on_request">ფასი მოთხოვნით</span>'
                + f'<button type="button" class="quote-btn" data-sku="{s}" data-name="{n}" data-i18n="request_quote">ფასის მოთხოვნა</button></div></div></article>\n')
    return (head + '<p class="product-stock" data-i18n="in_stock">საწყობშია</p>'
            f'<div class="product-buy"><span class="product-price">₾{p:,}</span><div class="buy-actions">{stepper(s, n, stock_max(r))}'
            f'<button type="button" class="add-btn" data-sku="{s}" data-name="{n}" data-price="{p}" data-i18n="add_to_cart">კალათაში</button></div></div></div></article>\n')


# Package comparison (owner brief, 19 Oct 2026): only what differs, from the catalog columns; what all three share in one line.
CMP_LABEL = {'drones': ('P150 MAX პლატფორმა (RevoSpray 5)', 'P150 MAX platform (RevoSpray 5)', 'платформа P150 MAX (RevoSpray 5)'),
             'remotes': ('SRC5 მართვის პულტი', 'SRC5 remote controller', 'пульт SRC5'),
             'batteries': ('B141050 აკუმულატორი', 'B141050 battery', 'аккумулятор B141050'),
             'chargers': ('CM13600S დამტენი', 'CM13600S charger', 'зарядное устройство CM13600S'),
             'towers': ('აკუმულატორის გამაგრილებელი ავზი', 'battery cooling tank', 'бак охлаждения аккумуляторов'),
             'rtk': ('XRTK7 RTK სადგური', 'XRTK7 RTK station', 'RTK-станция XRTK7'),
             'generators': ('GC4000+ გენერატორი', 'GC4000+ generator', 'генератор GC4000+')}
CMP_TEXT = {'cmp_title': ('რით განსხვავდება კომპლექტები', 'How the packages differ', 'Чем отличаются комплекты'),
            'cmp_price': ('ფასი', 'Price', 'Цена'),
            'cmp_separate': ('ცალკე', 'separate', 'отдельно'),
            'cmp_power_note': ('GC4000+ გენერატორი კომპლექტებში არ შედის და იყიდება ცალკე. დამტენებს სჭირდება შესაბამისი კვების წყარო — სხვა გენერატორის თავსებადობა წინასწარ შეგვითანხმეთ.',
                               'The GC4000+ generator is not part of any package and is sold separately. The chargers need a suitable power source; check any other generator with us before you rely on it.',
                               'Генератор GC4000+ не входит в комплекты и продаётся отдельно. Зарядным устройствам нужен подходящий источник питания — совместимость другого генератора согласуйте с нами заранее.'),
            'cmp_all': ('ყველა კომპლექტი და შემადგენლობა', 'All packages and contents', 'Все комплекты и состав'),
            'cmp_corner': ('კომპლექტი', 'Package', 'Комплект')}
_CMP_COLS = ['drones', 'remotes', 'batteries', 'chargers', 'towers', 'rtk', 'generators']


def _n(r, c):
    v = (r.get(c) or '').strip()
    return int(v) if v.isdigit() else 0


def compare_text(kits):
    common = [c for c in _CMP_COLS if all(_n(r, c) == _n(kits[0], c) for r in kits) and _n(kits[0], c)]
    lead = ('სამივე კომპლექტში შედის: ', 'All three packages include: ', 'Во все три комплекта входят: ')
    return tuple(lead[i] + ', '.join((f"{_n(kits[0], c)} × " if _n(kits[0], c) > 1 else '') + CMP_LABEL[c][i] for c in common) + '.' for i in range(3))


def _kit_short(r):
    return re.sub(r"^XAG P150 MAX ", "", r["name"])


def _kit_line(r, i):
    """One-line summary per package for the phone cards: batteries · chargers · RTK (when included)."""
    b, c, k = _n(r, 'batteries'), _n(r, 'chargers'), _n(r, 'rtk')
    if i == 0:
        parts = [f'{b} აკუმულატორი', f'{c} დამტენი'] + (['RTK სადგური'] if k else [])
    elif i == 1:
        parts = [f'{b} batteries', f'{c} chargers'] + (['RTK station'] if k else [])
    else:
        parts = [f'аккумуляторы: {b}', f'зарядные: {c}'] + (['RTK-станция'] if k else [])
    return ' · '.join(parts)


PICK = 'PDG-P150MAX-PRO'  # owner/ChatGPT review 19 Oct 2026: Pro gets the subtle accent


def compare(kits, more_href):
    """Package comparison (19 Oct 2026, second version): only what differs + price + link; no explanatory paragraphs.
    Desktop: table. Phone: three stacked cards."""
    diff = ['batteries', 'chargers', 'rtk']
    pick = lambda r: ' is-pick' if r['sku'] == PICK else ''
    head = ''.join(f'<th scope="col" class="pkg-col{pick(r)}">{html.escape(_kit_short(r))}</th>' for r in kits)
    body = ''
    for c in diff:
        cells = ''.join(f'<td class="pkg-col{pick(r)}">{_n(r, c)}</td>' if _n(r, c)
                        else f'<td class="pkg-col is-none{pick(r)}"><span aria-hidden="true">—</span><span class="visually-hidden" data-i18n="cmp_none">არ შედის</span></td>' for r in kits)
        body += f'<tr><th scope="row" data-i18n="cmp_l_{c}">{CMP_LABEL[c][0]}</th>{cells}</tr>'
    body += ('<tr class="pkg-compare-price"><th scope="row" data-i18n="cmp_price">ფასი</th>'
             + ''.join(f'<td class="pkg-col{pick(r)}">₾{price(r, True):,}</td>' for r in kits) + '</tr>')
    body += ('<tr class="pkg-compare-links"><th scope="row"><span class="visually-hidden" data-i18n="cmp_corner">კომპლექტი</span></th>'
             + ''.join(f'<td class="pkg-col{pick(r)}"><a class="text-link" href="{product_pages.url(r["sku"])}" data-local><span data-i18n="cmp_view">კომპლექტაციის ნახვა</span><span aria-hidden="true">→</span></a></td>' for r in kits) + '</tr>')
    cards = ''.join(
        f'<li class="pkg-card{pick(r)}"><a href="{product_pages.url(r["sku"])}" data-local>'
        f'<span class="pkg-card-head"><span class="pkg-card-name">{html.escape(_kit_short(r))}</span><span class="pkg-card-price">₾{price(r, True):,}</span></span>'
        f'<span class="pkg-card-line" data-i18n="cmp_line_{r["sku"].split("-")[-1].lower()}">{_kit_line(r, 0)}</span>'
        f'<span class="pkg-card-cta"><span data-i18n="cmp_view">კომპლექტაციის ნახვა</span><span aria-hidden="true">→</span></span></a></li>' for r in kits)
    return (f'<div class="pkg-compare"><h3 class="pkg-compare-title" data-i18n="cmp_title">რით განსხვავდება კომპლექტები</h3>'
            f'<div class="pkg-compare-scroll"><table class="pkg-compare-table"><thead><tr><th scope="col"><span class="visually-hidden" data-i18n="cmp_corner">კომპლექტი</span></th>{head}</tr></thead><tbody>{body}</tbody></table></div>'
            f'<ul class="pkg-cards">{cards}</ul></div>')

def _tile_desc(r, i):
    """Short contents line for a package listing, from the catalog columns (ka / en / ru)."""
    b, c, t, k = _n(r, 'batteries'), _n(r, 'chargers'), _n(r, 'towers'), _n(r, 'rtk')
    if i == 0:
        s = f'დრონი, SRC5 პულტი, {b} აკუმულატორი, {c} დამტენი, {t} გამაგრილებელი ავზი' + (', XRTK7 RTK სადგური' if k else '')
    elif i == 1:
        s = f'Drone, SRC5 remote, {b} batteries, {c} chargers, {t} cooling tanks' + (', XRTK7 RTK station' if k else '')
    else:
        s = f'Дрон, пульт SRC5, аккумуляторы: {b}, зарядные устройства: {c}, баки охлаждения: {t}' + (', RTK-станция XRTK7' if k else '')
    return s + '.'


TILE_TEXT = {
    'tile_platform_desc': ('დრონი RevoSpray 5 სისტემით. პულტი, აკუმულატორები და დამტენები იყიდება ცალკე.',
                           'Drone with the RevoSpray 5 system. Remote, batteries and chargers are sold separately.',
                           'Дрон с системой RevoSpray 5. Пульт, аккумуляторы и зарядные устройства продаются отдельно.'),
    'tile_platform_view': ('პლატფორმის ნახვა', 'View the platform', 'Смотреть платформу'),
    'tile_platform_name': ('პლატფორმა', 'Platform', 'Платформа'),
}


def tiles(platform, kits):
    """P150 MAX page (owner, 19 Oct 2026 final brief): four image-led listings - Platform, Starter, Pro, Business -
    each with its picture, name, price, short contents line and a link to its own page. Replaces the text comparison table."""
    out = []
    for r in platform + kits:
        s = r['sku']
        kit = r['group'] == 'kit'
        href = product_pages.url(s)
        name = html.escape(r['name'], quote=True)
        short = _kit_short(r) if kit else None
        desc_key = f'tile_desc_{s.split("-")[-1].lower()}' if kit else 'tile_platform_desc'
        desc_ka = _tile_desc(r, 0) if kit else TILE_TEXT['tile_platform_desc'][0]
        label = (f'<span class="pkg-tile-name">{html.escape(short)}</span>' if kit
                 else '<span class="pkg-tile-name" data-i18n="tile_platform_name">პლატფორმა</span>')
        view = ('<span data-i18n="cmp_view">კომპლექტაციის ნახვა</span>' if kit
                else '<span data-i18n="tile_platform_view">პლატფორმის ნახვა</span>')
        pick = ' is-pick' if s == PICK else ''
        out.append(
            f'<li class="pkg-tile{pick}" data-sku="{s}" data-name="{name}" data-price="{price(r, kit)}" data-kit="{int(kit)}">'
            f'<a class="pkg-tile-link" href="{href}" data-local>'
            f'<span class="pkg-tile-photo"><img src="/assets/img/products/{s}.webp" width="1200" height="900" alt="{name}" loading="lazy" decoding="async"></span>'
            f'<span class="pkg-tile-body"><span class="pkg-tile-model">XAG P150 MAX</span>{label}'
            f'<span class="pkg-tile-desc" data-i18n="{desc_key}">{html.escape(desc_ka)}</span>'
            f'<span class="pkg-tile-price">₾{price(r, kit):,}</span>'
            f'<span class="pkg-tile-cta">{view}<span aria-hidden="true">→</span></span></span></a></li>')
    return '<ul class="pkg-tiles">' + ''.join(out) + '</ul>'


def kit_row(r):
    n = html.escape(r['name'], quote=True)
    s = r['sku']
    p = price(r, True)
    short = re.sub(r'^XAG P150 Max\s*', '', r['name']).strip() or r['name']
    return (f'<li class="kit-row"><div class="kit-row-name"><span class="kit-row-title"><a href="{product_pages.url(s)}" data-local>{html.escape(short)}</a></span>{contents(r, "kit-contents kit-contents-inline")}</div>'
            f'<span class="kit-row-price">₾{p:,}</span><div class="buy-actions">{stepper(s, n, stock_max(r))}'
            f'<button type="button" class="add-btn" data-sku="{s}" data-name="{n}" data-price="{p}" data-i18n="add_to_cart">კალათაში</button></div></li>\n')


rows = list(csv.DictReader(open(ROOT / 'scripts/catalog.csv', encoding='utf-8')))
# Audit 19 Oct 2026: cards, cart and chat use the short Georgian name; the full price-list name stays in catalog.csv (search keyword).
from display_names import short_ka
for _r in rows:
    _r['name_ka_full'] = (_r.get('name_ka') or '').strip()
    _r['name_ka'] = short_ka(_r['sku'], _r.get('name_ka'))
import legacy_models
LEGACY_SPECS = {m['sku']: m['specs'] for m in legacy_models.MODELS}
rows += [{'group': 'legacy', 'name': m['name'], 'name_ka': m['name_ka'], 'name_ru': '', 'sku': m['sku'], 'usd': '', 'gel': '',
          'image': '', 'drones': '', 'batteries': '', 'chargers': '', 'rtk': '', 'generators': '', 'avail': 'legacy'} for m in legacy_models.MODELS]
import configurator as _pc
PLATFORM_TEXT = dict(_pc.TEXT)
PLATFORM_TEXT.update({
    'pp_eyebrow': ('ცალკე პლატფორმა', 'Platform only', 'Только платформа'),
    'pp_notice': ('ფასში შედის დრონი RevoSpray 5 სისტემით. მართვის პულტი, აკუმულატორები და დამტენები იყიდება ცალკე. ეს არ არის სრული სამუშაო კომპლექტი.',
                  'The price includes the drone with the RevoSpray 5 system. The remote controller, batteries and chargers are sold separately. This is not a complete working set.',
                  'В цену входит дрон с системой RevoSpray 5. Пульт управления, аккумуляторы и зарядные устройства продаются отдельно. Это не полный рабочий комплект.'),
    'pp_sub': ('სასოფლო-სამეურნეო დრონი · RevoSpray\u00a05', 'Agricultural drone · RevoSpray\u00a05', 'Сельскохозяйственный дрон · RevoSpray\u00a05'),
    'pp_back': ('← მაღაზია', '← Shop', '← Магазин'),
    'pm_cfg_link': tuple(t.format(int([r for r in csv.DictReader(open(ROOT / 'scripts/catalog.csv', encoding='utf-8')) if r['sku'] == _pc.PLATFORM][0]['gel']))
                         for t in ('კონფიგურაციის აწყობა — ₾{:,}-დან', 'Build your configuration — from ₾{:,}', 'Собрать конфигурацию — от ₾{:,}')),
    'pm_cfg_note': ('საწყისი ფასი — მხოლოდ დრონი RevoSpray 5 სისტემით.', 'Starting price: the drone with RevoSpray 5 only.', 'Начальная цена — только дрон с RevoSpray 5.'),
    'pp_configure': ('კონფიგურაციის აწყობა', 'Build your configuration', 'Собрать конфигурацию'),
    'pm_pl_platform': ('პლატფორმა (მხოლოდ დრონი)', 'Platform (drone only)', 'Платформа (только дрон)'),
    'pm_pl_kits': ('სრული კომპლექტები', 'Complete packages', 'Полные комплекты'),
    'pm_pl_kits_v': tuple(t.format(min(int(r['gel']) for r in csv.DictReader(open(ROOT / 'scripts/catalog.csv', encoding='utf-8')) if r['group'] == 'kit'))
                          for t in ('₾{:,}-დან', 'from ₾{:,}', 'от ₾{:,}')),
    'pm_pl_note': ('კომპლექტებში შედის SRC5 პულტი, აკუმულატორები და დამტენები; პლატფორმაში — არა.',
                   'Packages include the SRC5 remote, batteries and chargers; the platform does not.',
                   'В комплекты входят пульт SRC5, аккумуляторы и зарядные устройства; в платформу — нет.')})
import json as _json
_cj = ROOT / 'dist/assets/js/content.js'
_c = _json.loads(_cj.read_text(encoding='utf-8').split('=', 1)[1].strip().removesuffix(';'))
for _lang in ('en', 'ru', 'ka'):
    for _k in [k for k in _c[_lang] if k.startswith('pn_')]:
        del _c[_lang][_k]
for r in rows:
    if (r.get('name_ka') or '').strip():
        _c['ka'][pkey(r['sku'])] = r['name_ka'].strip()  # the cart shows the visitor's language (shop.js)
        _c['en'][pkey(r['sku'])] = r['name']
        _c['ru'][pkey(r['sku'])] = (r.get('name_ru') or '').strip() or r['name']
for _k, _ka, in [(k, ka) for _c_, k, ka in CONTENTS]:
    _c['ka'][_k] = _ka
    _c['en'][_k], _c['ru'][_k] = KIT_LABELS[_k]
_kits_for_text = [r for r in rows if r['group'] == 'kit']
PLATFORM_TEXT.update(CMP_TEXT)
PLATFORM_TEXT['cmp_common'] = compare_text(_kits_for_text)
PLATFORM_TEXT['cmp_view'] = ('კომპლექტაციის ნახვა', 'View package', 'Смотреть комплект')
PLATFORM_TEXT['cmp_none'] = ('არ შედის', 'not included', 'не входит')
for _r in _kits_for_text:
    PLATFORM_TEXT['cmp_line_' + _r['sku'].split('-')[-1].lower()] = tuple(_kit_line(_r, _i) for _i in range(3))
for _col, _lab in CMP_LABEL.items():
    PLATFORM_TEXT['cmp_l_' + _col] = _lab
for _k, (_ka, _en, _ru) in PLATFORM_TEXT.items():
    _c['ka'][_k], _c['en'][_k], _c['ru'][_k] = _ka, _en, _ru
for _s, (_ka, _en, _ru) in LEGACY_SPECS.items():
    _c['en'][pkey(_s) + '_spec'], _c['ru'][pkey(_s) + '_spec'] = _en, _ru
_cj.write_text('window.PDG_CONTENT = ' + _json.dumps(_c, ensure_ascii=False, indent=2) + ';\n', encoding='utf-8')
kits = [r for r in rows if r['group'] == 'kit']
parts = [r for r in rows if r['group'] not in ('kit', 'legacy', 'drone')]
platform = [r for r in rows if r['group'] == 'drone']  # owner, 16 Oct 2026: standalone P150 MAX platform (own row below the packages)
legacy = [r for r in rows if r['group'] == 'legacy']
for _k, _v in TILE_TEXT.items():
    _c['ka'][_k], _c['en'][_k], _c['ru'][_k] = _v
for _r in kits:
    _k = f'tile_desc_{_r["sku"].split("-")[-1].lower()}'
    _c['ka'][_k], _c['en'][_k], _c['ru'][_k] = (_tile_desc(_r, 0), _tile_desc(_r, 1), _tile_desc(_r, 2))
_cj.write_text('window.PDG_CONTENT = ' + _json.dumps(_c, ensure_ascii=False, indent=2) + ';\n', encoding='utf-8')
# Shop order: drone, energy, control/RTK, spraying/spreading, accessories, spare parts; most expensive first in each group.
ORDER = ['drone', 'power', 'control', 'spray', 'acc', 'spare']
parts.sort(key=lambda r: (ORDER.index(r['group']) if r['group'] in ORDER else 99, price(r, False) is None, -(price(r, False) or 0), r['name']))
for r in rows:
    if r['group'] not in {'kit', *ICON}:
        raise SystemExit(f'Unknown group {r["group"]!r} for {r["sku"]}')

# P150 MAX configurator (owner, 16 Oct 2026): shared builder in scripts/configurator.py, also used by the platform page.
import configurator as PCFG


def platform_link():
    """P150 MAX page hero (23 Oct 2026): the two price levels side by side - platform only vs complete packages (catalog prices)."""
    p = price(by_sku_all[PCFG.PLATFORM], False)
    k = min(price(r, True) for r in kits)
    return ('<div class="pm-pricebar">'
            f'<a class="pm-price-item" href="/p150-max-platform" data-local><span class="pm-price-label" data-i18n="pm_pl_platform">პლატფორმა (მხოლოდ დრონი)</span><span class="pm-price-val">₾{p:,}</span></a>'
            f'<a class="pm-price-item" href="#kits"><span class="pm-price-label" data-i18n="pm_pl_kits">სრული კომპლექტები</span><span class="pm-price-val" data-i18n="pm_pl_kits_v">₾{k:,}-დან</span></a>'
            '<p class="pm-pricebar-note" data-i18n="pm_pl_note">კომპლექტებში შედის SRC5 პულტი, აკუმულატორები და დამტენები; პლატფორმაში — არა.</p></div>')


def platform_kit_row(r):
    """P150 MAX page package table: the platform-only option first (owner, 18 Oct 2026), opening the configurator."""
    p = price(r, False)
    return ('<li class="kit-row kit-row-platform"><div class="kit-row-name"><span class="kit-row-title"><a href="/p150-max-platform" data-local data-i18n="pc_platform">XAG P150 MAX პლატფორმა (RevoSpray 5)</a></span>'
            '<span class="kit-row-note" data-i18n="pp_notice">ფასში შედის დრონი RevoSpray 5 სისტემით. მართვის პულტი, აკუმულატორები და დამტენები იყიდება ცალკე. ეს არ არის სრული სამუშაო კომპლექტი.</span></div>'
            f'<span class="kit-row-price">₾{p:,}</span><a class="button button-line kit-row-cfg" href="/p150-max-platform#configurator" data-local><span data-i18n="pp_configure">კონფიგურაციის აწყობა</span></a></li>\n')


def platform_row(r):
    """Standalone platform listing in the shop (owner, 17 Oct 2026: above the packages): drone only, link to its page and configurator."""
    p = price(r, False)
    return ('<div class="platform-row"><a class="platform-row-photo" href="/p150-max-platform" data-local>'
            f'<img src="/assets/img/products/{r["sku"]}.webp" width="1200" height="900" alt="{html.escape(r["name"], quote=True)}" loading="lazy" decoding="async"></a>'
            '<div class="platform-row-body"><p class="product-cat" data-i18n="pp_eyebrow">ცალკე პლატფორმა</p>'
            f'<h3><a class="product-link" href="/p150-max-platform" data-local data-i18n="pc_platform">XAG P150 MAX პლატფორმა (RevoSpray 5)</a></h3>'
            '<div class="pp-price-row"><p class="pp-price"><span class="product-price">₾{0:,}</span> <span class="pd-vat" data-i18n="pd_vat">ფასი დღგ-ს ჩათვლით</span></p>'.format(p) +
            '<p class="pp-notice" data-i18n="pp_notice">ფასში შედის დრონი RevoSpray 5 სისტემით. მართვის პულტი, აკუმულატორები და დამტენები იყიდება ცალკე. ეს არ არის სრული სამუშაო კომპლექტი.</p></div>'
            '<a class="button button-line" href="/p150-max-platform#configurator" data-local><span data-i18n="pp_configure">კონფიგურაციის აწყობა</span><span aria-hidden="true">→</span></a>'
            '</div></div>')


by_sku_all = {r['sku']: r for r in rows}
import json
pb = ROOT / 'scripts/page-bodies.html'
t = pb.read_text(encoding='utf-8')
subs = [
    (r'(<div class="shop-grid kit-grid">\n).*?(</div>\n<!--/kitGrid-->)', ''.join(card(r) for r in kits)),
    (r'(<!--platformRow-->\n).*?(<!--/platformRow-->)', ''.join(platform_row(r) for r in platform) + '\n'),
    (r'(<div class="shop-grid" id="partsGrid">\n).*?(</div>\n<!--partsMore-->)', ''.join(card(r).replace('<article class="product"', '<article hidden class="product"', 1) if i >= 24 else card(r) for i, r in enumerate(parts))),  # first 24 visible, the rest revealed by "Load more" (shop.js PAGE)
    (r'(<div class="shop-grid" id="legacyGrid">\n).*?(</div></div></section>)', ''.join(card(r) for r in legacy)),
    # Owner, 16 Oct 2026 (second brief): the full configurator lives only on /p150-max-platform; the P150 MAX page links to it.
    (r'(<!--configurator-->\n).*?(<!--/configurator-->)', ''),
    (r'(<!--platformLink-->).*?(<!--/platformLink-->)', platform_link()),
    (r'(<!--pmCompare-->).*?(<!--/pmCompare-->)', tiles(platform, kits)),
    (r'(<!--drKits-->).*?(<!--/drKits-->)', tiles(platform, kits).replace('data-kit="1"', 'data-kit="0"')),  # /drones (owner 19 Oct 2026): same four listings; schema stays on /p150-max
]
home = ROOT / 'dist/index.html'
ht = home.read_text(encoding='utf-8')
by_sku = {r['sku']: r for r in rows}
for pattern, body in [(r'(<!--homePlatform-->).*?(<!--/homePlatform-->)', ''.join(platform_row(r) for r in platform)),  # owner, 18 Oct 2026: platform first wherever the packages are
                      (r'(<div class="shop-grid kit-grid" id="homePackages">).*?(</div>\s*<!--/homePackages-->)', '\n' + ''.join(card(r) for r in kits)),
                      (r'(<!--homeCompare-->).*?(<!--/homeCompare-->)', compare(kits, '/shop#kits')),
                      (r'(<ul class="part-list" id="homeParts">).*?(</ul>\s*<!--/homeParts-->)', '\n' + ''.join(part_row(by_sku[s]) for s in HOME_PARTS if s in by_sku))]:
    ht, n = re.subn(pattern, lambda m: m.group(1) + body + m.group(2), ht, count=1, flags=re.S)
    # owner, 19 Oct 2026 (02:42): the home page has no packages section any more; these markers are optional.
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
        what = ', '.join(f"{r[c]} × {KIT_LABELS[k][0]}" for c, k, _ in CONTENTS if (r.get(c) or '').strip())
        return f"- {r['name']}: {price(r, True):,} GEL" + (f" ({what})" if what else '')
    extra = [r for r in platform + parts if (r.get('gel') or '').strip()]
    block = '## Packages (prices in GEL)\n' + '\n'.join(line(r) for r in kits) + '\n' + \
            '\n'.join(f"- {r['name']}: {price(r, False):,} GEL" for r in extra) + '\n\n'
    text = llms.read_text(encoding='utf-8')
    text = re.sub(r'## Packages \(prices in GEL\)\n.*?\n\n', lambda m: block, text, flags=re.S)
    llms.write_text(text, encoding='utf-8')

# Payment worker (Cloudflare Pages advanced mode): server-side prices from this same catalog.
sys.path.insert(0, str(ROOT / 'scripts'))
import json, site_config
cat = {r['sku']: [r['name'], price(r, r['group'] == 'kit'), stock_max(r)] for r in rows if price(r, r['group'] == 'kit') is not None}
tpl = (ROOT / 'scripts/worker.template.js').read_text(encoding='utf-8')
rules = {'threshold': site_config.PAYMENTS['threshold'], 'depositPercent': site_config.PAYMENTS['deposit_percent'],
         'shippingFee': site_config.SHIPPING['fee'], 'freeFrom': site_config.SHIPPING['free_from']}
# Knowledge for the AI chat: business facts (llms.txt), every product with its price, payment rules, terms, FAQ.
CATN = {'kit': 'P150 MAX package', 'drone': 'drone', 'legacy': 'previous-generation XAG drone', 'power': 'batteries and charging', 'spray': 'spraying and spreading', 'control': 'control and RTK',
        'acc': 'accessories', 'spare': 'spare parts'}
cdata = json.loads((ROOT / 'dist/assets/js/content.js').read_text(encoding='utf-8').split('=', 1)[1].strip().removesuffix(';'))['en']
know = [(ROOT / 'dist/llms.txt').read_text(encoding='utf-8').strip(), '',
        '## Website shop (prices in GEL incl. VAT). Availability: "listed in stock" = in stock (owner, 15 Oct 2026: nothing from the price list has been sold yet; the team still confirms the exact quantity '
        'with every order); "not in stock, price on request" = a part we do not have in stock (the team gives the price on request); "not in stock (previous model)" = consultation only.']
for r in rows:
    extra = ', '.join(f"{r[c]} × {KIT_LABELS[k][0]}" for c, k, _ in CONTENTS if (r.get(c) or '').strip())
    local = f" [ka: {r['name_ka']}]" if (r.get('name_ka') or '').strip() else ''
    p_ = price(r, r['group'] == 'kit'); st_ = status(r)
    what = f"{p_:,} GEL, listed in stock" if st_ == 'in_stock' else ('not in stock, price on request' if st_ == 'quote' else 'not in stock (previous model), consultation only')
    know.append(f"- {r['name']}{local} (code {r['sku']}, {CATN[r['group']]}): {what}" + (f" — contains {extra}" if extra else ''))
_pd = _pc.data()
know += ['', '## Standalone platform and configurator (owner, 16 Oct 2026)',
         f"The XAG P150 MAX Platform ({_pd['platform']['price']:,} GEL, code {_pd['platform']['sku']}) is the drone with the RevoSpray 5 system only: the SRC5 remote controller, batteries and chargers are NOT included and it is not a complete working set. "
         "It suits operators who already own compatible equipment; others should add a controller, batteries and chargers in the configurator (https://premium-drones.ge/p150-max-platform) or choose a package. Generator and RTK are optional.",
         "Controller (owner, 23 Oct 2026): PDG stocks and supplies the XAG SRC5 Smart Remote Controller; it is in the Starter, Pro and Business packages and also sold separately. "
         "The XAG ACS4 Control Stick appears in XAG's official P150 MAX specifications as a compatible accessory, but PDG does not supply it: never offer it or say it is included.",
         'Packages are cheaper than the same equipment bought item by item: ' + '; '.join(f"{p['name']} {p['price']:,} GEL instead of {p['single']:,} GEL" for p in _pd['packages']) + '.']
know += ['', '## Buying and payment',
         "Online card payment is NOT available on the website at the moment; do not tell customers they can pay online. Do not mention deposit percentages.",
         'Orders are sent from the cart by WhatsApp or email; PDG confirms price, stock and delivery, then sends an invoice and the customer pays by bank transfer.',
         f"Delivery within Georgia: GEL {rules['shippingFee']} for orders under GEL {rules['freeFrom']}, free from GEL {rules['freeFrom']}. Pickup from the Tbilisi storage (by appointment) is free.", '', '## Terms']
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
              f'window.PDG_PAY={{endpoint:"/api",threshold:{rules["threshold"]},depositPercent:{rules["depositPercent"]},shippingFee:{rules["shippingFee"]},freeFrom:{rules["freeFrom"]}}};\n', encoding='utf-8')
print(f'payments: worker with {len(cat)} prices; full payment under GEL {rules["threshold"]:,}, {rules["depositPercent"]}% deposit above')
