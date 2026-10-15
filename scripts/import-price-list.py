"""Import the owner's XAG price list (xlsx, sheet "Full Item Price List") into scripts/catalog.csv.

Usage:  python scripts/import-price-list.py PATH/TO/PDG_XAG_Complete_Item_Price_List_With_Margins.xlsx
Keeps the three P150 MAX packages (kit rows) and the non-invoice rows (avail=quote / legacy) and replaces the price-list rows:
SKU = the XAG manufacturer code (მწარმოებლის კოდი, e.g. 09-017-00073), looked up from the invoice code (Code, P0000…)
in scripts/supplier-code-map.csv (made from PDG_Invoice_Packing_List_Georgian.xlsx, owner 14 Oct 2026);
name = Original item (English), name_ka = Georgian item, gel = Retail incl. VAT GEL.
The P150 MAX drone itself is sold only in the packages (owner, 14 Oct 2026), so it is not imported as a separate item.
Cost and margin columns are internal and are NOT copied (the landed cost only sets the 5-15 GEL fastener price). Then run: python scripts/build.py
"""
import csv, re, sys
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / 'scripts/catalog.csv'
CODE_MAP = ROOT / 'scripts/supplier-code-map.csv'
GROUP = {'Battery': 'power', 'Charging': 'power',
         'Spraying': 'spray', 'Spreading': 'spray', 'Tank': 'spray', 'Pump': 'spray', 'Cargo': 'spray',
         'RTK': 'control', 'Electronics': 'control',
         'Lighting': 'acc', 'Landing gear': 'acc',
         'Spare part': 'spare', 'Cable': 'spare', 'Motor': 'spare', 'Propeller': 'spare'}


# Owner, 14 Oct 2026: screws and similar small fasteners cost 5-15 GEL, by their invoice cost (overrides the price list):
# price = landed unit cost x 2.5 + 3.5, rounded, kept between 5 and 15 GEL (cheapest screws 5, dearest bolts 15).
# Fasteners = the XAG standard-fastener family 02-004-* (screws, nuts, rivets, flat gaskets) and any nut / bolt / circlip / M-size gasket.
def fastener_gel(cost):
    return max(5, min(15, int(round(float(cost) * 2.5 + 3.5))))


def fastener(sku, en):
    return sku.startswith('02-004-') or bool(re.search(r'\b(nut|bolt|circlip)\b|^M[\d.]+\*[\d.*]+ ?gasket', en, re.I))


def clean(s):
    s = str(s or '').replace('（', '(').replace('）', ')').replace('，', ', ').replace('；', '; ')
    s = re.sub(r'\s+', ' ', s).strip()
    if s.count('(') > s.count(')'):
        s += ')'
    return s


def main(path):
    ws = openpyxl.load_workbook(path, data_only=True)['Full Item Price List']
    head = [c.value for c in ws[6]]
    need = ['Code', 'Category', 'Georgian item', 'Original item', 'Retail incl. VAT GEL', 'Landed unit cost GEL']
    col = {h: head.index(h) for h in need}
    code_map = {r['supplier_code']: r['manufacturer_code'] for r in csv.DictReader(open(CODE_MAP, encoding='utf-8'))}
    rows = list(csv.DictReader(open(CATALOG, encoding='utf-8')))
    fields = list(rows[0].keys())
    if 'avail' not in fields:
        fields.append('avail')
    # Keep the packages and every row that does not come from the price list: quote-only parts from the XAG parts
    # catalogues (avail=quote) and previous-generation models (avail=legacy). See scripts/pdf-part-matches.csv.
    out = [r for r in rows if r['group'] == 'kit']
    extra = [r for r in rows if r.get('avail') in ('quote', 'legacy')]
    seen = set()
    for r in ws.iter_rows(min_row=7, values_only=True):
        code = clean(r[col['Code']])
        if not code or r[col['Retail incl. VAT GEL']] in (None, ''):
            continue
        if code not in code_map:
            raise SystemExit(f'No manufacturer code for {code}: add it to scripts/supplier-code-map.csv (packing list)')
        sku = code_map[code]
        if sku in seen:
            continue  # the same code twice on the invoice = one product
        en, ka = clean(r[col['Original item']]), clean(r[col['Georgian item']])
        cat = clean(r[col['Category']])
        if re.search(r'Agricultural Drone', en):
            continue  # the drone is sold only in the P150 MAX packages
        group = GROUP.get(cat)
        seen.add(sku)
        if not group:
            raise SystemExit(f'Unknown category {cat!r} for {sku}: add it to GROUP')
        row = {f: '' for f in fields}
        gel = fastener_gel(r[col['Landed unit cost GEL']]) if fastener(sku, en) else int(round(float(r[col['Retail incl. VAT GEL']])))
        row.update(group=group, name=en, name_ka=ka, sku=sku, gel=str(gel))
        out.append(row)
    out += [r for r in extra if r['sku'] not in seen]
    with open(CATALOG, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
        w.writeheader()
        w.writerows(out)
    kits = sum(1 for r in out if r['group'] == 'kit')
    print(f'catalog: {len(out)} rows ({kits} packages, {len(seen)} price-list items, {len(out) - kits - len(seen)} quote-only parts)')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(sys.argv[1])
