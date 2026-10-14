"""Build the site search index: dist/assets/search/<lang>.json (pages + products with prices).
Runs after build-pages.py (it reads the generated pages). The header search box loads the file on first use."""
import csv, json, re, sys
from pathlib import Path
from lxml import html

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
sys.path.insert(0, str(ROOT / 'scripts'))
import product_pages

content = (DIST / 'assets/js/content.js').read_text(encoding='utf-8')
T = json.loads(content.split('=', 1)[1].strip().removesuffix(';'))
SKIP = {'404.html', 'payment.html', 'account.html', 'terms.html'}
# Words people type that the (English) product names do not contain.
SYN = {
    'power': {'ka': 'ბატარეა ბატარეები აკუმულატორი დამტენი დატენვა გენერატორი ენერგია', 'en': 'battery batteries charger charging generator power',
              'ru': 'батарея батареи аккумулятор зарядка зарядное генератор'},
    'spray': {'ka': 'შეწამვლა შეწამვლა საქშენი ტუმბო ავზი გაფანტვა', 'en': 'spray spraying nozzle pump tank spreading', 'ru': 'опрыскивание форсунка насос бак разбрасыватель'},
    'control': {'ka': 'პულტი მართვა RTK ანტენა', 'en': 'remote controller RTK antenna', 'ru': 'пульт управление RTK антенна'},
    'acc': {'ka': 'აქსესუარი', 'en': 'accessory accessories', 'ru': 'аксессуар'},
    'spare': {'ka': 'ნაწილი სათადარიგო ძრავა პროპელერი', 'en': 'part spare motor propeller', 'ru': 'запчасть мотор пропеллер'},
    'kit': {'ka': 'დრონი დრონები კომპლექტი კომპლექტაცია პაკეტი სასოფლო-სამეურნეო დრონი შესაწამლი დრონი შეწამვლა დრონით შეწამვლა შეწამვლა აგროდრონი აგრო დრონი გრანულების გაფანტვა სასუქის გაფანტვა ტვირთის გადატანა ფასი',
            'en': 'drone kit package agricultural drone ag drone spraying drone crop spraying sprayer spreading granules cargo price',
            'ru': 'дрон комплект пакет сельскохозяйственный дрон агродрон сельхоз дрон опрыскивание разбрасывание гранул удобрения перевозка груза цена'},
    'drone': {'ka': 'დრონი დრონები სასოფლო-სამეურნეო დრონი შესაწამლი დრონი აგროდრონი აგრო დრონი შეწამვლა ფასი',
              'en': 'drone agricultural drone ag drone spraying drone price', 'ru': 'дрон сельскохозяйственный дрон агродрон опрыскивание цена'},
}
# Shown instead of a price for quote-only parts and previous models (never ₾0).
DICT_Q = {'ka': 'ფასი მოთხოვნით', 'en': 'Price on request', 'ru': 'Цена по запросу'}
CAT = {'power': 'cat_power', 'spray': 'cat_spray', 'control': 'cat_control', 'acc': 'cat_acc', 'spare': 'cat_spare', 'kit': 'packages_title', 'drone': 'cat_drone'}


def page_url(rel):
    p = '/' + rel.as_posix()
    p = p[:-len('index.html')] if p.endswith('index.html') else p[:-5]
    return p


def ka_labels():
    """Georgian texts live in the HTML; read the category names from the shop page."""
    doc = html.fromstring((DIST / 'shop.html').read_text(encoding='utf-8'))
    out = {}
    for key in set(CAT.values()):
        el = doc.xpath(f'//*[@data-i18n="{key}"]')
        if el:
            out[key] = el[0].text_content().strip()
    return out


KA = ka_labels()
rows = list(csv.DictReader(open(ROOT / 'scripts/catalog.csv', encoding='utf-8')))
shop_doc = html.fromstring((DIST / 'shop.html').read_text(encoding='utf-8'))
prices = {b.get('data-sku'): int(b.get('data-price')) for b in shop_doc.xpath('//button[@data-sku][@data-price]')}

out_dir = DIST / 'assets/search'
out_dir.mkdir(parents=True, exist_ok=True)
for lang in ('ka', 'en', 'ru'):
    base = DIST if lang == 'ka' else DIST / lang
    pages = []
    for f in sorted(base.glob('*.html')):
        if f.name in SKIP:
            continue
        doc = html.fromstring(f.read_text(encoding='utf-8'))
        for bad in doc.xpath('//header|//footer|//script|//style|//dialog|//*[@hidden]|//nav'):
            bad.getparent().remove(bad)
        main = doc.xpath('//main') or [doc]
        h1 = ' '.join((main[0].xpath('.//h1') or [None])[0].text_content().split()) if main[0].xpath('.//h1') else ''
        desc = (doc.xpath('//meta[@name="description"]/@content') or [''])[0]
        text = ' '.join(' '.join(e.text_content().split()) for e in main[0].xpath('.//h2|.//h3|.//p|.//summary|.//dt|.//li'))
        rel = f.relative_to(DIST)
        entry = {'u': page_url(rel), 't': h1 or f.stem, 'd': desc[:200], 'x': text[:1500]}
        if f.name in ('index.html', 'p150-max.html'):  # farmer search words (not shown on the page)
            entry['k'] = (doc.xpath('//meta[@name="keywords"]/@content') or [''])[0]
        pages.append(entry)
    products = []
    prefix = '' if lang == 'ka' else '/' + lang
    for r in rows:
        g = r['group']
        key = CAT[g]
        cat = KA.get(key, '') if lang == 'ka' else T[lang].get(key, '')
        url = f'{prefix}/shop#kits' if g == 'kit' else (f'{prefix}{product_pages.url(r["sku"])}' if product_pages.url(r['sku']) else f'{prefix}/shop?q={r["sku"]}#parts')
        local = (r.get('name_' + lang) or '').strip() if lang != 'en' else ''
        products.append({'n': local or r['name'], 'o': r['name'] if local else '', 's': r['sku'], 'p': prices.get(r['sku'], 0), 'q': '' if prices.get(r['sku']) else DICT_Q[lang], 'c': cat,
                         'k': SYN[g][lang] + ' ' + r['name'], 'u': url})
    (out_dir / f'{lang}.json').write_text(json.dumps({'pages': pages, 'products': products}, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    print(f'search {lang}: {len(pages)} pages, {len(products)} products')
