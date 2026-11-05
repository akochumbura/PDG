"""XAG P150 MAX platform configurator (owner brief, 16 Oct 2026).

One builder, used on the standalone platform page (/p150-max-platform, build-products.py). Every price comes from scripts/catalog.csv (the owner's price list), every
stock limit from scripts/stock.csv, the package contents from the catalog kit rows: listings, cart, worker and configurator
read the same numbers. Pricing rule (owner brief, 4 Nov 2026, replaces the automatic rule of 16 Oct): a package price applies only after the customer
picks a package or accepts the offer; otherwise items are priced one by one. When the selection holds every component of a package
and that is cheaper, one inline offer shows the package total and the saving. Quantities are never changed by an offer.
Owner, 4 Nov 2026: no standalone "platform only" offer - the drone is the base component of every configuration (its price is used
in item-by-item totals only); new visits start with Starter. The configurator is on /shop (#configurator); /p150-max-platform forwards there.
Georgian text is here (data-i18n keys); en/ru are written to content.js by build-shop.py (TEXT).
"""
import csv, html, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLATFORM = '09-007-00188'
PAGE = '/shop'  # owner, 4 Nov 2026: one configurator, on the shop (the old platform address forwards here)
# (catalog column used by the package rows or own key, sku, i18n key, Georgian label, optional?)
ENERGY = [('remotes', '05-002-02725', 'pc_remote', 'მართვის პულტი SRC5', False),
          ('batteries', '09-017-00073', 'pc_battery', 'აკუმულატორი B141050', False),
          ('chargers', '09-017-00069', 'pc_charger', 'დამტენი CM13600S', False),
          ('towers', '09-017-00065', 'pc_tower', 'აკუმულატორის გამაგრილებელი ავზი', False),
          ('rtk', '09-016-00083', 'pc_rtk', 'მობილური RTK სადგური XRTK7', True)]  # 5 Nov 2026: with the package contents (Plus/Pro/Business include it)
EXTRA = [('generators', '09-017-00109', 'pc_generator', 'დამუხტვის სადგური (გენერატორი) GC4000+', True),
         ('spreader', '09-023-00145', 'pc_revocast', 'გრანულების გამფანტველი RevoCast\u00a05', True),
         ('sling', '05-002-02682', 'pc_revosling', 'ტვირთის საკიდი სისტემა RevoSling (შასით)', True),
         ('nozzle4', '05-002-02640', 'pc_nozzle4', '4-გამფრქვევიანი განახლების კომპლექტი (P150 MAX)', True),
         ('led', '09-027-00003', 'pc_led', 'LED ფარი 90 ვტ', True)]  # owner, 18 Oct 2026: LED lights as an option for every setup
KIT_COLS = ['remotes', 'batteries', 'chargers', 'towers', 'rtk', 'generators']
# Owner, 16 Oct 2026: the same equipment bought one by one. Checked against the catalog at every build.
OWNER_EQUIVALENT = {'PDG-P150MAX-STARTER': 79590, 'PDG-P150MAX-PLUS': 90587, 'PDG-P150MAX-PRO': 95587, 'PDG-P150MAX-BUSINESS': 114583}

TEXT = {  # key: (ka, en, ru)
    'pc_remote': ('მართვის პულტი SRC5', 'SRC5 remote controller', 'Пульт управления SRC5'),
    'pc_battery': ('აკუმულატორი B141050', 'B141050 battery', 'Аккумулятор B141050'),
    'pc_charger': ('დამტენი CM13600S', 'CM13600S charger', 'Зарядное устройство CM13600S'),
    'pc_tower': ('აკუმულატორის გამაგრილებელი ავზი', 'Battery cooling tank', 'Охлаждающий бак для аккумуляторов'),
    'pc_generator': ('დამუხტვის სადგური (გენერატორი) GC4000+', 'GC4000+ charging station (generator)', 'Зарядная станция (генератор) GC4000+'),
    'pc_rtk': ('მობილური RTK სადგური XRTK7', 'XRTK7 mobile RTK station', 'Мобильная RTK-станция XRTK7'),
    'pc_revocast': ('გრანულების გამფანტველი RevoCast\u00a05', 'RevoCast\u00a05 granule spreader', 'Разбрасыватель гранул RevoCast\u00a05'),
    'pc_revosling': ('ტვირთის საკიდი სისტემა RevoSling (შასით)', 'RevoSling cargo system (with landing gear)', 'Грузовая система RevoSling (с шасси)'),
    'pc_nozzle4': ('4-გამფრქვევიანი განახლების კომპლექტი (P150 MAX)', '4-Nozzle Upgrade Kit (P150 MAX)', 'Комплект модернизации на 4 форсунки (P150 MAX)'),
    'pc_led': ('LED ფარი 90 ვტ', '90 W LED headlight', 'Светодиодная фара 90 Вт'),
    'pc_title': ('კონფიგურატორი', 'Configurator', 'Конфигуратор'),
    'pc_intro': ('აირჩიეთ კომპლექტი და საჭიროებისამებრ შეცვალეთ რაოდენობა.', 'Pick a package and change the quantities if you need to.',
                 'Выберите комплект и при необходимости измените количество.'),
    'pc_presets': ('სწრაფი არჩევანი', 'Quick choice', 'Быстрый выбор'),
    'pc_platform': ('XAG P150 MAX პლატფორმა (RevoSpray\u00a05)', 'XAG P150 MAX platform (RevoSpray\u00a05)', 'Платформа XAG P150 MAX (RevoSpray\u00a05)'),
    'pc_energy': ('მართვა და ენერგია', 'Control and power', 'Управление и питание'),
    'pc_extra': ('დამატებითი აღჭურვილობა', 'Additional equipment', 'Дополнительное оборудование'),
    'pc_extra_sel': ('არჩეულია {n}', '{n} selected', 'выбрано: {n}'),
    'pkc_save': ('დაზოგავთ', 'You save', 'Экономия'),
    'pkc_bat': ('აკუმ.', 'batt.', 'акк.'),
    'pkc_chg': ('დამტ.', 'charg.', 'заряд.'),
    'pkc_incl': ('ყველა კომპლექტში: დრონი RevoSpray 5-ით, SRC5 მართვის პულტი და 2 გამაგრილებელი ავზი. გენერატორი იყიდება ცალკე.',
                 'Every package: the drone with RevoSpray 5, the SRC5 remote controller and 2 cooling tanks. The generator is sold separately.',
                 'В каждом комплекте: дрон с RevoSpray 5, пульт SRC5 и 2 охлаждающих бака. Генератор продаётся отдельно.'),
    'pkc_specs': ('P150 MAX-ის მახასიათებლები', 'P150 MAX specifications', 'Характеристики P150 MAX'),
    'pkc_contents': ('შემადგენლობა', 'Contents', 'Состав'),
    'pkc_close': ('დახურვა', 'Close', 'Закрыть'),
    # Premium buying page (owner, 5 Nov 2026: "work from the Apple site")
    'pb_eyebrow': ('სასოფლო-სამეურნეო დრონი', 'Agricultural drone', 'Сельскохозяйственный дрон'),
    'pb_title': ('XAG P150 MAX-ის ყიდვა', 'Buy XAG P150 MAX', 'Купить XAG P150 MAX'),
    'pb_step1': ('კომპლექტი.', 'Package.', 'Комплект.'),
    'pb_step1_q': ('რომელი გჭირდებათ?', 'Which one is right for you?', 'Какой вам подходит?'),
    'pb_step2': ('კომპლექტში შედის.', 'What is included.', 'Что входит.'),
    'pb_step2_q': ('რაოდენობა შეგიძლიათ შეცვალოთ.', 'You can change the quantities.', 'Количество можно изменить.'),
    'pb_step3': ('დამატებითი აღჭურვილობა.', 'Accessories.', 'Дополнительное оборудование.'),
    'pb_step3_q': ('გენერატორი, გაფანტვა, ტვირთი და სხვა.', 'Generator, spreading, cargo and more.', 'Генератор, разбрасывание, груз и другое.'),
    'pb_add': ('დამატება', 'Add', 'Добавить'),
    'pb_photo': ('ფოტოზე — არჩეული კომპლექტის შემადგენლობა.', 'Pictured: the contents of the selected package.', 'На фото — состав выбранного комплекта.'),
    'pb_save': ('₾{n}-ით ნაკლები, ვიდრე ცალ-ცალკე ყიდვისას.', '₾{n} less than buying the items separately.', 'На ₾{n} дешевле, чем по отдельности.'),
    'pb_t1': ('XAG-ის ოფიციალური გარანტია — 1 წელი', 'Official XAG warranty — 1 year', 'Официальная гарантия XAG — 1 год'),
    'pb_t2': ('სერვისი თბილისში, წინასწარი შეთანხმებით', 'Service in Tbilisi, by appointment', 'Сервис в Тбилиси, по записи'),
    'pb_t3': ('ოპერატორის სწავლება PDG აკადემიაში', 'Operator training at PDG Academy', 'Обучение операторов в Академии PDG'),
    'pb_t4': ('მიწოდება საქართველოში — ₾100-დან უფასოდ', 'Delivery in Georgia — free from ₾100', 'Доставка по Грузии — бесплатно от ₾100'),
    'pb_specs': ('ყველა მახასიათებელი', 'All specifications', 'Все характеристики'),
    'pb_summary': ('თქვენი კომპლექტი', 'Your configuration', 'Ваша конфигурация'),
    'pc_more_count': ('არჩეულია: {n}', 'selected: {n}', 'выбрано: {n}'),
    'pc_optional': ('არასავალდებულო', 'optional', 'по желанию'),
    'pc_each': ('/ ცალი', '/ each', '/ шт.'),
    'pc_summary': ('თქვენი კონფიგურაცია', 'Your configuration', 'Ваша конфигурация'),
    'pc_total': ('ჯამი, დღგ-ს ჩათვლით', 'Total incl. VAT', 'Итого с НДС'),
    'pc_send': ('კონფიგურაციის გაგზავნა', 'Send configuration', 'Отправить конфигурацию'),
    'pc_cart': ('კალათაში დამატება', 'Add to cart', 'В корзину'),
    'pc_applied': ('გამოყენებულია {name} კომპლექტის ფასი', '{name} package price applied', 'Применена цена комплекта {name}'),
    # owner brief, 4 Nov 2026 (buying refinement): package prices apply only after the customer chooses or accepts a package
    'pc_offer': ('{name} კომპლექტით ჯამი იქნება {total} — დაზოგავთ {saving}.', 'With the {name} package the total is {total}, you save {saving}.',
                 'С комплектом {name} итого {total}, экономия {saving}.'),
    'pc_offer_extras': ('დანარჩენი ნივთები ცალკე ფასით რჩება.', 'The other items stay at their own prices.', 'Остальное остается по отдельным ценам.'),
    'pc_offer_btn': ('კომპლექტის არჩევა', 'Choose the package', 'Выбрать комплект'),
    'pc_broken': ('{name} კომპლექტის შემადგენლობა აღარ არის სრული, ამიტომ ფასი ცალ-ცალკეა დათვლილი.', 'The {name} package is no longer complete, so items are priced individually.',
                  'Комплект {name} больше не полный, поэтому цена рассчитана поштучно.'),
    'pc_send_short': ('გაგზავნა', 'Send', 'Отправить'),
    'pc_send_aria': ('კონფიგურაციის გაგზავნა WhatsApp-ით', 'Send the configuration by WhatsApp', 'Отправить конфигурацию в WhatsApp'),
    'pc_vat_short': ('დღგ-ს ჩათვლით', 'incl. VAT', 'с НДС'),
    'pc_jump_cfg': ('კონფიგურატორი', 'Configurator', 'Конфигуратор'),
    'pc_jump_pkgs': ('მზა კომპლექტები', 'Ready packages', 'Готовые комплекты'),
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


def _row(key, it, ka, opt, add=False):
    lab = it['label']
    # add=True (accessories): an "add" button until the item is chosen, then the quantity stepper (Apple-style accessory cards)
    plus = f'<button type="button" class="pcfg-add" data-add-key="{key}"><span data-i18n="pb_add">{TEXT["pb_add"][0]}</span></button>' if add else ''
    return (f'<div class="pcfg-row{" pcfg-acc" if add else ""}" data-key="{key}">{_thumb(it["sku"])}<div class="pcfg-name"><span class="pcfg-label" data-i18n="{lab}">{html.escape(ka)}</span>'
            f'<span class="pcfg-unit">₾{it["price"]:,} <span data-i18n="pc_each">/ ცალი</span></span></div>{plus}'
            f'<div class="qty-stepper pcfg-stepper"><button type="button" class="qty-btn" data-step="-1" aria-label="რაოდენობის შემცირება" data-i18n-aria="qty_less">−</button>'
            f'<input class="qty-input" type="number" inputmode="numeric" min="0" max="{it["max"]}" step="1" value="0" aria-label="{html.escape(ka, quote=True)}" data-i18n-aria="{lab}">'
            f'<button type="button" class="qty-btn" data-step="1" aria-label="რაოდენობის გაზრდა" data-i18n-aria="qty_more">+</button></div></div>')


def block(heading='h1'):
    """The buying page (owner, 5 Nov 2026, "work from the Apple site"): a large picture of the chosen package on the left
    (sticky on desktop), the choices on the right in three calm steps, then the summary with the price and verified trust facts.
    The pricing logic, ids and data are the same as before (shop.js)."""
    d = data()
    t = {k: v[0] for k, v in TEXT.items()}
    lst = {k: (ka, opt) for k, s_, l_, ka, opt in ENERGY + EXTRA}
    energy = ''.join(_row(k, d['items'][k], *lst[k]) for k, *_ in ENERGY)
    extra = ''.join(_row(k, d['items'][k], *lst[k], add=True) for k, *_ in EXTRA)
    def keys(p):
        q = p['q']
        bits = [f'{q.get("batteries", 0)} <span data-i18n="kk_bat">აკუმულატორი</span>', f'{q.get("chargers", 0)} <span data-i18n="kk_chg">დამტენი</span>']
        if q.get('rtk'):
            bits.append('RTK')
        return ' · '.join(bits)
    rows = ''.join(
        f'<button type="button" class="pcfg-preset pkr" data-preset="{p["sku"]}" data-img="/assets/img/products/{p["sku"]}.webp" aria-pressed="false">'
        f'<span class="pkr-main"><span class="pkr-name">{html.escape(p["short"])}</span><span class="pkr-keys">{keys(p)}</span></span>'
        f'<span class="pkr-price pcfg-preset-price">₾{p["price"]:,}</span></button>' for p in d['packages'])
    cfg = html.escape(json.dumps(d, ensure_ascii=False), quote=True)
    first = d['packages'][0]
    trust = ''.join(f'<li data-i18n="{k}">{t[k]}</li>' for k in ('pb_t1', 'pb_t2', 'pb_t3', 'pb_t4'))
    return (f'<section class="buy" id="configurator" aria-labelledby="buyTitle"><div class="container buy-grid">'
            f'<div class="buy-pick"><div class="buy-media"><figure class="buy-figure"><img id="buyImg" src="/assets/img/products/{first["sku"]}.webp" width="1200" height="900" '
            f'alt="{html.escape(first["name"], quote=True)}" fetchpriority="high" decoding="async"></figure>'
            f'<p class="buy-caption" data-i18n="pb_photo">{t["pb_photo"]}</p></div>'
            f'<div class="buy-head">'
            f'<p class="buy-eyebrow" data-i18n="pb_eyebrow">{t["pb_eyebrow"]}</p><{heading} class="buy-title" id="buyTitle" data-i18n="pb_title">{t["pb_title"]}</{heading}>'
            f'<a class="buy-specs" href="/p150-max#specifications" data-local><span data-i18n="pb_specs">{t["pb_specs"]}</span> <span aria-hidden="true">›</span></a>'
            f'<div class="buy-step pcfg-presets" role="group" aria-labelledby="pbStep1"><h2 class="buy-step-h" id="pbStep1"><span data-i18n="pb_step1">{t["pb_step1"]}</span> '
            f'<span class="buy-step-q" data-i18n="pb_step1_q">{t["pb_step1_q"]}</span></h2><div class="pkr-list">{rows}</div></div></div></div>'
            f'<div class="buy-panel"><div class="pcfg" id="platformConfig" data-config="{cfg}">'
            f'<div class="pcfg-options">'
            f'<div class="buy-step"><h2 class="buy-step-h"><span data-i18n="pb_step2">{t["pb_step2"]}</span> <span class="buy-step-q" data-i18n="pb_step2_q">{t["pb_step2_q"]}</span></h2>'
            f'<div class="buy-tiles"><div class="pcfg-row pcfg-fixed">{_thumb(d["platform"]["sku"])}<div class="pcfg-name"><span class="pcfg-label" data-i18n="pc_platform">{t["pc_platform"]}</span>'
            f'<span class="pcfg-unit">₾{d["platform"]["price"]:,}</span></div><output class="pcfg-fixed-qty">1</output></div>{energy}</div></div>'
            f'<details class="buy-step pcfg-extra" id="pcExtra"><summary class="buy-step-h"><span><span data-i18n="pb_step3">{t["pb_step3"]}</span> '
            f'<span class="buy-step-q" data-i18n="pb_step3_q">{t["pb_step3_q"]}</span></span><span class="pcfg-extra-count" id="pcExtraCount" hidden></span></summary>'
            f'<div class="buy-acc">{extra}</div></details>'
            f'</div>'
            f'<aside class="pcfg-summary buy-summary" id="pcSummary" aria-labelledby="pcSumTitle"><h2 class="buy-step-h" id="pcSumTitle" data-i18n="pb_summary">{t["pb_summary"]}</h2>'
            f'<div class="pcfg-total-row"><strong class="pcfg-total" id="pcTotal" aria-live="polite">₾{first["price"]:,}</strong>'
            f'<span class="pcfg-total-label" data-i18n="pc_vat_short">{t["pc_vat_short"]}</span></div>'
            f'<p class="buy-save" id="pcSave" hidden></p>'
            f'<p class="pcfg-applied" id="pcApplied" hidden></p>'
            f'<div class="pcfg-offer" id="pcOffer" hidden><p id="pcOfferText"></p><button class="button button-line pcfg-offer-btn" id="pcOfferBtn" type="button" data-i18n="pc_offer_btn">{t["pc_offer_btn"]}</button></div>'
            f'<p class="pcfg-remind" id="pcRemind" role="status" hidden></p>'
            f'<div class="pcfg-actions"><button class="button button-red" id="pcWa" type="button"><span data-i18n="pc_send">{t["pc_send"]}</span></button>'
            f'<button class="button button-line" id="pcCart" type="button"><span data-i18n="pc_cart">{t["pc_cart"]}</span></button></div>'
            f'<ul class="buy-trust">{trust}</ul>'
            f'<details class="buy-lines"><summary data-i18n="pkc_contents">{t["pkc_contents"]}</summary><ul class="pcfg-list" id="pcList"></ul></details>'
            f'</aside></div></div></div>'
            f'<div class="pcfg-bar" id="pcBar" aria-hidden="true"><div class="pcfg-bar-sum"><strong id="pcBarTotal">₾{first["price"]:,}</strong>'
            f'<span class="pcfg-bar-label" data-i18n="pc_vat_short">{t["pc_vat_short"]}</span></div>'
            f'<button class="button button-red" type="button" id="pcBarSend" tabindex="-1" aria-label="{t["pc_send_aria"]}" data-i18n-aria="pc_send_aria"><span data-i18n="pc_send_short">{t["pc_send_short"]}</span></button></div>'
            f'</section>')
