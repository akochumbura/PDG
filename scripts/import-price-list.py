"""Import the owner's XAG price list (xlsx, sheet "Full Item Price List") into scripts/catalog.csv.

Usage:  python scripts/import-price-list.py PATH/TO/PDG_XAG_Complete_Item_Price_List_With_Margins.xlsx
Keeps the three P150 MAX packages (kit rows) and the non-invoice rows (avail=quote / legacy) and replaces the price-list rows:
SKU = the XAG manufacturer code (მწარმოებლის კოდი, e.g. 09-017-00073), looked up from the invoice code (Code, P0000…)
in scripts/supplier-code-map.csv (made from PDG_Invoice_Packing_List_Georgian.xlsx, owner 14 Oct 2026);
name = Original item (English), name_ka = Georgian item, gel = Retail incl. VAT GEL.
The P150 MAX drone is imported as the standalone platform listing (owner, 16 Oct 2026: 41,999 GEL, RevoSpray 5 only,
no controller/batteries/chargers), with the clean names in NAMES; the packages stay unchanged.
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
    s = re.sub(r'(?<=[A-Za-z0-9\u10d0-\u10ff)])\((?=[A-Za-z0-9\u10d0-\u10ff])', ' (', s)  # "Station(INTL)" -> "Station (INTL)"
    if s.count('(') > s.count(')'):
        s += ')'
    return s


# Owner, 15 Oct 2026: the RevoSling and its landing gear (05-002-02683) are one system, sold together as one item.
MERGE = {'05-002-02683': '05-002-02682'}
# Clean shop names that replace the price-list text (sku: (en, ka, ru); '' = keep the price-list value).
NAMES = {'09-007-00188': ('XAG P150 MAX Platform (RevoSpray 5)', 'XAG P150 MAX პლატფორმა (RevoSpray 5)', 'Платформа XAG P150 MAX (RevoSpray 5)'),
         '09-017-00065': ('', 'XAG 2024 აკუმულატორის გაგრილების მოწყობილობა (ავზი, INTL), სასოფლო-სამეურნეო დრონის აკუმულატორების გასაგრილებლად', ''),
         '05-002-02682': ('', '', 'Система подвеса груза XAG RevoSling с посадочным шасси (05-002-02683), INTL')}
MERGED_NAMES = {'05-002-02682': ('XAG RevoSling system (RevoSling + Landing Gear 05-002-02683, INTL)',
                                 'XAG RevoSling ტვირთის საკიდი სისტემა დასაჯდომი შასით (05-002-02683), INTL — ტვირთის გადასატანად')}


def merge_systems(out):
    """Fold each MERGE child into its parent: one row, prices added, child removed."""
    by = {r['sku']: r for r in out}
    for child, parent in MERGE.items():
        if child in by and parent in by:
            by[parent]['gel'] = str(int(by[parent]['gel']) + int(by[child]['gel']))
            by[parent]['name'], by[parent]['name_ka'] = MERGED_NAMES[parent]
            out.remove(by[child])
    return out


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
        group = 'drone' if re.search(r'Agricultural Drone', en) else GROUP.get(cat)
        seen.add(sku)
        if not group:
            raise SystemExit(f'Unknown category {cat!r} for {sku}: add it to GROUP')
        row = {f: '' for f in fields}
        gel = fastener_gel(r[col['Landed unit cost GEL']]) if fastener(sku, en) else int(round(float(r[col['Retail incl. VAT GEL']])))
        row.update(group=group, name=en, name_ka=ka, sku=sku, gel=str(gel))
        out.append(row)
    out += [r for r in extra if r['sku'] not in seen]
    out = merge_systems(out)
    for r in out:
        for f, v in zip(('name', 'name_ka', 'name_ru'), NAMES.get(r['sku'], ())):
            if v:
                r[f] = v
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
