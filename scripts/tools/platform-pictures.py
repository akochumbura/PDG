"""Pictures for the standalone P150 MAX platform page (owner photos, 16 Oct 2026) and small configurator thumbnails.
Usage: python scripts/tools/platform-pictures.py [front.webp] [field.jpg]
- front render -> dist/assets/img/products/09-007-00188.webp (shop/product photo) and dist/assets/img/platform/platform-front(-t).webp:
  white background trimmed, the whole drone kept (propellers not cropped), centred on a 4:3 canvas.
- field photo -> dist/assets/img/platform/platform-field(-t).webp (centre crop to 4:3).
- configurator thumbnails: dist/assets/img/products/thumbs/<sku>.webp (96x72) from each product's own photo.
"""
import sys
from pathlib import Path
from PIL import Image, ImageChops
ROOT = Path(__file__).resolve().parents[2]
IMG = ROOT / 'dist/assets/img'
THUMBS = ['09-027-00003', '05-002-02725', '09-017-00073', '09-017-00069', '09-017-00065', '09-016-00083', '09-017-00109', '09-023-00145', '05-002-02682', '05-002-02640', '09-007-00188']


def fit(im, w, h, pad=0.06):
    im = im.convert('RGB')
    box = ImageChops.difference(im, Image.new('RGB', im.size, 'white')).point(lambda v: 255 if v > 10 else 0).getbbox()
    im = im.crop(box)
    s = min(w * (1 - 2 * pad) / im.width, h * (1 - 2 * pad) / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    c = Image.new('RGB', (w, h), 'white'); c.paste(im, ((w - im.width) // 2, (h - im.height) // 2)); return c


def crop43(im):
    im = im.convert('RGB'); w = min(im.width, round(im.height * 4 / 3)); h = round(w * 3 / 4)
    l, t = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((l, t, l + w, t + h))


if len(sys.argv) > 1:
    front = fit(Image.open(sys.argv[1]), 1200, 900)
    front.save(IMG / 'products/09-007-00188.webp', quality=86, method=6)
    front.save(IMG / 'platform/platform-front.webp', quality=86, method=6)
    front.resize((240, 180), Image.LANCZOS).save(IMG / 'platform/platform-front-t.webp', quality=82, method=6)
if len(sys.argv) > 2:
    field = crop43(Image.open(sys.argv[2])).resize((800, 600), Image.LANCZOS)
    field.save(IMG / 'platform/platform-field.webp', quality=84, method=6)
    field.resize((240, 180), Image.LANCZOS).save(IMG / 'platform/platform-field-t.webp', quality=82, method=6)
for sku in THUMBS:
    src = IMG / f'products/{sku}.webp'
    if src.is_file():
        fit(Image.open(src), 192, 144, 0.04).save(IMG / f'products/thumbs/{sku}.webp', quality=82, method=6)
print('platform pictures done')
