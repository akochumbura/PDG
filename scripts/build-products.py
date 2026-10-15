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
     'pd_fits_control': ('XAG P150 MAX-ის მართვა და კავშირი', 'XAG P150 MAX control and communication', 'Управление и связь XAG P150 MAX'),
     'pd_vat': ('ფასი დღგ-ს ჩათვლით', 'Price incl. VAT', 'Цена с НДС'),
     'cfg_tower': ('გამაგრილებელი ავზი', 'Cooling tank', 'Охлаждающий бак'),
     'pd_pk_more': ('შემადგენლობა და ფოტოები', 'Contents and photos', 'Состав и фото'),
     'pd_pk_in': ('კომპლექტში შედის', 'The package includes', 'В комплект входит'),
     'pd_pk_back': ('← კომპლექტები', '← Packages', '← Комплекты'),
     'pd_pk_photo_note': ('პირველი ფოტო ზუსტად აჩვენებს კომპლექტის შემადგენლობას; დანარჩენი ფოტოები — XAG P150 MAX.',
                          'The first photo shows exactly what the package contains; the other photos show the XAG P150 MAX.',
                          'Первое фото точно показывает состав комплекта; остальные фото — XAG P150 MAX.'),
     'pd_pk_specs': ('P150 MAX-ის სრული მახასიათებლები', 'Full P150 MAX specifications', 'Полные характеристики P150 MAX'),
     'pd_pk_cfg': ('კომპლექტის შეცვლა კონფიგურატორში', 'Change the package in the configurator', 'Изменить комплект в конфигураторе'),
     'pd_pk_photo': ('ფოტო', 'Photo', 'Фото')}


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


GROUPS = {g['id']: g['blocks'] for g in S.SPECS}
rows = {r['sku']: r for r in csv.DictReader(open(ROOT / 'scripts/catalog.csv', encoding='utf-8'))}
PHOTOS = ROOT / 'dist/assets/img/products'
out = []
for p in P.PAGES:
    r = rows.get(p['sku'])
    if not r or not (r.get('gel') or '').strip() or (r.get('avail') or '') == 'quote':
        raise SystemExit(f'product page {p["slug"]}: {p["sku"]} is not a priced price-list item in catalog.csv')
    sku, pid = p['sku'], p['slug'].replace('-', '_')
    head, specs = GROUPS[p.get('specs', 'power')][p['block']]
    name_en = html.escape(r['name'], quote=True)
    gel = int(r['gel'])
    for k in ('title', 'intro'):
        put(f'pd_{pid}_{k}', p[k])
    # Short product heading (the page title without " — price and specifications"); the long price-list name stays in search and cards.
    put(f'pd_{pid}_h1', tuple(t.split(' — ')[0] for t in p['title']))
    stock = {row['sku']: int(row['qty']) for row in csv.DictReader(open(ROOT / 'scripts/stock.csv', encoding='utf-8'))}.get(sku, 0)
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
        + (f'<p class="eyebrow" data-i18n="pd_fits_control">{T["pd_fits_control"][0]}</p>' if p.get('specs') == 'control' else f'<p class="eyebrow" data-i18n="pd_fits">{T["pd_fits"][0]}</p>') +
        f'<h1 data-i18n="pd_{pid}_h1">{html.escape(p["title"][0].split(" — ")[0])}</h1><p class="product-orig">{html.escape(r["name"])}</p>'
        f'<p class="page-intro" data-i18n="pd_{pid}_intro">{html.escape(p["intro"][0])}</p></div></section>\n'
        f'  <section class="section pd-main"><div class="container pd-grid">{pic}'
        f'<article class="product pd-buybox" data-cat="{r["group"]}" data-avail="in_stock">'
        f'<p class="product-sku"><span data-i18n="pd_code">მწარმოებლის კოდი</span>: {sku}</p>'
        f'<p class="product-stock" data-i18n="in_stock">საწყობშია</p>'
        f'<p class="pd-price"><span class="product-price">₾{gel:,}</span> <span class="pd-vat" data-i18n="pd_vat">ფასი დღგ-ს ჩათვლით</span></p>'
        f'<div class="buy-actions"><div class="qty-stepper" data-for="{sku}"><button type="button" class="qty-btn" data-step="-1" aria-label="რაოდენობის შემცირება" data-i18n-aria="qty_less">−</button>'
        f'<input class="qty-input" type="number" inputmode="numeric" min="1"' + (f' max="{stock}"' if stock else '') + ' step="1" value="1" aria-label="რაოდენობა" data-i18n-aria="qty_label">'
        f'<button type="button" class="qty-btn" data-step="1" aria-label="რაოდენობის გაზრდა" data-i18n-aria="qty_more">+</button></div>'
        f'<button type="button" class="add-btn" data-sku="{sku}" data-name="{name_en}" data-price="{gel}" data-i18n="add_to_cart">კალათაში</button></div>'
        f'<a class="button button-line pd-ask" href="{html.escape(wa, quote=True)}" target="_blank" rel="noopener noreferrer"><span data-i18n="pd_ask">კითხვა WhatsApp-ით</span></a>'
        f'</article></div></section>\n'
        f'  <section class="section pd-specs" id="specifications" aria-labelledby="pd-specs-title"><div class="container">'
        f'<div class="section-heading"><h2 id="pd-specs-title"><span data-i18n="pd_specs">მახასიათებლები</span></h2></div>'
        f'<div class="spec-block pd-spec-block">{label("h3", f"pd_{pid}_head", head)}<dl>{dl}</dl></div>'
        f'<p class="small-note"><a href="https://www.xa.com/en/p150max/p150maxspecs" target="_blank" rel="noopener noreferrer" data-i18n="pd_source">{html.escape(T["pd_source"][0])}</a></p>'
        f'</div></section>\n</template>\n')


# ---- P150 MAX package pages (gallery + exact contents) ----
CONTENTS = [  # same order and labels as build-shop.py CONTENTS (Georgian label from content.js kit_* keys)
    ('drones', 'kit_drone'), ('remotes', 'kit_remote'), ('batteries', 'kit_batteries'), ('chargers', 'kit_chargers'),
    ('towers', 'kit_towers'), ('rtk', 'kit_rtk'), ('generators', 'kit_generators')]
LINK = {'remotes': '05-002-02725', 'batteries': '09-017-00073', 'chargers': '09-017-00069', 'towers': '09-017-00065', 'rtk': '09-016-00083', 'generators': '09-017-00109'}
KIT_INTRO = {
    'p150-max-starter': ('საბაზისო კომპლექტი: დრონი, მართვის პულტი, 4 აკუმულატორი, 2 დამტენი და 2 გამაგრილებელი ავზი.',
                         'Base package: drone, remote controller, 4 batteries, 2 chargers and 2 cooling tanks.',
                         'Базовый комплект: дрон, пульт, 4 аккумулятора, 2 зарядных устройства и 2 охлаждающих бака.'),
    'p150-max-pro': ('Starter-ის შემადგენლობა, დამატებით 2 აკუმულატორი და XRTK7 მობილური RTK სადგური.',
                     'Everything in Starter plus 2 more batteries and the XRTK7 mobile RTK station.',
                     'Всё из Starter, плюс 2 аккумулятора и мобильная RTK-станция XRTK7.'),
    'p150-max-business': ('Pro-ს შემადგენლობა, სულ 8 აკუმულატორით და 4 დამტენით — დიდი ფართობებისთვის.',
                          'Everything in Pro with 8 batteries and 4 chargers in total, for large areas.',
                          'Всё из Pro, всего 8 аккумуляторов и 4 зарядных устройства — для больших площадей.')}
for i, (f, ka, en, ru) in enumerate(P.GALLERY, 1):
    put(f'pd_g{i}', (ka, en, ru))
for sku, slug in P.KITS.items():
    r = rows[sku]
    pid = slug.replace('-', '_')
    gel = int(r['gel'])
    name = html.escape(r['name'], quote=True)
    put(f'pd_{pid}_intro', KIT_INTRO[slug])
    put(f'pd_{pid}_title', (f'{r["name"]} — კომპლექტი, შემადგენლობა და ფასი', f'{r["name"]} — package contents and price', f'{r["name"]} — состав комплекта и цена'))
    put(f'pd_{pid}_alt', (f'{r["name"]} — კომპლექტის შემადგენლობა', f'{r["name"]} — package contents', f'{r["name"]} — состав комплекта'))
    items = []
    for col, key in CONTENTS:
        n = (r.get(col) or '').strip()
        if not n:
            continue
        lab = f'<span data-i18n="{key}">{html.escape(c["ka"][key])}</span>'
        if col == 'drones':  # the drone itself: the P150 MAX page (description and full specifications)
            lab = f'<a href="/p150-max.html" data-local>{lab}</a>'
        elif col in LINK:
            lab = f'<a href="{P.url(LINK[col])}" data-local>{lab}</a>'
        items.append(f'<li><span class="pk-qty">{n} ×</span> {lab}</li>')
    pics = [(f'/assets/img/products/{sku}.webp', f'/assets/img/packages/{sku}-t.webp', f'pd_{pid}_alt', c['ka'][f'pd_{pid}_alt'])]
    pics += [(f'/assets/img/packages/{f}', f'/assets/img/packages/{f.replace(".webp", "-t.webp")}', f'pd_g{i}', ka) for i, (f, ka, en, ru) in enumerate(P.GALLERY, 1)]
    thumbs = ''.join(f'<button type="button" class="pk-thumb{" is-on" if j == 0 else ""}" data-full="{full}" aria-label="{html.escape(alt, quote=True)}" data-i18n-aria="{key}"{" aria-current=\"true\"" if j == 0 else ""}>'
                     f'<img src="{th}" width="240" height="180" alt="" loading="lazy" decoding="async"></button>'
                     for j, (full, th, key, alt) in enumerate(pics))
    wa = 'https://wa.me/995550004333?text=' + quote(f'გამარჯობა! მაინტერესებს {r["name"]} ({gel:,} ₾).')
    # Stock limit = complete sets the packing-list stock allows (same rule as build-shop.py stock_max).
    _st = {row['sku']: int(row['qty']) for row in csv.DictReader(open(ROOT / 'scripts/stock.csv', encoding='utf-8'))}
    _parts = {'drones': '09-007-00188', 'remotes': '05-002-02725', 'batteries': '09-017-00073', 'chargers': '09-017-00069',
              'towers': '09-017-00065', 'rtk': '09-016-00083', 'generators': '09-017-00109'}
    _lim = [_st.get(v, 0) // int(r[k]) for k, v in _parts.items() if (r.get(k) or '').strip() and int(r[k])]
    kit_max = min(_lim) if _lim else 0
    out.append(
        f'<template data-page="{slug}.html" data-ka-title="{html.escape(r["name"] + " — კომპლექტის შემადგენლობა და ფასი | საქართველოს პრემიუმ დრონები", quote=True)}" data-title="pd_{pid}_title" data-description="pd_{pid}_intro">\n'
        f'  <section class="page-hero pd-hero"><div class="container"><a class="back-link" href="/shop.html#kits" data-local data-i18n="pd_pk_back">← კომპლექტები</a>'
        f'<p class="eyebrow">XAG P150 MAX</p><h1>{html.escape(r["name"])}</h1>'
        f'<p class="page-intro" data-i18n="pd_{pid}_intro">{html.escape(KIT_INTRO[slug][0])}</p></div></section>\n'
        f'  <section class="section pd-main"><div class="container pd-grid">'
        f'<div class="pk-gallery"><div class="product-photo pd-photo pk-main"><img id="pkMain" src="{pics[0][0]}" width="1200" height="900" alt="{html.escape(pics[0][3], quote=True)}" data-i18n-alt="{pics[0][2]}" decoding="async"></div>'
        f'<div class="pk-thumbs" aria-label="ფოტო" data-i18n-aria="pd_pk_photo">{thumbs}</div>'
        f'<p class="small-note" data-i18n="pd_pk_photo_note">{html.escape(T["pd_pk_photo_note"][0])}</p></div>'
        f'<article class="product product-kit pd-buybox" data-cat="kit" data-avail="in_stock">'
        f'<p class="pd-price"><span class="product-price">₾{gel:,}</span> <span class="pd-vat" data-i18n="pd_vat">ფასი დღგ-ს ჩათვლით</span></p>'
        f'<h2 class="pk-in-title" data-i18n="pd_pk_in">კომპლექტში შედის</h2><ul class="pk-in">{"".join(items)}</ul>'
        f'<div class="buy-actions"><div class="qty-stepper" data-for="{sku}"><button type="button" class="qty-btn" data-step="-1" aria-label="რაოდენობის შემცირება" data-i18n-aria="qty_less">−</button>'
        f'<input class="qty-input" type="number" inputmode="numeric" min="1"' + (f' max="{kit_max}"' if kit_max else '') + ' step="1" value="1" aria-label="რაოდენობა" data-i18n-aria="qty_label">'
        f'<button type="button" class="qty-btn" data-step="1" aria-label="რაოდენობის გაზრდა" data-i18n-aria="qty_more">+</button></div>'
        f'<button type="button" class="add-btn" data-sku="{sku}" data-name="{name}" data-price="{gel}" data-i18n="add_to_cart">კალათაში</button></div>'
        f'<a class="button button-line pd-ask" href="{html.escape(wa, quote=True)}" target="_blank" rel="noopener noreferrer"><span data-i18n="pd_ask">კითხვა WhatsApp-ით</span></a>'
        f'<p class="pk-links"><a class="text-link" href="/p150-max.html#specifications" data-local><span data-i18n="pd_pk_specs">P150 MAX-ის სრული მახასიათებლები</span><span aria-hidden="true">→</span></a>'
        f'<a class="text-link" href="/p150-max.html?kit={sku.split('-')[-1].lower()}#configurator" data-local><span data-i18n="pd_pk_cfg">კომპლექტის შეცვლა კონფიგურატორში</span><span aria-hidden="true">→</span></a></p>'
        f'</article></div></section>\n</template>\n')

# ---- Previous-generation model pages (gallery, specs, consultation) ----
import legacy_models as LM
T2 = {'pd_lg_back': ('← წინა მოდელები', '← Previous models', '← Предыдущие модели'),
      'pd_lg_note': ('წინა თაობის მოდელი. ამჟამად არ არის მარაგში; მიიღეთ კონსულტაცია.', 'Previous-generation model. Currently out of stock; ask for a consultation.',
                     'Модель предыдущего поколения. Сейчас нет в наличии; получите консультацию.'),
      'pd_lg_eyebrow': ('წინა თაობა', 'Previous generation', 'Предыдущее поколение'),
      'pd_lg_source': ('წყარო: XAG-ის ოფიციალური მახასიათებლები (xa.com).', 'Source: official XAG specifications (xa.com).', 'Источник: официальные характеристики XAG (xa.com).')}
for k, v in T2.items():
    put(k, v)
for m in LM.MODELS:
    L = P.LEGACY[m['sku']]
    slug, pid = L['slug'], L['slug'].replace('-', '_')
    n = len(L['pics'])
    put(f'pd_{pid}_title', (f'{L["short"]} — წინა თაობის მოდელი, ფოტოები და მახასიათებლები', f'{L["short"]} — previous-generation model, photos and specifications',
                            f'{L["short"]} — модель предыдущего поколения, фото и характеристики'))
    put(f'pd_{pid}_intro', (f'{L["short"]} სასოფლო-სამეურნეო დრონი: ფოტოები და ოფიციალური მახასიათებლები. ამჟამად არ არის მარაგში.',
                            f'{L["short"]} agricultural drone: photos and official specifications. Currently out of stock.',
                            f'Сельскохозяйственный дрон {L["short"]}: фото и официальные характеристики. Сейчас нет в наличии.'))
    for i, a in enumerate(L['pics'], 1):
        put(f'pd_{pid}_g{i}', a)
    pics = [(f'/assets/img/models/{L["prefix"]}-{i}.webp', f'/assets/img/models/{L["prefix"]}-{i}-t.webp', f'pd_{pid}_g{i}', L['pics'][i - 1][0]) for i in range(1, n + 1)]
    thumbs = ''.join(f'<button type="button" class="pk-thumb{" is-on" if j == 0 else ""}" data-full="{full}" aria-label="{html.escape(alt, quote=True)}" data-i18n-aria="{key}"{" aria-current=\"true\"" if j == 0 else ""}>'
                     f'<img src="{th}" width="240" height="180" alt="" loading="lazy" decoding="async"></button>' for j, (full, th, key, alt) in enumerate(pics))
    spec_ka = m['specs'][0]
    put(f'pd_{pid}_spec', tuple(m['specs']))
    out.append(
        f'<template data-page="{slug}.html" data-ka-title="{html.escape(L["short"] + " — წინა თაობის მოდელი | საქართველოს პრემიუმ დრონები", quote=True)}" data-title="pd_{pid}_title" data-description="pd_{pid}_intro">\n'
        f'  <section class="page-hero pd-hero"><div class="container"><a class="back-link" href="/shop.html#previous-models" data-local data-i18n="pd_lg_back">← წინა მოდელები</a>'
        f'<p class="eyebrow" data-i18n="pd_lg_eyebrow">წინა თაობა</p><h1>{html.escape(L["short"])}</h1><p class="product-orig">{html.escape(m["name"])}</p>'
        f'<p class="page-intro" data-i18n="pd_{pid}_intro">{html.escape(c["ka"][f"pd_{pid}_intro"])}</p></div></section>\n'
        f'  <section class="section pd-main"><div class="container pd-grid">'
        f'<div class="pk-gallery"><div class="product-photo pd-photo pk-main"><img id="pkMain" src="{pics[0][0]}" width="1200" height="900" alt="{html.escape(pics[0][3], quote=True)}" data-i18n-alt="{pics[0][2]}" decoding="async"></div>'
        f'<div class="pk-thumbs" aria-label="ფოტო" data-i18n-aria="pd_pk_photo">{thumbs}</div></div>'
        f'<article class="product product-out pd-buybox" data-cat="legacy" data-avail="out">'
        f'<h2 class="pk-in-title" data-i18n="pd_specs">მახასიათებლები</h2><p class="product-specs" data-i18n="pd_{pid}_spec">{html.escape(spec_ka)}</p>'
        f'<p class="product-stock is-out" data-i18n="out_of_stock">არ არის მარაგში</p>'
        f'<p class="small-note" data-i18n="pd_lg_note">{html.escape(T2["pd_lg_note"][0])}</p>'
        f'<a class="button button-line consult-btn" href="/consultation" data-local><span data-i18n="consult_cta">კონსულტაცია</span></a>'
        f'<p class="small-note"><span data-i18n="pd_lg_source">{html.escape(T2["pd_lg_source"][0])}</span></p>'
        f'</article></div></section>\n</template>\n')

pb = ROOT / 'scripts/page-bodies.html'
t = pb.read_text(encoding='utf-8')
if '<!--product-pages-->' not in t:
    t = t.rstrip('\n') + '\n<!--product-pages-->\n<!--/product-pages-->\n'
t = re.sub(r'<!--product-pages-->\n.*?<!--/product-pages-->', lambda m: '<!--product-pages-->\n' + ''.join(out) + '<!--/product-pages-->', t, count=1, flags=re.S)
pb.write_text(t, encoding='utf-8')
cj.write_text('window.PDG_CONTENT = ' + json.dumps(c, ensure_ascii=False, indent=2) + ';\n', encoding='utf-8')
print(f'product pages: {len(out)} ({", ".join([p["slug"] for p in P.PAGES] + list(P.KITS.values()))})')
