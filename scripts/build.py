"""One command to rebuild and check the whole site:  python scripts/build.py"""
import os,sys as _sys
if os.environ.get('CF_PAGES'):
    # On Cloudflare Pages: dist/ is already built, checked and committed, so publish it as is.
    print('Cloudflare Pages: publishing the committed dist/ folder as is.'); _sys.exit(0)
import subprocess,sys,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'scripts')); import pricing
def run(*a): 
    r=subprocess.run(list(a),cwd=ROOT)
    if r.returncode: sys.exit(r.returncode)
py=sys.executable
run(py,'scripts/build-shop.py'); run(py,'scripts/build-specs.py'); run(py,'scripts/build-products.py'); run(py,'scripts/build-pages.py',pricing.SITE_URL); run(py,'scripts/build-search.py')
# Cache busting: every page asks for the current CSS/JS (assets are cached for an hour by Cloudflare and browsers).
import hashlib,re
D=ROOT/'dist'
ver={p:hashlib.sha1((D/p.lstrip('/')).read_bytes()).hexdigest()[:10] for p in ['/assets/css/style.css']+[f'/assets/js/{n}' for n in ('content.js','script.js','shop.js','payments-config.js','chat.js','account.js')] if (D/p.lstrip('/')).exists()}
# Images too (logos, product photos): a recoloured or replaced picture must reach visitors at once, not after the cache expires.
def img_ver(p):
    f=D/p.lstrip('/')
    if p not in ver and f.is_file(): ver[p]=hashlib.sha1(f.read_bytes()).hexdigest()[:10]
    return ver.get(p)
for f in D.rglob('*.html'):
    s=f.read_text(encoding='utf-8')
    s2=re.sub(r'(?<=["(])(/assets/(?:css|js)/[\w.-]+\.(?:css|js))(?:\?v=[0-9a-f]+)?(?=[")])',lambda m:m.group(1)+('?v='+ver[m.group(1)] if m.group(1) in ver else ''),s)
    s2=re.sub(r'(?<=")(/assets/img/[\w./-]+\.(?:png|svg|webp|jpg))(?:\?v=[0-9a-f]+)?(?=[" ])',lambda m:m.group(1)+('?v='+img_ver(m.group(1)) if img_ver(m.group(1)) else ''),s2)
    if s2!=s: f.write_text(s2,encoding='utf-8')
if shutil.which('node'):
    for f in ('content','script','shop','payments-config','chat','account'): run('node','--check',f'dist/assets/js/{f}.js')
    run('node','--check','dist/_worker.js')
run(py,'scripts/verify-site.py'); print('BUILD OK')
