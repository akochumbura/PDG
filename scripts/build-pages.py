"""Regenerate self-contained language pages; no production build is needed."""
from pathlib import Path
import json
import re
import sys
from html import escape
from urllib.parse import urlsplit, urlunsplit
from lxml import html, etree

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / 'dist'
BASE_URL = sys.argv[1].rstrip('/') if len(sys.argv) > 1 else 'https://premium-drones.ge'
if not re.fullmatch(r'https://[a-zA-Z0-9.-]+(?::\d+)?', BASE_URL):
    raise ValueError('Supply a plain HTTPS origin.')
source = (PUBLIC / 'index.html').read_text(encoding='utf-8')
content = (PUBLIC / 'assets/js/content.js').read_text(encoding='utf-8')
DICT = json.loads(content.split('=', 1)[1].strip().removesuffix(';'))
templates = html.fromstring((ROOT / 'scripts/page-bodies.html').read_text(encoding='utf-8'))
header = re.search(r'<header class="site-header">.*?</header>', source, re.S).group()
footer = re.search(r'<footer class="site-footer">.*?</footer>', source, re.S).group()
dialog = re.search(r'<dialog .*?</dialog>', source, re.S).group()
head = re.search(r'<head>.*?</head>', source, re.S).group()
skip = re.search(r'<a class="skip-link".*?</a>', source, re.S).group()
pages = {'index.html': source}
for template in templates.xpath('//template[@data-page]'):
    title_key = template.get('data-title')
    desc_key = template.get('data-description')
    page_head = re.sub(r'(<title data-i18n=")[^"]+(">).*?</title>', r'\g<1>'+title_key+r'\g<2>'+escape(template.xpath('.//h1')[0].text_content())+' — Premium Drones Georgia</title>', head)
    intro = template.xpath('.//p[contains(@class,"page-intro")]')[0].text_content()
    page_head = re.sub(r'<meta name="description"[^>]+>', '<meta name="description" content="'+escape(intro,quote=True)+'" data-i18n-content="'+desc_key+'">', page_head)
    page_head = re.sub(r'\s*<link rel="preload"[^>]*as="image"[^>]*>', '', page_head)
    body = ''.join(etree.tostring(child, encoding='unicode', method='html') for child in template)
    pages[template.get('data-page')] = '<!doctype html><html lang="ka" data-theme="light">'+page_head+'<body>'+skip+header+'<main id="main">'+body+'</main>'+footer+dialog+'</body></html>'

def localized_href(href, language, filename):
    parts = urlsplit(href)
    if parts.scheme or parts.netloc: return href
    if href.startswith('#') and filename != 'index.html':
        return ('/' if language == 'ka' else '/'+language+'/') + href
    if not parts.path or parts.path.startswith('/assets/'): return href
    path = re.sub(r'^/(en|ru)(?=/|$)', '', parts.path)
    prefix = '' if language == 'ka' else '/'+language
    return urlunsplit(('', '', prefix+path, parts.query, parts.fragment))

def render(page_source, language, filename):
    doc = html.document_fromstring(page_source)
    doc.set('lang', language)
    if language != 'ka':
        translations = DICT[language]
        for element in doc.xpath('//*[@data-i18n]'):
            key = element.get('data-i18n')
            if key not in translations: raise ValueError(f'Missing {language}: {key}')
            for child in list(element): element.remove(child)
            element.text = translations[key]
        for attribute, target in [('data-i18n-alt','alt'),('data-i18n-aria','aria-label'),('data-i18n-placeholder','placeholder'),('data-i18n-content','content')]:
            for element in doc.xpath(f'//*[@{attribute}]'):
                key=element.get(attribute)
                if key not in translations: raise ValueError(f'Missing {language}: {key}')
                element.set(target,translations[key])
        for font in doc.xpath('//link[@as="font"]'):
            if language == 'en': font.set('href','/assets/fonts/D-DIN.woff');font.set('type','font/woff')
    for element in doc.xpath('//*[@data-local or @data-home] | //nav[@id="site-nav"]/a | //a[@class="header-contact"]'):
        element.set('href', localized_href(element.get('href','/'),language,filename))
    prefix='' if language=='ka' else '/'+language
    for element in doc.xpath('//*[@data-lang]'):
        target=element.get('data-lang')
        target_prefix='' if target=='ka' else '/'+target
        target_path='/' if filename=='index.html' else '/'+filename
        element.set('href',target_prefix+target_path)
        if target==language:element.set('aria-current','page')
        else:element.attrib.pop('aria-current',None)
    # Remove any prior generated metadata so repeated generation is idempotent.
    for el in doc.xpath('//link[@rel="canonical" or @rel="alternate"] | //meta[@property="og:url"]'):
        el.getparent().remove(el)
    doc_head=doc.find('head')
    path='/' if filename=='index.html' else '/'+filename
    canonical=BASE_URL+prefix+path
    etree.SubElement(doc_head,'link',rel='canonical',href=canonical)
    for target in ['ka','en','ru','x-default']:
        p='' if target in ['ka','x-default'] else '/'+target
        etree.SubElement(doc_head,'link',rel='alternate',hreflang=target,href=BASE_URL+p+path)
    etree.SubElement(doc_head,'meta',property='og:url',content=canonical)
    for image in doc.xpath('//meta[@property="og:image"]'):image.set('content',BASE_URL+'/assets/img/p150-max-flight.webp')
    return '<!doctype html>\n'+etree.tostring(doc,encoding='unicode',method='html',pretty_print=True)

for filename,page_source in pages.items():
    for language in ['ka','en','ru']:
        target=PUBLIC if language=='ka' else PUBLIC/language
        target.mkdir(exist_ok=True)
        (target/filename).write_text(render(page_source,language,filename),encoding='utf-8')

urls=[]
for filename in pages:
    path='/' if filename=='index.html' else '/'+filename
    for language in ['ka','en','ru']:
        prefix='' if language=='ka' else '/'+language
        urls.append('<url><loc>'+BASE_URL+prefix+path+'</loc></url>')
(PUBLIC/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(urls)+'</urlset>',encoding='utf-8')
(PUBLIC/'robots.txt').write_text('User-agent: *\nAllow: /\nDisallow: /status.html\nSitemap: '+BASE_URL+'/sitemap.xml\n',encoding='utf-8')
print(f'Generated {len(pages)*3} pages in ka/en/ru, with canonical origin {BASE_URL}.')
