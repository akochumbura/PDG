"""Add real product photos to the shop.

1. Put photos in one folder, each named by the part code (SKU), e.g. 09-017-00083.jpg
   (the list of codes is in scripts/photo-checklist.csv).
2. Run:  python scripts/import-photos.py path/to/folder
3. Run:  python scripts/build.py     (the shop then uses each photo automatically)

Needs: pip install pillow
"""
import csv, sys
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist/assets/img/products'
SKUS = {r['sku'] for r in csv.DictReader(open(ROOT / 'scripts/catalog.csv', encoding='utf-8'))}
if len(sys.argv) != 2:
    raise SystemExit(__doc__)
OUT.mkdir(parents=True, exist_ok=True)
done = 0
for f in sorted(Path(sys.argv[1]).iterdir()):
    if f.suffix.lower() not in {'.jpg', '.jpeg', '.png', '.webp'}:
        continue
    if f.stem not in SKUS:
        print('skipped (name is not a part code from catalog.csv):', f.name)
        continue
    im = ImageOps.exif_transpose(Image.open(f)).convert('RGB')
    im.thumbnail((1400, 1400))
    im.save(OUT / (f.stem + '.webp'), quality=84)
    done += 1
    print('added', f.stem)
print(f'{done} photo(s) added. Now run: python scripts/build.py')
