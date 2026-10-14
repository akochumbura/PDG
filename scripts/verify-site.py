"""Check all shipped pages, local resources, anchors and translation coverage."""
from pathlib import Path
from urllib.parse import urlsplit, unquote
from collections import Counter
import json
import re
from lxml import html
from fontTools.ttLib import TTFont

ROOT=Path(__file__).resolve().parents[1]
PUBLIC=ROOT/'dist'
content=(PUBLIC/'assets/js/content.js').read_text(encoding='utf-8')
translations=json.loads(content.split('=',1)[1].strip().removesuffix(';'))
errors=[]
files=sorted(PUBLIC.rglob('*.html'))
documents={p:html.document_fromstring(p.read_text(encoding='utf-8')) for p in files}
resources=0
for path,doc in documents.items():
    relative=path.relative_to(PUBLIC)
    lang=doc.get('lang')
    if lang not in ['ka','en','ru']:errors.append(f'{relative}: bad language')
    ids=Counter(doc.xpath('//*[@id]/@id'))
    if any(n>1 for n in ids.values()):errors.append(f'{relative}: duplicate IDs')
    if len(doc.xpath('//h1'))!=1:errors.append(f'{relative}: expected one h1')
    if not doc.xpath('//meta[@name="description"]/@content'):errors.append(f'{relative}: no description')
    if path.name=='404.html':
        if not doc.xpath('//meta[@name="robots" and @content="noindex"]'):errors.append(f'{relative}: 404 page must be noindex')
    elif len(doc.xpath('//link[@rel="canonical"]'))!=1:errors.append(f'{relative}: canonical missing or duplicated')
    for script in doc.xpath('//script[@type="application/ld+json"]'):
        try:json.loads(script.text_content())
        except ValueError:errors.append(f'{relative}: invalid JSON-LD')
    for href in doc.xpath('//a/@href'):
        parts=urlsplit(href)
        if not parts.scheme and not parts.netloc and parts.path.endswith('.html'):errors.append(f'{relative}: link uses .html URL {href} (use the clean URL)')
    for card in doc.xpath('//article[contains(@class,"product") and @data-cat!="kit"]'):
        for src in card.xpath('.//img/@src'):
            if not src.startswith('/assets/img/products/'):errors.append(f'{relative}: part card shows another product photo {src}')
    for node in doc.xpath('//*[@data-i18n] | //*[@data-i18n-aria] | //*[@data-i18n-alt] | //*[@data-i18n-content] | //*[@data-i18n-placeholder]'):
        for attr in ['data-i18n','data-i18n-aria','data-i18n-alt','data-i18n-content','data-i18n-placeholder']:
            key=node.get(attr)
            if key:
                for target in ['en','ru']:
                    if key not in translations[target]:errors.append(f'{relative}: missing {target}/{key}')
    for img in doc.xpath('//img'):
        if img.get('alt') is None:errors.append(f'{relative}: image without alt')
        if img.get('src') and (not img.get('width') or not img.get('height')):errors.append(f'{relative}: image lacks dimensions')
    for node in doc.xpath('//*[@src] | //a[@href] | //link[@href] | //source[@srcset]'):
        for attr in ['src','href','srcset']:
            raw=node.get(attr)
            if not raw:continue
            if attr=='srcset':raw=raw.split()[0]
            parts=urlsplit(raw)
            if parts.scheme or parts.netloc:continue
            if not parts.path:target=path
            else:target=(PUBLIC/unquote(parts.path).lstrip('/')) if parts.path.startswith('/') else path.parent/unquote(parts.path)
            if target.is_dir():target/= 'index.html'
            elif not target.is_file() and target.with_name(target.name+'.html').is_file():target=target.with_name(target.name+'.html')
            if not target.is_file():errors.append(f'{relative}: missing {raw}')
            elif parts.fragment and target.suffix=='.html':
                if not documents[target].xpath('//*[@id=$id]',id=parts.fragment):errors.append(f'{relative}: missing anchor {raw}')
            resources+=1
    # Owner rules (brief 14 Oct 2026): no people photos, no founder/biography, no '1000+ ha', no placeholder tiles
    page=path.read_text(encoding='utf-8')
    for banned in ['technical-service.webp','founder','Tchumburidze','ჭუმბურიძე','1000+','product-tile','CEO']:
        if banned in page:errors.append(f'{relative}: contains {banned!r} (not allowed by owner brief)')
    if not doc.xpath('//*[@data-i18n="dealer_line" or @data-i18n="about_intro"]') and path.name=='index.html':errors.append(f'{relative}: dealer line missing')
    if lang=='en' and re.search('[\u10a0-\u10ff]',doc.text_content()):errors.append(f'{relative}: Georgian text leaked into English')
    for key,label in [('ka','KA'),('en','EN'),('ru','RU')]:
        if not doc.xpath(f'//a[@data-lang="{key}"]'):errors.append(f'{relative}: missing {label} switch')
for css in PUBLIC.rglob('*.css'):
    for source in re.findall(r'url\([\'"]?([^\)\'\"]+)',css.read_text()):
        if source.startswith('data:') or '://' in source:continue
        if not (css.parent/source).is_file():errors.append(f'{css.relative_to(PUBLIC)}: missing CSS asset {source}')
font=TTFont(PUBLIC/'assets/fonts/D-DIN.woff')
if 0x10d0 in font.getBestCmap():errors.append('Unexpected D-DIN glyph coverage')
georgian=TTFont(PUBLIC/'assets/fonts/NotoSansGeorgian-400.woff2')
if not all(i in georgian.getBestCmap() for i in range(0x10d0,0x10f1)):errors.append('Missing Georgian glyphs')
for css in PUBLIC.rglob('*.css'):
    if re.search(r'letter-spacing:\s*-',css.read_text()):errors.append(f'{css.relative_to(PUBLIC)}: negative letter-spacing (owner: none)')
cyr=TTFont(PUBLIC/'assets/fonts/ibm-plex-sans-cyrillic-400-normal.woff2')
if not all(i in cyr.getBestCmap() for i in range(0x0410,0x0450)):errors.append('Missing Cyrillic glyphs')
for license_name in ['OFL-D-DIN.txt','OFL-NotoSansGeorgian.txt','OFL-IBMPlexSans.txt']:
    if not (PUBLIC/'assets/fonts'/license_name).is_file():errors.append('Missing '+license_name)
if errors:
    print('\n'.join(errors));raise SystemExit(1)
print(f'PASS: {len(files)} pages, {resources} local resource/anchor checks, complete ka/en/ru content, font files and licenses.')
