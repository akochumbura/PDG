"""Regenerate the shop product cards from scripts/catalog.csv and scripts/pricing.py."""
import csv,html,re,sys
from decimal import Decimal,ROUND_HALF_UP
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'scripts'))
import pricing
RATE=Decimal(pricing.RATE)
def gel(usd,mark): return int((Decimal(str(usd))*Decimal(mark)*RATE).quantize(Decimal('1'),ROUND_HALF_UP))
FB={'power':('battery.webp',960,1280,'50% 50%'),'spray':('drone-detail.webp',1280,960,'30% 70%'),'control':('field-ready.webp',1280,960,'50% 60%'),'acc':('transport.webp',960,1280,'50% 40%'),'spare':('drone-detail.webp',1280,960,'70% 30%'),
 'flight':('p150-max-flight-1200.webp',1200,500,'50% 60%'),'field':('field-ready.webp',1280,960,'50% 60%'),'detail':('drone-detail.webp',1280,960,'50% 45%'),'transport':('transport.webp',960,1280,'50% 55%')}
def card(r):
    g=r['group']; kit=g=='kit'; key=(r.get('image') or 'flight') if kit else g
    fb,w,h,pos=FB[key]; n=html.escape(r['name'],quote=True); s=r['sku']; p=gel(r['usd'],pricing.MARKUP_KITS if kit else pricing.MARKUP_PARTS)
    return (f'<article class="product{" product-kit" if kit else ""}" data-cat="{g}"><div class="product-photo"><img src="/assets/img/{fb}" width="{w}" height="{h}" data-photo="/assets/img/products/{s}.webp" alt="{n}" style="object-position:{pos}" loading="lazy" decoding="async"></div>'
      f'<div class="product-body"><p class="product-sku">{s}</p><h3>{n}</h3><p class="product-stock" data-i18n="in_stock">საწყობშია</p>'
      f'<div class="product-buy"><span class="product-price">₾{p:,}</span><button type="button" class="add-btn" data-sku="{s}" data-name="{n}" data-price="{p}" data-i18n="add_to_cart">კალათაში</button></div></div></article>\n')
rows=list(csv.DictReader(open(ROOT/'scripts/catalog.csv',encoding='utf-8')))
kits=''.join(card(r) for r in rows if r['group']=='kit'); parts=''.join(card(r) for r in rows if r['group']!='kit')
pb=ROOT/'scripts/page-bodies.html'; t=pb.read_text(encoding='utf-8')
t,a=re.subn(r'(<div class="shop-grid kit-grid">\n).*?(</div></div></section>\n\s*<section class="section shop-section shop-alt")',lambda m:m.group(1)+kits+m.group(2),t,flags=re.S)
t,b=re.subn(r'(<div class="shop-grid" id="partsGrid">\n).*?(</div></div></section>\n\s*<dialog)',lambda m:m.group(1)+parts+m.group(2),t,flags=re.S)
assert a==1 and b==1,'shop template markers not found'
pb.write_text(t,encoding='utf-8'); print(f'shop: {len(rows)} products ({sum(r["group"]=="kit" for r in rows)} kits)')
