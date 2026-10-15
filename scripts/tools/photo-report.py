"""Writes scripts/photo-unmatched.csv: every shop card that still shows the XAG logo, with the reason.
Photos come only from the parts PDFs (scripts/pdf-part-matches.csv, matched by exact manufacturer code); nothing is guessed."""
import csv, os
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
cat = list(csv.DictReader(open(ROOT / 'scripts/catalog.csv', encoding='utf-8')))
pdf = {r['manufacturer_code']: r for r in csv.DictReader(open(ROOT / 'scripts/pdf-part-matches.csv', encoding='utf-8'))}
have = {f[:-5] for f in os.listdir(ROOT / 'dist/assets/img/products') if f.endswith('.webp')}
out, total = [], 0
for r in cat:
    if r['group'] == 'kit':
        continue
    total += 1
    if r['sku'] in have:
        continue
    p = pdf.get(r['sku'])
    if not p:
        why = 'not listed in any of the 11 parts PDFs'
    elif 'shared' in p['photo_note']:
        why = 'PDF picture is shared by different part numbers (not used): ' + p['photo_note'].split(': ')[-1]
    elif p['photo_note']:
        why = 'PDF card has no usable picture (' + p['photo_note'] + ')'
    else:
        why = 'PDF card has no usable picture'
    out.append((r['sku'], r['name'], r['group'], r.get('avail') or 'in stock list', why))
with open(ROOT / 'scripts/photo-unmatched.csv', 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f); w.writerow(['sku', 'name', 'group', 'listing', 'reason']); w.writerows(out)
legacy = ['XAG-P100PRO', 'XAG-P100', 'XAG-V40']
print(f'{total} part cards, {total - len(out)} with a verified PDF photo, {len(out)} without (scripts/photo-unmatched.csv)')
print('previous models without photo (no verified official photograph available):', ', '.join(legacy))
