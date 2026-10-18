"""XAG P150 MAX platform configurator (owner brief, 16 Oct 2026).

One builder, used on the standalone platform page (/p150-max-platform, build-products.py). Every price comes from scripts/catalog.csv (the owner's price list), every
stock limit from scripts/stock.csv, the package contents from the catalog kit rows: listings, cart, worker and configurator
read the same numbers. Pricing rule (owner, 16 Oct 2026, second brief): total at individual shop prices; every approved
package whose complete contents are in the selection is checked (package price + only the additional items) and the
lowest valid total is used automatically ("გამოყენებულია Pro კომპლექტის ფასი"). At most one package; quantities are
never changed; no prorating or partial discounts. Starts with the platform only; nothing paid is preselected.
Only the platform page shows the configurator (the P150 MAX page links to it).
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
          ('towers', '09-017-00065', 'pc_tower', 'აკუმულატორის გამაგრილებელი ავზი', False)]
EXTRA = [('generators', '09-017-00109', 'pc_generator', 'დამუხტვის სადგური (გენერატორი) GC4000+', True),
         ('rtk', '09-016-00083', 'pc_rtk', 'მობილური RTK სადგური XRTK7', True),
         ('spreader', '09-023-00145', 'pc_revocast', 'გრანულების გამფანტველი RevoCast 5', True),
         ('sling', '05-002-02682', 'pc_revosling', 'ტვირთის საკიდი სისტემა RevoSling (შასით)', True),
         ('nozzle4', '05-002-02640', 'pc_nozzle4', '4-გამფრქვევიანი განახლების კომპლექტი (P150 MAX)', True),
         ('led', '09-027-00003', 'pc_led', 'LED ფარი 90 ვტ', True)]  # owner, 18 Oct 2026: LED lights as an option for every setup
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
    'pc_led': ('LED ფარი 90 ვტ', '90 W LED headlight', 'Светодиодная фара 90 Вт'),
    'pc_title': ('კონფიგურატორი', 'Configurator', 'Конфигуратор'),
    'pc_intro': ('დაიწყეთ მხოლოდ პლატფორმით ან აირჩიეთ კომპლექტი. თუ არჩევანი კომპლექტის სრულ შემადგენლობას შეიცავს, კომპლექტის ფასი ავტომატურად გამოიყენება.',
                 'Start with the platform only or pick a package. When your selection contains a complete package, the package price is applied automatically.',
                 'Начните только с платформы или выберите комплект. Если выбор содержит полный состав комплекта, цена комплекта применяется автоматически.'),
    'pc_presets': ('სწრაფი არჩევანი', 'Quick choice', 'Быстрый выбор'),
    'pc_preset_none': ('მხოლოდ პლატფორმა', 'Platform only', 'Только платформа'),
    'pc_platform': ('XAG P150 MAX პლატფორმა (RevoSpray 5)', 'XAG P150 MAX platform (RevoSpray 5)', 'Платформа XAG P150 MAX (RevoSpray 5)'),
    'pc_energy': ('მართვა და ენერგია', 'Control and power', 'Управление и питание'),
    'pc_extra': ('დამატებითი აღჭურვილობა', 'Additional equipment', 'Дополнительное оборудование'),
    'pc_more_count': ('არჩეულია: {n}', 'selected: {n}', 'выбрано: {n}'),
    'pc_optional': ('არასავალდებულო', 'optional', 'по желанию'),
    'pc_each': ('/ ცალი', '/ each', '/ шт.'),
    'pc_summary': ('თქვენი კონფიგურაცია', 'Your configuration', 'Ваша конфигурация'),
    'pc_total': ('ჯამი, დღგ-ს ჩათვლით', 'Total incl. VAT', 'Итого с НДС'),
    'pc_send': ('კონფიგურაციის გაგზავნა', 'Send configuration', 'Отправить конфигурацию'),
    'pc_cart': ('კალათაში დამატება', 'Add to cart', 'В корзину'),
    'pc_applied': ('გამოყენებულია {name} კომპლექტის ფასი', '{name} package price applied', 'Применена цена комплекта {name}'),
    'pc_pkg_line': ('{name} კომპლექტი', '{name} package', 'Комплект {name}'),
    'pc_extras': ('დამატებით', 'In addition', 'Дополнительно'),
    'pc_remind': ('არ არის არჩეული: {list}. თუ თავსებადი აღჭურვილობა უკვე გაქვთ, შეგიძლიათ ასე გააგრძელოთ.',
                  'Not selected: {list}. If you already have compatible equipment, you can continue as it is.',
                  'Не выбрано: {list}. Если у вас уже есть совместимое оборудование, можно продолжить так.'),
    'pc_need_remote': ('მართვის პულტი', 'remote controller', 'пульт управления'),
    'pc_need_batteries': ('აკუმულატორები', 'batteries', 'аккумуляторы'),
    'pc_need_chargers': ('დამტენები', 'chargers', 'зарядные устройства'),
    'pc_msg_title': ('გამარჯობა! მაინტერესებს XAG P150 MAX-ის კონფიგურაცია:', 'Hello! I am interested in this XAG P150 MAX configuration:', 'Здравствуйте! Меня интересует конфигурация XAG P150 MAX:'),
    'pc_msg_missing': ('არ არის არჩეული', 'Not selected', 'Не выбрано'),
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


def _thumb(sku):
    f = ROOT / f'dist/assets/img/products/thumbs/{sku}.webp'
    if f.is_file():
        return f'<img class="pcfg-thumb" src="/assets/img/products/thumbs/{sku}.webp" width="96" height="72" alt="" loading="lazy" decoding="async">'
    return '<span class="pcfg-thumb" aria-hidden="true"></span>'


def _row(key, it, ka, opt):
    lab = it['label']
    return (f'<div class="pcfg-row" data-key="{key}">{_thumb(it["sku"])}<div class="pcfg-name"><span class="pcfg-label" data-i18n="{lab}">{html.escape(ka)}</span>'
            f'<span class="pcfg-unit">₾{it["price"]:,} <span data-i18n="pc_each">/ ცალი</span></span></div>'
            f'<div class="qty-stepper pcfg-stepper"><button type="button" class="qty-btn" data-step="-1" aria-label="რაოდენობის შემცირება" data-i18n-aria="qty_less">−</button>'
            f'<input class="qty-input" type="number" inputmode="numeric" min="0" max="{it["max"]}" step="1" value="0" aria-label="{html.escape(ka, quote=True)}" data-i18n-aria="{lab}">'
            f'<button type="button" class="qty-btn" data-step="1" aria-label="რაოდენობის გაზრდა" data-i18n-aria="qty_more">+</button></div></div>')


def block(heading='h2'):
    d = data()
    t = {k: v[0] for k, v in TEXT.items()}
    lst = {k: (ka, opt) for k, s_, l_, ka, opt in ENERGY + EXTRA}
    energy = ''.join(_row(k, d['items'][k], *lst[k]) for k, *_ in ENERGY)
    extra = ''.join(_row(k, d['items'][k], *lst[k]) for k, *_ in EXTRA)
    presets = (f'<button type="button" class="pcfg-preset" data-preset="none" aria-pressed="true"><span data-i18n="pc_preset_none">{t["pc_preset_none"]}</span></button>'
               + ''.join(f'<button type="button" class="pcfg-preset" data-preset="{p["sku"]}" aria-pressed="false">{html.escape(p["short"])}'
                         f' <span class="pcfg-preset-price">₾{p["price"]:,}</span></button>' for p in d['packages']))
    cfg = html.escape(json.dumps(d, ensure_ascii=False), quote=True)
    h = heading
    return (f'<section class="section pcfg-section" id="configurator" aria-labelledby="pcfg-title"><div class="container">'
            f'<div class="pcfg-head"><{h} id="pcfg-title" data-i18n="pc_title">{t["pc_title"]}</{h}><p class="pcfg-lead" data-i18n="pc_intro">{t["pc_intro"]}</p></div>'
            f'<div class="pcfg" id="platformConfig" data-config="{cfg}">'
            f'<div class="pcfg-options">'
            f'<div class="pcfg-presets" role="group" aria-labelledby="pcPresetsLabel"><span class="pcfg-presets-label" id="pcPresetsLabel" data-i18n="pc_presets">{t["pc_presets"]}</span>'
            f'<div class="pcfg-preset-list">{presets}</div></div>'
            f'<div class="pcfg-row pcfg-fixed">{_thumb(d["platform"]["sku"])}<div class="pcfg-name"><span class="pcfg-label" data-i18n="pc_platform">{t["pc_platform"]}</span>'
            f'<span class="pcfg-unit">₾{d["platform"]["price"]:,}</span></div><output class="pcfg-fixed-qty">1</output></div>'
            f'<div class="pcfg-group"><p class="pcfg-legend" data-i18n="pc_energy">{t["pc_energy"]}</p>{energy}</div>'
            f'<div class="pcfg-group pcfg-extra"><p class="pcfg-legend" data-i18n="pc_extra">{t["pc_extra"]}</p>{extra}</div>'
            f'</div>'
            f'<aside class="pcfg-summary" id="pcSummary" aria-labelledby="pcSumTitle"><h3 id="pcSumTitle" data-i18n="pc_summary">{t["pc_summary"]}</h3>'
            f'<ul class="pcfg-list" id="pcList"></ul>'
            f'<p class="pcfg-applied" id="pcApplied" hidden></p>'
            f'<p class="pcfg-remind" id="pcRemind" role="status" hidden></p>'
            f'<div class="pcfg-total-row"><span class="pcfg-total-label" data-i18n="pc_total">{t["pc_total"]}</span><strong class="pcfg-total" id="pcTotal" aria-live="polite">₾{d["platform"]["price"]:,}</strong></div>'
            f'<div class="pcfg-actions"><button class="button button-red" id="pcWa" type="button"><span data-i18n="pc_send">{t["pc_send"]}</span></button>'
            f'<button class="button button-line" id="pcCart" type="button"><span data-i18n="pc_cart">{t["pc_cart"]}</span></button></div></aside></div>'
            f'<div class="pcfg-bar" id="pcBar" aria-hidden="true"><div class="pcfg-bar-sum"><span class="pcfg-bar-label" data-i18n="pc_total">{t["pc_total"]}</span>'
            f'<strong id="pcBarTotal">₾{d["platform"]["price"]:,}</strong></div><button class="button button-red" type="button" id="pcBarSend" tabindex="-1"><span data-i18n="pc_send">{t["pc_send"]}</span></button></div>'
            f'</div></section>')
