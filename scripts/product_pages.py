"""Product pages for the energy system (owner, 14 Oct 2026: batteries and generators need their own page with specs).
Only products whose specs are on the official XAG P150 MAX spec page (scripts/p150_specs.py, 'power' group) get a page;
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
]
BY_SKU = {p['sku']: p for p in PAGES}


def url(sku):
    """Clean URL of the product page (Cloudflare Pages serves /x.html as /x), or None."""
    p = BY_SKU.get(sku)
    return f"/{p['slug']}" if p else None
