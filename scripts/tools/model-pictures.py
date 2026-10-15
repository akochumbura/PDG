"""Gallery pictures for the previous-generation model pages (owner photos, 15 Oct 2026).
Usage: python scripts/tools/model-pictures.py  (sources: owner uploads, paths below). Output: dist/assets/img/models/<slug>-N.webp (+ -t thumbs).
Every picture is placed on a 4:3 canvas; non-4:3 pictures sit on a blurred copy of themselves. The P100 expo photo is cropped to remove the person."""
from PIL import Image, ImageFilter
from pathlib import Path
U = Path('/root/.claude/uploads/3f4209c6-7936-56a3-b322-1ac209a877c5')
OUT = Path(__file__).resolve().parents[2] / 'dist/assets/img/models'
W, H = 1200, 900


def flat(im):
    if im.mode == 'RGBA':
        bg = Image.new('RGB', im.size, 'white'); bg.paste(im, mask=im.split()[3]); return bg
    return im.convert('RGB')


def fit43(im, blur=True, bgcol=None):
    im = flat(im)
    if abs(im.width / im.height - 4 / 3) < .01:
        return im.resize((W, H), Image.LANCZOS)
    s = min(W / im.width, H / im.height)
    fg = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    bg = (im.resize((W, H)).filter(ImageFilter.GaussianBlur(40)) if blur else Image.new('RGB', (W, H), bgcol or 'white'))
    bg.paste(fg, ((W - fg.width) // 2, (H - fg.height) // 2)); return bg


def trim(im, pad=40):
    im = flat(im)
    from PIL import ImageChops
    d = ImageChops.difference(im, Image.new('RGB', im.size, 'white')).point(lambda v: 255 if v > 12 else 0).getbbox()
    return im.crop((max(d[0] - pad, 0), max(d[1] - pad, 0), min(d[2] + pad, im.width), min(d[3] + pad, im.height)))


def save(im, name):
    im.save(OUT / f'{name}.webp', quality=82, method=6)
    im.resize((240, 180), Image.LANCZOS).save(OUT / f'{name}-t.webp', quality=80, method=6)


save(fit43(Image.open(U / '37386242-image.jpg')), 'p100-1')
save(fit43(Image.open(U / '2caa9263-image.jpg').crop((290, 290, 1932, 1932))), 'p100-2')  # person (left edge) cropped out
save(fit43(trim(Image.open(U / '635136a8-image.webp')), blur=False), 'p100pro-1')
save(fit43(Image.open(U / '5153c6a8-image.webp'), blur=False), 'p100pro-2')
save(fit43(Image.open(U / '1ccbae5f-image.jpg')), 'v40-1')
save(fit43(Image.open(U / '452b2693-image.webp')), 'v40-2')
