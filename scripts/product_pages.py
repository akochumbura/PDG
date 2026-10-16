"""Product pages for the energy system (owner, 14 Oct 2026: batteries and generators need their own page with specs).
Only products whose specs are on the official XAG P150 MAX spec page (scripts/p150_specs.py: 'specs' group, 'block' index) get a page;
do not add a page with unverified specs. Used by build-shop.py (links on cards) and build-products.py (the pages).
"""

PAGES = [
    {'sku': '09-017-00073', 'slug': 'b141050-battery', 'block': 0,
     'title': ('XAG B141050 აკუმულატორი — ფასი და მახასიათებლები', 'XAG B141050 battery — price and specifications', 'Аккумулятор XAG B141050 — цена и характеристики'),
     'intro': ('XAG P150 MAX-ის ჭკვიანი სწრაფად დასატენი აკუმულატორი. ოფიციალური მახასიათებლები, ფასი და შეკვეთა.',
               'Smart SuperCharge battery for the XAG P150 MAX. Official specifications, price and ordering.',
               'Умный аккумулятор SuperCharge для XAG P150 MAX. Официальные характеристики, цена и заказ.')},
    {'sku': '09-017-00069', 'slug': 'cm13600s-charger', 'block': 1,
     'title': ('XAG CM13600S დამტენი — ფასი და მახასიათებლები', 'XAG CM13600S charger — price and specifications', 'Зарядное устройство XAG CM13600S — цена и характеристики'),
     'intro': ('XAG P150 MAX-ის აკუმულატორების დამტენი. ოფიციალური მახასიათებლები, ფასი და შეკვეთა.',
               'Charger for XAG P150 MAX batteries. Official specifications, price and ordering.',
               'Зарядное устройство для аккумуляторов XAG P150 MAX. Официальные характеристики, цена и заказ.')},
    {'sku': '09-017-00109', 'slug': 'gc4000-plus-generator', 'block': 2,
     'title': ('XAG GC4000+ დამუხტვის სადგური (გენერატორი) — ფასი და მახასიათებლები', 'XAG GC4000+ charging station (generator) — price and specifications',
               'Зарядная станция XAG GC4000+ (генератор) — цена и характеристики'),
     'intro': ('XAG P150 MAX-ის აკუმულატორების საველე დამუხტვის სადგური (გენერატორი). ოფიციალური მახასიათებლები, ფასი და შეკვეთა.',
               'Field charging station (generator) for XAG P150 MAX batteries. Official specifications, price and ordering.',
               'Полевая зарядная станция (генератор) для аккумуляторов XAG P150 MAX. Официальные характеристики, цена и заказ.')},
    {'sku': '09-017-00065', 'slug': 'battery-cooling-tank', 'block': 3,
     'title': ('XAG აკუმულატორის გამაგრილებელი ავზი — ფასი და მახასიათებლები', 'XAG battery cooling tank — price and specifications', 'Охлаждающий бак XAG для аккумуляторов — цена и характеристики'),
     'intro': ('XAG P150 MAX-ის აკუმულატორების წყლით გამაგრილებელი ავზი: დატენვის წინ აგრილებს აკუმულატორს. ოფიციალური მახასიათებლები, ფასი და შეკვეთა.',
               'Water cooling tank for XAG P150 MAX batteries: cools the battery before charging. Official specifications, price and ordering.',
               'Водяной охлаждающий бак для аккумуляторов XAG P150 MAX: охлаждает аккумулятор перед зарядкой. Официальные характеристики, цена и заказ.')},
    {'sku': '05-002-02725', 'slug': 'src5-remote-controller', 'specs': 'control', 'block': 1,
     'title': ('XAG SRC5 ჭკვიანი მართვის პულტი — ფასი და მახასიათებლები', 'XAG SRC5 smart remote controller — price and specifications', 'Умный пульт XAG SRC5 — цена и характеристики'),
     'intro': ('XAG P150 MAX-ის ჭკვიანი მართვის პულტი ეკრანით. ოფიციალური მახასიათებლები, ფასი და შეკვეთა.',
               'Smart remote controller with screen for the XAG P150 MAX. Official specifications, price and ordering.',
               'Умный пульт управления с экраном для XAG P150 MAX. Официальные характеристики, цена и заказ.')},
    {'sku': '09-016-00083', 'slug': 'xrtk7-rtk-station', 'specs': 'control', 'block': 2,
     'title': ('XAG XRTK7 მობილური RTK სადგური — ფასი და მახასიათებლები', 'XAG XRTK7 mobile RTK station — price and specifications', 'Мобильная RTK-станция XAG XRTK7 — цена и характеристики'),
     'intro': ('მობილური RTK სადგური სანტიმეტრული სიზუსტის ფრენისა და ნაკვეთის აზომვისთვის. ოფიციალური მახასიათებლები, ფასი და შეკვეთა.',
               'Mobile RTK station for centimetre-accurate flight and field mapping. Official specifications, price and ordering.',
               'Мобильная RTK-станция для полётов и съёмки участков с сантиметровой точностью. Официальные характеристики, цена и заказ.')},
]
BY_SKU = {p['sku']: p for p in PAGES}

# P150 MAX package pages (owner, 14 Oct 2026): first picture = the package's own combo picture (exactly its contents),
# then the P150 MAX gallery (dist/assets/img/packages/p150-max-1..9.webp). Contents = catalog columns (see build-shop CONTENTS).
KITS = {'PDG-P150MAX-STARTER': 'p150-max-starter', 'PDG-P150MAX-PRO': 'p150-max-pro', 'PDG-P150MAX-BUSINESS': 'p150-max-business'}
GALLERY = [  # (file, ka alt, en alt, ru alt)
    ('p150-max-1.webp', 'XAG P150 MAX — სამი მეოთხედის ხედი', 'XAG P150 MAX — three-quarter view', 'XAG P150 MAX — вид в три четверти'),
    ('p150-max-2.webp', 'XAG P150 MAX — გვერდითი ხედი', 'XAG P150 MAX — side view', 'XAG P150 MAX — вид сбоку'),
    ('p150-max-3.webp', 'XAG RevoCast — გრანულების გამფანტველი სისტემა (ცალკე)', 'XAG RevoCast granule spreading system (sold separately)', 'Система разбрасывания гранул XAG RevoCast (отдельно)'),
    ('p150-max-4.webp', 'XAG SRC5 ჭკვიანი მართვის პულტი', 'XAG SRC5 smart remote controller', 'Умный пульт управления XAG SRC5'),
    ('p150-max-5.webp', 'XAG B141050 ჭკვიანი აკუმულატორი', 'XAG B141050 smart battery', 'Умный аккумулятор XAG B141050'),
    ('p150-max-6.webp', 'XAG P150 MAX გრანულების გაფანტვისას', 'XAG P150 MAX spreading granules', 'XAG P150 MAX при разбрасывании гранул'),
    ('p150-max-7.webp', 'XAG P150 MAX ტვირთის გადატანისას', 'XAG P150 MAX carrying cargo', 'XAG P150 MAX при перевозке груза'),
    ('p150-max-8.webp', 'XAG P150 MAX შეწამვლისას', 'XAG P150 MAX spraying', 'XAG P150 MAX при опрыскивании'),
    ('p150-max-9.webp', 'XAG P150 MAX ბაღის შეწამვლისას', 'XAG P150 MAX spraying an orchard', 'XAG P150 MAX при опрыскивании сада'),
]


# Standalone P150 MAX platform (owner, 16 Oct 2026): own page with the configurator (scripts/configurator.py).
PLATFORM = '09-007-00188'
PLATFORM_GALLERY = [  # P150 MAX gallery pictures that show only what the platform includes (no remote/battery/spreader pictures)
    ('p150-max-1.webp', 'pd_g1'), ('p150-max-2.webp', 'pd_g2'), ('p150-max-8.webp', 'pd_g8'), ('p150-max-9.webp', 'pd_g9')]

# Previous-generation models (owner photos, 15 Oct 2026): own page with gallery, no price, consultation instead of a cart.
# Pictures: dist/assets/img/models/<prefix>-N.webp (+ -t thumbs), made by scripts/tools/model-pictures.py.
LEGACY = {
    'XAG-P100PRO': {'slug': 'xag-p100-pro', 'prefix': 'p100pro', 'short': 'XAG P100 Pro', 'pics': [
        ('XAG P100 Pro — სტუდიური ფოტო', 'XAG P100 Pro — studio picture', 'XAG P100 Pro — студийное фото'),
        ('XAG P100 Pro — დრონი და აღჭურვილობა', 'XAG P100 Pro — drone and equipment', 'XAG P100 Pro — дрон и оборудование')]},
    'XAG-P100': {'slug': 'xag-p100', 'prefix': 'p100', 'short': 'XAG P100', 'pics': [
        ('XAG P100 ფრენისას მინდორზე', 'XAG P100 flying over a field', 'XAG P100 в полёте над полем'),
        ('XAG P100 გამოფენაზე', 'XAG P100 at an exhibition', 'XAG P100 на выставке')]},
    'XAG-V40': {'slug': 'xag-v40', 'prefix': 'v40', 'short': 'XAG V40', 'pics': [
        ('XAG V40 მინდორზე', 'XAG V40 on the field', 'XAG V40 в поле'),
        ('XAG V40 ბაღის შეწამვლისას', 'XAG V40 spraying an orchard', 'XAG V40 при опрыскивании сада')]},
}


def url(sku):
    """Clean URL of the product or package page (Cloudflare Pages serves /x.html as /x), or None."""
    if sku == PLATFORM:
        return '/p150-max-platform'
    if sku in LEGACY:
        return '/' + LEGACY[sku]['slug']
    if sku in KITS:
        return '/' + KITS[sku]
    p = BY_SKU.get(sku)
    return f"/{p['slug']}" if p else None
