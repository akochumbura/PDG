"""One-off (14 Oct 2026): package pictures from the owner-supplied XAG P150 MAX images (chat uploads, not in the repo).
compose.py part: the Pro picture = XAG combo (6 batteries, 2 chargers, SRC5, XRTK7, 2 cooling tanks); Starter removes the XRTK7
and 2 batteries, Business adds 2 batteries and 2 chargers (battery stack spliced by whole battery periods, charger pair from the
second XAG combo picture because the first had the shop zoom button over it). gallery.py part: zoom buttons and card borders removed.
"""
from PIL import Image
import numpy as np
U='/root/.claude/uploads/3f4209c6-7936-56a3-b322-1ac209a877c5/'
B=Image.open(U+'6096b32e-image.png').convert('RGB'); A=Image.open(U+'387c9af4-image.png').convert('RGB')
bn=np.array(B).astype(int)
Y0,Y1=790,956
def crop(x0,x1,img=B,y0=Y0,y1=Y1): return img.crop((x0,y0,x1,y1))
remote=crop(20,152); rtk=crop(170,238); towers=crop(284,492)
stack=np.array(crop(574,966)).astype(int)
D=64
def nstack(n):
    if n==6: return Image.fromarray(stack.astype('uint8'))
    k=abs(n-6)//2*2*D//2*1  # periods to remove/add = |n-6|
    p=abs(n-6)*D
    g=stack.astype(float).mean(2)
    lo,hi=120,stack.shape[1]-120-p
    x=min(range(lo,hi),key=lambda x: np.abs(g[:,x]-g[:,x+p]).sum())
    if n<6: out=np.concatenate([stack[:,:x],stack[:,x+p:]],1)
    else: out=np.concatenate([stack[:,:x+p],stack[:,x:]],1)
    return Image.fromarray(out.astype('uint8'))
# chargers pair from image 1 (no zoom button over it), scaled to image-11 size
ch=A.crop((796,782,1062,940))
from PIL import ImageDraw
ImageDraw.Draw(ch).rectangle((1047-796,880-782,ch.width,ch.height),fill='white')  # tip of the separate power cord
s=151/147
ch=ch.resize((round(ch.width*s),round(ch.height*s)),Image.LANCZOS)
def whiten_cord(im):  # nothing
    return im
def row(items,gap=44):
    W=sum(i.width for i in items)+gap*(len(items)-1); H=max(i.height for i in items)
    r=Image.new('RGB',(W,H),'white'); x=0
    for i in items:
        r.paste(i,(x,H-i.height),); x+=i.width+gap
    return r
def compose(n_bat,n_ch,with_rtk,name):
    c=Image.new('RGB',(1400,960),'white')
    drone=B.crop((30,140,1372,745)); c.paste(drone,(29,150))
    items=[remote]+([rtk] if with_rtk else [])+[towers,nstack(n_bat)]+[ch]*(n_ch//2)
    r=row(items)
    if r.width>1320: r=r.resize((1320,round(r.height*1320/r.width)),Image.LANCZOS)
    c.paste(r,((1400-r.width)//2,940-r.height))
    c.save(name+'.png'); return c
compose(4,2,False,'starter'); compose(6,2,True,'pro'); compose(8,4,True,'business')

# ---- gallery ----
from PIL import Image, ImageChops
import numpy as np
U='/root/.claude/uploads/3f4209c6-7936-56a3-b322-1ac209a877c5/'
OUT='/home/claude/pdg/dist/assets/img/'
def fit43(im, pad=0.06):
    box=ImageChops.difference(im,Image.new('RGB',im.size,'white')).convert('L').point(lambda v:255 if v>14 else 0).getbbox()
    im=im.crop(box); W,H=1200,900
    s=min(W*(1-2*pad)/im.width,H*(1-2*pad)/im.height)
    im=im.resize((round(im.width*s),round(im.height*s)),Image.LANCZOS)
    c=Image.new('RGB',(W,H),'white'); c.paste(im,((W-im.width)//2,(H-im.height)//2)); return c
def render(n):
    im=Image.open(U+n+'-image.png').convert('RGB'); W,H=im.size; a=np.array(im)
    a[H-170:,W-170:]=255          # the shop's zoom button, not part of the picture
    a[:8,:]=255; a[-8:,:]=255; a[:,:8]=255; a[:,-8:]=255   # card border of the screenshot
    return fit43(Image.fromarray(a))
def photo(n):
    im=Image.open(U+n+'-image.png').convert('RGB'); W,H=im.size
    im=im.crop((6,6,W-170,H-6))   # cut the zoom button and rounded card corners
    w,h=im.size
    if w/h>4/3: nw=round(h*4/3); im=im.crop(((w-nw)//2,0,(w-nw)//2+nw,h))
    else: nh=round(w*3/4); im=im.crop((0,(h-nh)//2,w,(h-nh)//2+nh))
    return im.resize((1200,900),Image.LANCZOS)
G=[('c596682a',render),('d945cba7',render),('68a548e0',render),('dddcd0dc',render),('29a38c8b',render),
   ('e149b3e0',photo),('5c5fa8d6',photo),('54f20ab0',photo),('787885b3',photo)]
for i,(n,f) in enumerate(G,1):
    f(n).save(OUT+f'packages/p150-max-{i}.webp','WEBP',quality=84,method=6)
for k,sku in [('starter','STARTER'),('pro','PRO'),('business','BUSINESS')]:
    fit43(Image.open(k+'.png').convert('RGB'),pad=0.03).save(OUT+f'products/PDG-P150MAX-{sku}.webp','WEBP',quality=86,method=6)
print('ok')
# thumbnails for the package page gallery
import glob,os
for f in glob.glob(OUT+'packages/p150-max-[0-9].webp')+glob.glob(OUT+'products/PDG-P150MAX-*.webp'):
    if f.endswith('-t.webp'): continue
    Image.open(f).convert('RGB').resize((240,180),Image.LANCZOS).save(f.replace('.webp','-t.webp').replace('/products/','/packages/'),'WEBP',quality=80,method=6)
print(sorted(os.listdir(OUT+'packages')))
