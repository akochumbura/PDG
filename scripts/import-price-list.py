"""Import the owner's XAG price list (xlsx, sheet "Full Item Price List") into scripts/catalog.csv.

Usage:  python scripts/import-price-list.py PATH/TO/PDG_XAG_Complete_Item_Price_List_With_Margins.xlsx
Keeps the three P150 MAX packages (kit rows) as they are and replaces every other row with the price list:
SKU = Code, name = Original item (English), name_ka = Georgian item, gel = Retail incl. VAT GEL.
Cost and margin columns are internal and are NOT copied. Then run: python scripts/build.py
"""
import csv, re, sys
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / 'scripts/catalog.csv'
GROUP = {'Battery': 'power', 'Charging': 'power',
         'Spraying': 'spray', 'Spreading': 'spray', 'Tank': 'spray', 'Pump': 'spray', 'Cargo': 'spray',
         'RTK': 'control', 'Electronics': 'control',
         'Lighting': 'acc', 'Landing gear': 'acc',
         'Spare part': 'spare', 'Cable': 'spare', 'Motor': 'spare', 'Propeller': 'spare'}


def clean(s):
    s = str(s or '').replace('（', '(').replace('）', ')').replace('，', ', ').replace('；', '; ')
    s = re.sub(r'\s+', ' ', s).strip()
    if s.count('(') > s.count(')'):
        s += ')'
    return s


def main(path):
    ws = openpyxl.load_workbook(path, data_only=True)['Full Item Price List']
    head = [c.value for c in ws[6]]
    need = ['Code', 'Category', 'Georgian item', 'Original item', 'Retail incl. VAT GEL']
    col = {h: head.index(h) for h in need}
    rows = list(csv.DictReader(open(CATALOG, encoding='utf-8')))
    fields = list(rows[0].keys())
    out = [r for r in rows if r['group'] == 'kit']
    seen = set()
    for r in ws.iter_rows(min_row=7, values_only=True):
        sku = clean(r[col['Code']])
        if not sku or r[col['Retail incl. VAT GEL']] in (None, ''):
            continue
        if sku in seen:
            continue  # the same code twice on the invoice = one product
        seen.add(sku)
        en, ka = clean(r[col['Original item']]), clean(r[col['Georgian item']])
        cat = clean(r[col['Category']])
        group = 'drone' if re.search(r'Agricultural Drone', en) else GROUP.get(cat)
        if not group:
            raise SystemExit(f'Unknown category {cat!r} for {sku}: add it to GROUP')
        row = {f: '' for f in fields}
        row.update(group=group, name=en, name_ka=ka, sku=sku, gel=str(int(round(float(r[col['Retail incl. VAT GEL']])))))
        out.append(row)
    with open(CATALOG, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
        w.writeheader()
        w.writerows(out)
    print(f'catalog: {len(out)} rows ({len(out) - len(seen)} packages, {len(seen)} items from the price list)')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(sys.argv[1])
