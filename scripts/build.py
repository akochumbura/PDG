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
# analytics.js is generated from site_config.GA_ID (empty ID = file does nothing and the CSP does not open Google hosts)
import site_config as _sc
GA=getattr(_sc,'GA_ID','').strip()
# Events (SEO/measurement brief, 19 Oct 2026): call_click, whatsapp_click, messenger_click, email_click (any link, with its place on the page),
# generate_lead (consultation form accepted by the server, with topic), whatsapp_order / email_order (cart), via the 'pdg:track' DOM event.
GA_EVENTS = r"""
function pdgWhere(a){var n=a.closest('[id],header,footer,.mobile-bar,.chat-panel');if(!n)return 'page';if(n.matches('header'))return 'header';if(n.matches('footer'))return 'footer';if(n.matches('.mobile-bar'))return 'mobile_bar';if(n.matches('.chat-panel'))return 'chat';return n.id;}
document.addEventListener('click',function(e){var c=e.target.closest&&e.target.closest('[data-chat-open]');if(c)gtag('event','chat_open',{link_location:pdgWhere(c),page_path:location.pathname});var a=e.target.closest&&e.target.closest('a[href]');if(!a)return;var h=a.getAttribute('href')||'',n=null;
if(/^tel:/i.test(h))n='call_click';else if(/wa\.me\//i.test(h))n='whatsapp_click';else if(/m\.me\//i.test(h))n='messenger_click';else if(/^mailto:/i.test(h))n='email_click';
if(n)gtag('event',n,{link_location:pdgWhere(a),page_path:location.pathname});},true);
document.addEventListener('pdg:track',function(e){var d=e.detail||{};if(d.name)gtag('event',d.name,Object.assign({page_path:location.pathname},d.params||{}));});
"""
(D/'assets/js/analytics.js').write_text(("window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}gtag('js',new Date());gtag('config','"+GA+"',{anonymize_ip:true});var pdgGs=document.createElement('script');pdgGs.async=true;pdgGs.src='https://www.googletagmanager.com/gtag/js?id="+GA+"';document.head.appendChild(pdgGs);\n"+GA_EVENTS) if GA else "/* analytics off: set GA_ID in scripts/site_config.py */\n",encoding='utf-8')
ver={p:hashlib.sha1((D/p.lstrip('/')).read_bytes()).hexdigest()[:10] for p in ['/assets/css/style.css']+[f'/assets/js/{n}' for n in ('content.js','script.js','shop.js','payments-config.js','chat.js','account.js','analytics.js')] if (D/p.lstrip('/')).exists()}
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

# Security headers: the CSP lists the SHA-256 of each inline script (only the theme bootstrap today); nothing else may run.
import base64
def csp_hashes():
    found=set()
    for f in D.rglob('*.html'):
        for m in re.finditer(r'<script(?![^>]*\bsrc=)([^>]*)>(.*?)</script>',f.read_text(encoding='utf-8'),re.S):
            if 'json' in m.group(1): continue
            found.add("'sha256-"+base64.b64encode(hashlib.sha256(m.group(2).encode('utf-8')).digest()).decode()+"'")
    return sorted(found)
GAH=" https://static.cloudflareinsights.com"+(" https://www.googletagmanager.com" if GA else "")  # Cloudflare Web Analytics beacon is always allowed
CSP=("default-src 'self'; script-src 'self' "+' '.join(csp_hashes())+GAH+"; style-src 'self' 'unsafe-inline'; img-src 'self' data:"+(" https://www.google-analytics.com https://www.googletagmanager.com" if GA else "")+"; font-src 'self'; "
     "connect-src 'self' https://cloudflareinsights.com"+(" https://*.google-analytics.com https://*.analytics.google.com https://www.googletagmanager.com" if GA else "")+"; media-src 'self'; object-src 'none'; frame-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'self'; upgrade-insecure-requests")
hp=D/'_headers'; hs=hp.read_text(encoding='utf-8')
hs=re.sub(r'^  (Content-Security-Policy|Strict-Transport-Security):.*\n','',hs,flags=re.M)
hs=hs.replace('/*\n','/*\n  Strict-Transport-Security: max-age=31536000\n  Content-Security-Policy: '+CSP+'\n',1)
hp.write_text(hs,encoding='utf-8')
if shutil.which('node'):
    for f in ('content','script','shop','payments-config','chat','account'): run('node','--check',f'dist/assets/js/{f}.js')
    import tempfile  # the worker is an ES module: check it as one (a .js copy is parsed as a script and misses duplicate declarations)
    with tempfile.TemporaryDirectory() as td:
        (Path(td)/'worker.mjs').write_text((D/'_worker.js').read_text(encoding='utf-8'),encoding='utf-8'); run('node','--check',str(Path(td)/'worker.mjs'))
run(py,'scripts/verify-site.py'); print('BUILD OK')
