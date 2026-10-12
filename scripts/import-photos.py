"""Convert a folder of photos named by SKU (e.g. 09-017-00083.jpg) into dist/assets/img/products/<SKU>.webp.
Usage: python scripts/import-photos.py path/to/photos   (needs: pip install pillow)"""
import sys
from pathlib import Path
from PIL import Image
src=Path(sys.argv[1]); out=Path(__file__).resolve().parents[1]/'dist/assets/img/products'; out.mkdir(parents=True,exist_ok=True)
for f in src.iterdir():
    if f.suffix.lower() in {'.jpg','.jpeg','.png','.webp'}:
        im=Image.open(f).convert('RGB'); im.thumbnail((1200,1200)); im.save(out/(f.stem+'.webp'),quality=84); print('ok',f.stem)

skus=sorted(f.stem for f in out.glob('*.webp'))
(out.parent.parent/'js/photos.js').write_text('window.PDG_PHOTOS='+__import__('json').dumps(skus)+';\n',encoding='utf-8')
print(len(skus),'photos registered')
