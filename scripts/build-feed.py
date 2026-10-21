"""Google Merchant Center product feed: dist/merchant-feed.xml (RSS 2.0 + g: namespace).
Source = the Product/Offer structured data already on dist/shop.html, so the feed lists exactly the
items the site itself shows as in stock, priced and with their OWN photo (no XAG-logo placeholders).
Feed language: English (titles are the original XAG names). Country: Georgia, currency GEL."""
import json, re
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / 'dist'
SITE = 'https://premium-drones.ge'


def products(html):
    out = []

    def walk(x):
        if isinstance(x, dict):
            if x.get('@type') == 'Product' and isinstance(x.get('offers'), dict):
                out.append(x)
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        walk(json.loads(block))
    return out


def en_desc(p):
    sku = p.get('sku', '')
    if sku.startswith('PDG-P150MAX'):
        return 'XAG P150 MAX agricultural drone package for field mapping, spraying, granule spreading and cargo transport. Official XAG dealer in Georgia, local stock and service.'
    if p.get('category') == 'Agricultural drone':
        return 'XAG P150 MAX agricultural drone. Official XAG dealer in Georgia, local stock and service.'
    return f'Original XAG part for the XAG P150 MAX agricultural drone. Manufacturer code: {sku}. In stock in Georgia.'


def item(p):
    o = p['offers']
    price = float(o['price'])
    sku = p.get('sku', '')
    ship = 0 if price >= 100 else 30
    link = o.get('url') or SITE + '/shop'
    rows = [
        ('g:id', sku), ('g:title', p['name'][:150]), ('g:description', en_desc(p)),
        ('g:link', link), ('g:image_link', p['image'] if isinstance(p['image'], str) else p['image'][0]),
        ('g:availability', 'in_stock'), ('g:condition', 'new'),
        ('g:price', f'{price:.2f} GEL'), ('g:brand', 'XAG'),
    ]
    if sku.startswith('PDG-'):
        rows.append(('g:identifier_exists', 'no'))
    else:
        rows.append(('g:mpn', sku))
    body = ''.join(f'<{k}>{escape(str(v))}</{k}>' for k, v in rows)
    body += f'<g:shipping><g:country>GE</g:country><g:price>{ship:.2f} GEL</g:price></g:shipping>'
    return f'<item>{body}</item>'


def main():
    seen, items = set(), []
    for page in ('shop.html', 'p150-max.html'):
        f = D / page
        if not f.exists():
            continue
        for p in products(f.read_text(encoding='utf-8')):
            sku = p.get('sku')
            if not sku or sku in seen or not p.get('image'):
                continue
            seen.add(sku)
            items.append(item(p))
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:g="http://base.google.com/ns/1.0"><channel>'
           '<title>Premium Drones Georgia</title><link>https://premium-drones.ge/</link>'
           '<description>XAG P150 MAX agricultural drones, packages and original parts in Georgia</description>'
           + ''.join(items) + '</channel></rss>\n')
    (D / 'merchant-feed.xml').write_text(xml, encoding='utf-8')
    print(f'merchant feed: {len(items)} products')


if __name__ == '__main__':
    main()
