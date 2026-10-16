"""XAG P150 MAX platform configurator (owner brief, 16 Oct 2026).

One builder, used on the standalone platform page (/p150-max-platform, build-products.py) and on the P150 MAX page
(<!--configurator--> marker, build-shop.py). Every price comes from scripts/catalog.csv (the owner's price list), every
stock limit from scripts/stock.csv, the package contents from the catalog kit rows: listings, cart, worker and configurator
read the same numbers. Pricing rule: individual shop prices; when the selection contains a complete package, the
configurator offers the existing package price (+ the remaining items at shop price) with a switch button. No other
discounts. Starts with the platform only; nothing paid is preselected.
Georgian text is here (data-i18n keys); en/ru are written to content.js by build-shop.py (TEXT).
"""
import csv, html, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLATFORM = '09-007-00188'
PAGE = '/p150-max-platform'
# (catalog column used by the package rows or own key, sku, i18n key, Georgian label, optional?)
ENERGY = [('remotes', '05-002-02725', 'pc_remote', 'მართვის პულტი SRC5', False),
          ('batteries', '09-017-00073', 'pc_battery', 'აკუმულატორი B141050', False),
          ('chargers', '09-017-00069', 'pc_charger', 'დამტენი CM13600S', False),
          ('towers', '09-017-00065', 'pc_tower', 'აკუმულატორის გამაგრილებელი ავზი', False),
          ('generators', '09-017-00109', 'pc_generator', 'დამუხტვის სადგური (გენერატორი) GC4000+', True)]
EXTRA = [('rtk', '09-016-00083', 'pc_rtk', 'მობილური RTK სადგური XRTK7', True),
         ('spreader', '09-023-00145', 'pc_revocast', 'გრანულების გამფანტველი RevoCast 5', True),
         ('sling', '05-002-02682', 'pc_revosling', 'ტვირთის საკიდი სისტემა RevoSling (შასით)', True),
         ('nozzle4', '05-002-02640', 'pc_nozzle4', '4-გამფრქვევიანი განახლების კომპლექტი (P150 MAX)', True)]
KIT_COLS = ['remotes', 'batteries', 'chargers', 'towers', 'rtk', 'generators']
# Owner, 16 Oct 2026: the same equipment bought one by one. Checked against the catalog at every build.
OWNER_EQUIVALENT = {'PDG-P150MAX-STARTER': 79590, 'PDG-P150MAX-PRO': 95587, 'PDG-P150MAX-BUSINESS': 114583}

TEXT = {  # key: (ka, en, ru)
    'pc_remote': ('მართვის პულტი SRC5', 'SRC5 remote controller', 'Пульт управления SRC5'),
    'pc_battery': ('აკუმულატორი B141050', 'B141050 battery', 'Аккумулятор B141050'),
    'pc_charger': ('დამტენი CM13600S', 'CM13600S charger', 'Зарядное устройство CM13600S'),
    'pc_tower': ('აკუმულატორის გამაგრილებელი ავზი', 'Battery cooling tank', 'Охлаждающий бак для аккумуляторов'),
    'pc_generator': ('დამუხტვის სადგური (გენერატორი) GC4000+', 'GC4000+ charging station (generator)', 'Зарядная станция (генератор) GC4000+'),
    'pc_rtk': ('მობილური RTK სადგური XRTK7', 'XRTK7 mobile RTK station', 'Мобильная RTK-станция XRTK7'),
    'pc_revocast': ('გრანულების გამფანტველი RevoCast 5', 'RevoCast 5 granule spreader', 'Разбрасыватель гранул RevoCast 5'),
    'pc_revosling': ('ტვირთის საკიდი სისტემა RevoSling (შასით)', 'RevoSling cargo system (with landing gear)', 'Грузовая система RevoSling (с шасси)'),
    'pc_nozzle4': ('4-გამფრქვევიანი განახლების კომპლექტი (P150 MAX)', '4-Nozzle Upgrade Kit (P150 MAX)', 'Комплект модернизации на 4 форсунки (P150 MAX)'),
    'pc_title': ('კონფიგურატორი', 'Configurator', 'Конфигуратор'),
    'pc_intro': ('დაიწყეთ მხოლოდ პლატფორმით და დაამატეთ ის, რაც გჭირდებათ. სამუშაოდ საჭიროა თავსებადი მართვის პულტი, აკუმულატორები და დამტენები — თუ ისინი უკვე არ გაქვთ. დამუხტვის სადგური (გენერატორი) და RTK სადგური არასავალდებულოა.',
                 'Start with the platform only and add what you need. To work, you need a compatible remote controller, batteries and chargers — unless you already have them. The charging station (generator) and the RTK station are optional.',
                 'Начните только с платформы и добавьте то, что нужно. Для работы нужны совместимый пульт, аккумуляторы и зарядные устройства — если у вас их ещё нет. Зарядная станция (генератор) и RTK-станция — по желанию.'),
    'pc_base': ('პლატფორმა', 'Platform', 'Платформа'),
    'pc_platform': ('XAG P150 MAX პლატფორმა (RevoSpray 5)', 'XAG P150 MAX platform (RevoSpray 5)', 'Платформа XAG P150 MAX (RevoSpray 5)'),
    'pc_energy': ('მართვა და ენერგია', 'Control and power', 'Управление и питание'),
    'pc_extra': ('დამატებითი აღჭურვილობა', 'Additional equipment', 'Дополнительное оборудование'),
    'pc_optional': ('არასავალდებულო', 'optional', 'по желанию'),
    'pc_each': ('/ ცალი', '/ each', '/ шт.'),
    'pc_summary': ('თქვენი კონფიგურაცია', 'Your configuration', 'Ваша конфигурация'),
    'pc_total': ('ჯამი, დღგ-ს ჩათვლით', 'Total incl. VAT', 'Итого с НДС'),
    'pc_send': ('კონფიგურაციის გაგზავნა', 'Send configuration', 'Отправить конфигурацию'),
    'pc_cart': ('კალათაში დამატება', 'Add to cart', 'В корзину'),
    'pc_rule': ('ფასები — მაღაზიის ფასები ცალ-ცალკე. კომპლექტის ფასი მოქმედებს, როცა კონფიგურაცია კომპლექტის სრულ შემადგენლობას შეიცავს.',
                'Prices are the shop prices of each item. The package price applies when the configuration contains a complete package.',
                'Цены — цены магазина за каждую позицию. Цена комплекта действует, когда конфигурация содержит полный состав комплекта.'),
    'pc_offer_exact': ('ეს კონფიგურაცია ზუსტად ემთხვევა {name} კომპლექტს.', 'This configuration matches the {name} package exactly.', 'Эта конфигурация точно совпадает с комплектом {name}.'),
    'pc_offer_contains': ('ეს კონფიგურაცია შეიცავს {name} კომპლექტს.', 'This configuration contains the {name} package.', 'Эта конфигурация содержит комплект {name}.'),
    'pc_offer_price': ('კომპლექტის ფასით: {total} — ცალ-ცალკე {single}. დაზოგავთ {save}.', 'At the package price: {total} — {single} item by item. You save {save}.',
                       'По цене комплекта: {total} — по отдельности {single}. Экономия {save}.'),
    'pc_switch': ('{name} კომპლექტის ფასზე გადასვლა', 'Switch to the {name} package price', 'Перейти на цену комплекта {name}'),
    'pc_unswitch': ('ცალ-ცალკე ფასებით ჩვენება', 'Show item-by-item prices', 'Показать цены по отдельности'),
    'pc_in_pkg': ('კომპლექტის ფასით', 'at the package price', 'по цене комплекта'),
    'pc_remind': ('კონფიგურაციაში არ არის: {list}. თუ თავსებადი აღჭურვილობა უკვე გაქვთ, შეგიძლიათ ასე გაგზავნოთ.',
                  'Not in this configuration: {list}. If you already have compatible equipment, you can send it as it is.',
                  'В конфигурации нет: {list}. Если у вас уже есть совместимое оборудование, можно отправить так.'),
    'pc_need_remote': ('მართვის პულტი', 'remote controller', 'пульт управления'),
    'pc_need_batteries': ('აკუმულატორები', 'batteries', 'аккумуляторы'),
    'pc_need_chargers': ('დამტენები', 'chargers', 'зарядные устройства'),
    'pc_compare': ('კომპლექტები — შედარება', 'Packages compared', 'Сравнение комплектов'),
    'pc_compare_intro': ('იგივე აღჭურვილობა ცალ-ცალკე და კომპლექტში.', 'The same equipment bought item by item and as a package.', 'То же оборудование по отдельности и в комплекте.'),
    'pc_single': ('ცალ-ცალკე', 'Item by item', 'По отдельности'),
    'pc_pkg_price': ('კომპლექტში', 'As a package', 'В комплекте'),
    'pc_save': ('დაზოგავთ {save}', 'You save {save}', 'Экономия {save}'),
    'pc_load': ('კონფიგურაციაში ჩასმა', 'Load into the configurator', 'Загрузить в конфигуратор'),
    'pc_pkg_page': ('კომპლექტის გვერდი', 'Package page', 'Страница комплекта'),
    'pc_msg_title': ('გამარჯობა! მაინტერესებს XAG P150 MAX-ის კონფიგურაცია:', 'Hello! I am interested in this XAG P150 MAX configuration:', 'Здравствуйте! Меня интересует конфигурация XAG P150 MAX:'),
    'pc_msg_missing': ('კონფიგურაციაში არ არის', 'Not in the configuration', 'В конфигурации нет'),
    'pc_msg_link': ('ბმული', 'Link', 'Ссылка'),
    'pc_contents_of': ('შემადგენლობა', 'Contents', 'Состав'),
}


def load():
    rows = {r['sku']: r for r in csv.DictReader(open(ROOT / 'scripts/catalog.csv', encoding='utf-8'))}
    stock = {r['sku']: int(r['qty']) for r in csv.DictReader(open(ROOT / 'scripts/stock.csv', encoding='utf-8'))}
    return rows, stock


def gel(r):
    v = (r.get('gel') or '').strip()
    if not v or (r.get('avail') or '') == 'quote':
        raise SystemExit(f'configurator: {r["sku"]} has no approved shop price')
    return int(v)


def data():
    rows, stock = load()
    p = rows[PLATFORM]
    items = {}
    for group, lst in (('energy', ENERGY), ('extra', EXTRA)):
        for key, sku, lab, ka, opt in lst:
            items[key] = {'sku': sku, 'name': rows[sku]['name'], 'price': gel(rows[sku]), 'max': stock.get(sku, 0), 'group': group, 'label': lab}
    kit_parts = {'remotes': '05-002-02725', 'batteries': '09-017-00073', 'chargers': '09-017-00069', 'towers': '09-017-00065',
                 'rtk': '09-016-00083', 'generators': '09-017-00109'}
    pkgs = []
    for r in rows.values():
        if r['group'] != 'kit':
            continue
        q = {c: int((r.get(c) or '0').strip() or 0) for c in KIT_COLS if (r.get(c) or '').strip() and int(r[c])}
        if int((r.get('drones') or '0').strip() or 0) != 1:
            raise SystemExit('configurator: package without exactly one drone: ' + r['sku'])
        single = gel(p) + sum(n * items[c]['price'] for c, n in q.items())
        lim = [stock.get(PLATFORM, 0)] + [stock.get(kit_parts[c], 0) // n for c, n in q.items()]
        slug = r['sku'].split('-')[-1].lower()
        pkgs.append({'sku': r['sku'], 'name': r['name'], 'short': r['name'].replace('XAG P150 MAX ', ''), 'price': gel(r), 'single': single,
                     'q': q, 'max': min(lim), 'url': f'/p150-max-{slug}', 'key': slug})
        want = OWNER_EQUIVALENT.get(r['sku'])
        if want is not None and want != single:
            print(f'WARNING configurator: {r["sku"]} item-by-item total {single:,} differs from the owner figure {want:,} (catalog prices changed?)')
    return {'platform': {'sku': PLATFORM, 'name': p['name'], 'price': gel(p), 'max': stock.get(PLATFORM, 0)},
            'items': items, 'packages': pkgs, 'page': PAGE}


def _row(key, it, ka, opt):
    lab = it['label']
    return (f'<div class="pcfg-row" data-key="{key}"><div class="pcfg-name"><span data-i18n="{lab}">{html.escape(ka)}</span>'
            + (' <span class="pcfg-opt" data-i18n="pc_optional">არასავალდებულო</span>' if opt else '') +
            f'<span class="pcfg-unit">₾{it["price"]:,} <span data-i18n="pc_each">/ ცალი</span></span></div>'
            f'<div class="pcfg-qty"><div class="qty-stepper"><button type="button" class="qty-btn" data-step="-1" aria-label="რაოდენობის შემცირება" data-i18n-aria="qty_less">−</button>'
            f'<input class="qty-input" type="number" inputmode="numeric" min="0" max="{it["max"]}" step="1" value="0" aria-label="{html.escape(ka, quote=True)}" data-i18n-aria="{lab}">'
            f'<button type="button" class="qty-btn" data-step="1" aria-label="რაოდენობის გაზრდა" data-i18n-aria="qty_more">+</button></div>'
            f'<span class="pcfg-line" aria-hidden="true"></span></div></div>')


def block(heading='h2'):
    d = data()
    t = {k: v[0] for k, v in TEXT.items()}
    lst = {k: (ka, opt) for k, s, l, ka, opt in ENERGY + EXTRA}
    energy = ''.join(_row(k, d['items'][k], *lst[k]) for k, *_ in ENERGY)
    extra = ''.join(_row(k, d['items'][k], *lst[k]) for k, *_ in EXTRA)
    comp = ''.join(
        f'<li class="pcfg-pkg"><div class="pcfg-pkg-head"><a class="pcfg-pkg-name" href="{p["url"]}" data-local>{html.escape(p["name"])}</a>'
        f'<span class="pcfg-pkg-save" data-save="{p["single"] - p["price"]}">−₾{p["single"] - p["price"]:,}</span></div>'
        f'<p class="pcfg-pkg-in" data-pkg-in="{p["sku"]}"></p>'
        f'<dl class="pcfg-pkg-prices"><div><dt data-i18n="pc_single">ცალ-ცალკე</dt><dd><s>₾{p["single"]:,}</s></dd></div>'
        f'<div><dt data-i18n="pc_pkg_price">კომპლექტში</dt><dd><strong>₾{p["price"]:,}</strong></dd></div></dl>'
        f'<button type="button" class="button button-line pcfg-load" data-load="{p["sku"]}"><span data-i18n="pc_load">კონფიგურაციაში ჩასმა</span></button></li>'
        for p in d['packages'])
    cfg = html.escape(json.dumps(d, ensure_ascii=False), quote=True)
    h = heading
    return (f'<section class="section pcfg-section" id="configurator" aria-labelledby="pcfg-title"><div class="container">'
            f'<div class="section-heading"><{h} id="pcfg-title" data-i18n="pc_title">{t["pc_title"]}</{h}></div>'
            f'<p class="page-intro" data-i18n="pc_intro">{t["pc_intro"]}</p>'
            f'<div class="pcfg" id="platformConfig" data-config="{cfg}">'
            f'<div class="pcfg-options">'
            f'<div class="pcfg-group"><p class="pcfg-legend" data-i18n="pc_base">პლატფორმა</p>'
            f'<div class="pcfg-row pcfg-fixed"><div class="pcfg-name"><span data-i18n="pc_platform">{t["pc_platform"]}</span>'
            f'<span class="pcfg-unit">₾{d["platform"]["price"]:,}</span></div><div class="pcfg-qty"><output class="pcfg-fixed-qty">1</output>'
            f'<span class="pcfg-line">₾{d["platform"]["price"]:,}</span></div></div></div>'
            f'<fieldset class="pcfg-group"><legend class="pcfg-legend" data-i18n="pc_energy">მართვა და ენერგია</legend>{energy}</fieldset>'
            f'<fieldset class="pcfg-group"><legend class="pcfg-legend" data-i18n="pc_extra">დამატებითი აღჭურვილობა</legend>{extra}</fieldset>'
            f'</div>'
            f'<aside class="pcfg-summary" id="pcSummary" aria-labelledby="pcSumTitle"><h3 id="pcSumTitle" data-i18n="pc_summary">თქვენი კონფიგურაცია</h3>'
            f'<ul class="pcfg-list" id="pcList"></ul>'
            f'<div class="pcfg-offer" id="pcOffer" hidden><p id="pcOfferText"></p><p id="pcOfferPrice"></p>'
            f'<button type="button" class="button button-line" id="pcSwitch"><span></span></button></div>'
            f'<p class="pcfg-remind" id="pcRemind" role="status" hidden></p>'
            f'<p class="pcfg-total-label" data-i18n="pc_total">ჯამი, დღგ-ს ჩათვლით</p><p class="pcfg-total" id="pcTotal" aria-live="polite"></p>'
            f'<div class="pcfg-actions"><button class="button button-red" id="pcWa" type="button"><span data-i18n="pc_send">კონფიგურაციის გაგზავნა</span></button>'
            f'<button class="button button-line" id="pcCart" type="button"><span data-i18n="pc_cart">კალათაში დამატება</span></button></div>'
            f'<p class="small-note" data-i18n="pc_rule">{t["pc_rule"]}</p></aside></div>'
            f'<div class="pcfg-bar" id="pcBar" aria-hidden="true"><div><span class="pcfg-bar-label" data-i18n="pc_total">ჯამი, დღგ-ს ჩათვლით</span>'
            f'<strong id="pcBarTotal"></strong></div><button class="button button-red" type="button" id="pcBarSend" tabindex="-1"><span data-i18n="pc_send">კონფიგურაციის გაგზავნა</span></button></div>'
            f'<div class="pcfg-compare" id="pcCompare"><h3 data-i18n="pc_compare">კომპლექტები — შედარება</h3><p class="small-note" data-i18n="pc_compare_intro">{t["pc_compare_intro"]}</p>'
            f'<ul class="pcfg-pkgs">{comp}</ul></div>'
            f'</div></section>')
