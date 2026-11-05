"""Regenerate self-contained language pages; no production build is needed."""
from pathlib import Path
import json
import re
import sys
from html import escape
from urllib.parse import urlsplit, urlunsplit
from lxml import html, etree
sys.path.insert(0, str(Path(__file__).resolve().parent))
from site_config import SOCIAL

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
    meta_key = template.get('data-meta')  # optional: a fuller search description than the short visible intro (ka/en/ru in content.js)
    ka_title = template.get('data-ka-title') or template.xpath('.//h1')[0].text_content()+' — საქართველოს პრემიუმ დრონები'
    page_head = re.sub(r'(<title data-i18n=")[^"]+(">).*?</title>', lambda m: m.group(1)+title_key+m.group(2)+escape(ka_title)+'</title>', head)
    _intro = template.xpath('.//p[contains(@class,"page-intro")]')
    # Pages without an intro paragraph (the compact platform page) take the Georgian description from content.js.
    intro = _intro[0].text_content() if _intro else json.loads((ROOT/'dist/assets/js/content.js').read_text(encoding='utf-8').split('=',1)[1].strip().rstrip(';'))['ka'][desc_key]
    if meta_key:
        intro = json.loads((ROOT/'dist/assets/js/content.js').read_text(encoding='utf-8').split('=',1)[1].strip().rstrip(';'))['ka'][meta_key]; desc_key = meta_key
    page_head = re.sub(r'<meta name="description"[^>]+>', '<meta name="description" content="'+escape(intro,quote=True)+'" data-i18n-content="'+desc_key+'">', page_head)
    page_head = re.sub(r'\s*<link rel="preload"[^>]*as="image"[^>]*>', '', page_head)
    body = ''.join(etree.tostring(child, encoding='unicode', method='html') for child in template)
    pages[template.get('data-page')] = '<!doctype html><html lang="ka" data-theme="light">'+page_head+'<body>'+skip+header+'<main id="main">'+body+'</main>'+footer+dialog+'</body></html>'

def clean_path(path):
    """Cloudflare Pages serves /shop.html as /shop (it redirects .html URLs), so link to the clean URL directly."""
    if path.endswith('/index.html'): return path[:-len('index.html')]
    if path.endswith('.html'): return path[:-len('.html')]
    return path

def pretty(href):
    parts = urlsplit(href)
    if parts.scheme or parts.netloc or not parts.path.endswith('.html'): return href
    return urlunsplit(('', '', clean_path(parts.path), parts.query, parts.fragment))

def page_path(filename):
    return '/' if filename == 'index.html' else '/' + clean_path(filename)

# Owner-verified facts only (14 Oct 2026): Tbilisi = storage and service by appointment (not a showroom, no opening hours);
# Lagodekhi = warehouse (in a village of the Lagodekhi area; no street address published) and field operations. No HQ claim.
# SEO brief 5 Nov 2026: PDG is its own business (seller of XAG products), named "PDG — Premium Drones Georgia" where a full name fits.
ORG = {"@context": "https://schema.org", "@type": "Organization", "name": "Premium Drones Georgia", "legalName": "Premium Drones Georgia LLC", "foundingDate": "2022", "alternateName": ["PDG — Premium Drones Georgia", "PDG", "საქართველოს პრემიუმ დრონები"],
       "description": "Premium Drones Georgia is the official and exclusive XAG dealer in the Caucasus region: XAG drones, batteries, chargers, generators, parts, service and training.",
       "url": BASE_URL + "/", "logo": BASE_URL + "/assets/img/pdg-logo-light.png", "image": BASE_URL + "/assets/img/og-image.jpg",
       "telephone": "+995550004333", "email": "info@premium-drones.ge",
       "location": [{"@type": "Place", "name": "Premium Drones Georgia, Tbilisi (storage and service, by appointment)",
                     "address": {"@type": "PostalAddress", "streetAddress": "12 Panaskerteli-Tsitsishvili St", "addressLocality": "Tbilisi", "postalCode": "0160", "addressCountry": "GE"}},
                    {"@type": "Place", "name": "Premium Drones Georgia, Lagodekhi (warehouse and field operations)",
                     "address": {"@type": "PostalAddress", "addressLocality": "Lagodekhi", "addressRegion": "Kakheti", "addressCountry": "GE"}}]}

# Breadcrumb parent of each inner page: (path, content key, Georgian name). Pages not listed sit directly under home.
_ART=('/blog','nav_blog','ბლოგი'); _P150=('/p150-max','nav_p150','XAG P150 MAX'); _SHOP=('/shop','nav_shop','მაღაზია'); _DR=('/drones','nav_drones','დრონები')
CRUMB_PARENT={'choosing-a-drone.html':_ART,'first-flight.html':_ART,'batteries-and-charging.html':_ART,'service-and-parts.html':_ART,
              'p150-max-starter.html':_P150,'p150-max-plus.html':_P150,'p150-max-pro.html':_P150,'p150-max-business.html':_P150,
              'b141050-battery.html':_SHOP,'cm13600s-charger.html':_SHOP,'gc4000-plus-generator.html':_SHOP,'battery-cooling-tank.html':_SHOP,
              'src5-remote-controller.html':_SHOP,'xrtk7-rtk-station.html':_SHOP,'xag-p100-pro.html':_DR,'xag-p100.html':_DR,'xag-v40.html':_DR}

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
        target_path=page_path(filename)
        element.set('href',target_prefix+target_path)
        if target==language:element.set('aria-current','page')
        else:element.attrib.pop('aria-current',None)
    for slot in doc.xpath('//div[contains(concat(" ",@class," ")," social-links ")]'):
        for child in list(slot): slot.remove(child)
        slot.text=None
        for name,url in SOCIAL.items():
            if url.strip():
                a=etree.SubElement(slot,'a',href=url.strip(),target='_blank',rel='noopener noreferrer'); a.text=name
    for element in doc.xpath('//a[@href]'):
        element.set('href', pretty(element.get('href')))
    # Remove any prior generated metadata so repeated generation is idempotent.
    for el in doc.xpath('//link[@rel="canonical" or @rel="alternate"] | //meta[@property="og:url"] | //meta[@name="robots"] | //script[@type="application/ld+json"]'):
        el.getparent().remove(el)
    # Product names (5 Nov 2026): the official XAG name joins the code line under the card title, and is dropped where it
    # repeats the title exactly (English pages), so a card reads: category, code · XAG name, title.
    for orig in doc.xpath('//*[contains(@class,"product-orig")]'):
        box=orig.getparent(); title=(box.xpath('./h3|./h1') or [None])[0]
        same=title is not None and ' '.join(title.text_content().split())==' '.join(orig.text_content().split())
        sku=(orig.xpath('ancestor::*[contains(@class,"product-body")][1]//p[contains(@class,"product-sku")]') or [None])[0]
        if same: box.remove(orig)
        elif sku is not None and title is not None and title.tag=='h3':
            sku.text=(sku.text or '').strip()+' · '+orig.text_content().strip(); box.remove(orig)
            # the code line goes under the title, so the card reads: category, title, code · XAG name
            link=title.getparent() if title.getparent() is not None and 'product-link' in (title.getparent().get('class') or '') else title
            sku.getparent().remove(sku); link.addnext(sku)
    doc_head=doc.find('head')
    path=page_path(filename)
    canonical=BASE_URL+prefix+path
    if filename in ('404.html','payment.html','account.html','p150-max-platform.html'):
        etree.SubElement(doc_head,'meta',name='robots',content='noindex')
    if filename=='404.html':
        pass
    else:
        etree.SubElement(doc_head,'link',rel='canonical',href=canonical)
        for target in ['ka','en','ru','x-default']:
            p='' if target in ['ka','x-default'] else '/'+target
            etree.SubElement(doc_head,'link',rel='alternate',hreflang=target,href=BASE_URL+p+path)
        etree.SubElement(doc_head,'meta',property='og:url',content=canonical)
    # Per-page share text (Facebook, WhatsApp, Telegram previews) = the page's own title and description.
    # Owner (19 Oct 2026): brand written 'Premium Drones Georgia' (not capitals); home = 'საქართველოს პრემიუმ დრონები • Premium Drones Georgia',
    # other pages start with 'Premium Drones Georgia — '.
    # Owner (19 Oct 2026, SEO brief): home = 'XAG საქართველო | Premium Drones Georgia' (page_title); every other page = '<topic> | Premium Drones Georgia'.
    t_el=doc.find('.//title')
    if t_el is not None and filename!='index.html':
        rest=re.sub(r'^(PREMIUM DRONES GEORGIA|Premium Drones Georgia)\s*[—|–-]\s*','',(t_el.text or '').strip())
        rest=re.sub(r'\s*[—|–-]\s*(PDG|საქართველოს პრემიუმ დრონები|Premium Drones Georgia|Премиум Дроны Грузии)\s*$','',rest)
        rest=re.sub(r'\s*[—|–-]\s*(მაღაზია|shop|магазин) PDG\s*$','',rest,flags=re.I)
        t_el.text=rest+' | Premium Drones Georgia'
    title_text=doc.findtext('.//title') or ''
    desc=(doc.xpath('//meta[@name="description"]/@content') or [''])[0]
    for m in doc.xpath('//meta[@property="og:title"]'): m.set('content',title_text); m.attrib.pop('data-i18n-content',None)
    for m in doc.xpath('//meta[@property="og:description"]'): m.set('content',desc); m.attrib.pop('data-i18n-content',None)
    for m in doc.xpath('//meta[@property="og:locale"]'): m.getparent().remove(m)
    etree.SubElement(doc_head,'meta',property='og:locale',content={'ka':'ka_GE','en':'en_US','ru':'ru_RU'}[language])
    # Share / search image (5 Nov 2026): a product, package or model page uses its own first photo; other pages the site image.
    own_img=(doc.xpath('//main//div[contains(@class,"pd-photo") or contains(@class,"pp-gallery") or contains(@class,"pd-gallery")]//img/@src') or [''])[0].split('?')[0]
    # Kept on the JPEG site image: WebP previews are not shown by every messenger (WhatsApp, Viber). Product photos are in the Product schema.
    og=BASE_URL+'/assets/img/og-image.jpg'
    for image in doc.xpath('//meta[@property="og:image"]'):image.set('content',og)
    graph=[]
    lp='' if language=='ka' else '/'+language
    if filename=='index.html':
        org=dict(ORG); org['@id']=BASE_URL+'/#business'
        org['sameAs']=[u for u in SOCIAL.values() if u.strip()]
        org['areaServed']={"@type":"Country","name":"Georgia"}
        # Owner, 19 Oct 2026: contact hours (Tbilisi time); visits only by appointment.
        org['contactPoint']={"@type":"ContactPoint","contactType":"customer service","telephone":"+995550004333","email":"info@premium-drones.ge",
            "availableLanguage":["ka","en","ru"],"areaServed":"GE","hoursAvailable":[
            {"@type":"OpeningHoursSpecification","dayOfWeek":["Monday","Tuesday","Wednesday","Thursday","Friday"],"opens":"09:00","closes":"21:00"},
            {"@type":"OpeningHoursSpecification","dayOfWeek":"Saturday","opens":"09:00","closes":"15:00"}]}
        # 5 Nov 2026: only what PDG actually sells and does (no other brands' models: PDG is an XAG dealer).
        org['knowsAbout']=["agricultural drones","drone crop spraying","drone granule spreading","drone field mapping","agricultural drone operator training",
                           "agricultural drone service and repair","XAG P150 MAX","XAG agricultural drone batteries, chargers and parts"]
        org['brand']={"@type":"Brand","name":"XAG"}
        org.pop('@context',None); graph.append(org)
        graph.append({"@type":"WebSite","@id":BASE_URL+'/#website',"url":BASE_URL+'/',"name":"Premium Drones Georgia",
                      "alternateName":["PDG — Premium Drones Georgia","PDG","საქართველოს პრემიუმ დრონები"],
                      "inLanguage":["ka","en","ru"],"publisher":{"@id":BASE_URL+'/#business'}})
    # BreadcrumbList (5 Nov 2026): home > section > page, from the site's real structure and the page's own h1.
    if filename not in ('index.html','404.html','payment.html','account.html','p150-max-platform.html'):
        h1=(doc.xpath('//h1') or [None])[0]
        name=re.sub(r'\s+',' ',h1.text_content()).strip().rstrip('.') if h1 is not None else title_text.split(' | ')[0]
        HOME={'ka':'მთავარი','en':'Home','ru':'Главная'}[language]
        crumbs=[(HOME,BASE_URL+lp+'/')]
        parent=CRUMB_PARENT.get(filename)
        if parent: crumbs.append((DICT[language].get(parent[1],parent[2]) if language!='ka' else parent[2], BASE_URL+lp+parent[0]))
        crumbs.append((name,canonical))
        graph.append({"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":i+1,"name":n,"item":u} for i,(n,u) in enumerate(crumbs)]})
    if True:
        faq=[{"@type":"Question","name":d.findtext('summary').strip(),"acceptedAnswer":{"@type":"Answer","text":d.findtext('p').strip()}} for d in doc.xpath('//details[contains(@class,"faq-item")]')]
        if faq: graph.append({"@type":"FAQPage","mainEntity":faq})
    # Product/Offer schema = exactly what the page shows: packages, and shop items that have their own photo.
    # Availability comes from each card (data-avail); quote-only parts and previous-generation models get no Offer.
    # 5 Nov 2026: packages include the RevoSpray 5 spraying system; RevoCast 5 (spreading) and RevoSling (cargo) are sold separately.
    KIT_DESC={"ka":"XAG P150 MAX სასოფლო-სამეურნეო დრონის კომპლექტი RevoSpray 5 შესაწამლი სისტემით, რუკის შედგენისა და შეწამვლისთვის. გრანულების გაფანტვის (RevoCast 5) და ტვირთის გადატანის (RevoSling) მოდულები იყიდება ცალკე.",
              "en":"XAG P150 MAX agricultural drone package with the RevoSpray 5 spraying system, for field mapping and spraying. RevoCast 5 spreading and RevoSling cargo modules are sold separately.",
              "ru":"Комплект сельскохозяйственного дрона XAG P150 MAX с системой опрыскивания RevoSpray 5 для картографирования и опрыскивания. Модули RevoCast 5 (разбрасывание) и RevoSling (перевозка грузов) продаются отдельно."}[language]
    AVAIL={'in_stock':'https://schema.org/InStock'}
    # Return policy = the terms page (terms_p5): 14 days, unused, complete, original packaging; contact first.
    # Return fees / method are not stated in the terms, so they are not claimed here.
    # Delivery (owner, 16 Oct 2026, terms_p4 + site_config.SHIPPING): fee under free_from GEL, free from it (one item = its own order value).
    import site_config as _sc
    def SHIP(price):
        rate=0 if float(price)>=_sc.SHIPPING['free_from'] else _sc.SHIPPING['fee']
        return {"@type":"OfferShippingDetails","shippingDestination":{"@type":"DefinedRegion","addressCountry":"GE"},
                "shippingRate":{"@type":"MonetaryAmount","value":rate,"currency":"GEL"},
                # Owner, 18 Oct 2026 (terms_p4): after confirmation, Tbilisi same or next day, regions 1-3 days.
                "deliveryTime":{"@type":"ShippingDeliveryTime","handlingTime":{"@type":"QuantitativeValue","minValue":0,"maxValue":0,"unitCode":"DAY"},
                                "transitTime":{"@type":"QuantitativeValue","minValue":0,"maxValue":3,"unitCode":"DAY"}}}
    lp='' if language=='ka' else '/'+language
    RETURNS={"@type":"MerchantReturnPolicy","applicableCountry":"GE","returnPolicyCategory":"https://schema.org/MerchantReturnFiniteReturnWindow",
             "merchantReturnDays":14,"merchantReturnLink":BASE_URL+lp+'/terms',
             # Owner, 18 Oct 2026 (terms_p5): returns at the Tbilisi storage or by courier; return shipping paid by the customer,
             # free when the item is faulty or wrong.
             "returnMethod":["https://schema.org/ReturnInStore","https://schema.org/ReturnByMail"],
             "returnFees":"https://schema.org/ReturnFeesCustomerResponsibility",
             "customerRemorseReturnFees":"https://schema.org/ReturnFeesCustomerResponsibility",
             "itemDefectReturnFees":"https://schema.org/FreeReturn"}
    PART_DESC={"ka":"XAG-ის ორიგინალი პროდუქტი XAG P150 MAX-ისთვის. მწარმოებლის კოდი: {}.","en":"Original XAG product for the XAG P150 MAX. Manufacturer code: {}.",
               "ru":"Оригинальный продукт XAG для XAG P150 MAX. Код производителя: {}."}[language]
    import product_pages as _pp
    def product(sku,name,price,img,avail,kit,url):
        if avail not in AVAIL or not price: return None
        # SEO brief 19 Oct 2026: an item with its own page (package, battery, charger...) points its Offer to that page and
        # shares that page's @id, so the shop / P150 MAX listings and the item page describe one product, not two.
        own=_pp.url(sku)
        pid=BASE_URL+'/shop#'+sku
        if own:
            url=BASE_URL+lp+own; pid=url+'#product'
        d={"@type":"Product","@id":pid,"name":name,"sku":sku,"mpn":sku if sku[:1].isdigit() else None,"brand":{"@type":"Brand","name":"XAG"},
           "image":BASE_URL+img if img.startswith('/') else img,"description":KIT_DESC if kit else PART_DESC.format(sku),
           "offers":{"@type":"Offer","price":price,"priceCurrency":"GEL","availability":AVAIL[avail],"itemCondition":"https://schema.org/NewCondition",
                     "priceSpecification":{"@type":"UnitPriceSpecification","price":price,"priceCurrency":"GEL","valueAddedTaxIncluded":True},
                     "url":url,"seller":{"@id":BASE_URL+'/#business'},"hasMerchantReturnPolicy":RETURNS,"shippingDetails":SHIP(price)}}
        if not d['mpn']: d.pop('mpn')
        if kit: d.update(category="Agricultural drone")
        return d
    if filename in ('shop.html','parts.html'):
        for card in doc.xpath('//article[contains(@class,"product")][@data-avail]'):
            kit='product-kit' in card.get('class','')
            img=(card.xpath('.//img/@src') or [''])[0]
            if not kit and not img.startswith('/assets/img/products/'): continue
            btn=(card.xpath('.//button[contains(@class,"add-btn")]') or [None])[0]
            if btn is None: continue
            d=product(btn.get('data-sku'),btn.get('data-name'),btn.get('data-price'),img,card.get('data-avail'),kit,canonical+('#kits' if kit else ''))
            if d: graph.append(d)
    for box in doc.xpath('//article[contains(@class,"pd-buybox") or contains(@class,"pp-buy")][@data-avail][@data-avail!="out"]'):
        # Product page (battery, charger, charging station): Offer only with the product's own photo (as on the shop page).
        img=box.get('data-img') or (doc.xpath('//div[contains(@class,"pd-photo")]//img/@src') or [''])[0]
        btn=(box.xpath('.//button[contains(@class,"add-btn")]') or [box])[0]  # platform page: data on the buybox itself (configurator is the buy path)
        if img.startswith('/assets/img/products/'):
            d=product(btn.get('data-sku'),btn.get('data-name'),btn.get('data-price'),img,box.get('data-avail'),box.get('data-cat')=='kit',canonical)
            if d: d['@id']=canonical+'#product'; d['description']=desc; graph.append(d)
    if filename=='p150-max.html':
        for btn in doc.xpath('//li[contains(@class,"pkg-tile")][@data-kit="1"]'):
            # 19 Oct 2026: image-led package listings; the platform listing links to its own page (its Offer lives there)
            d=product(btn.get('data-sku'),btn.get('data-name'),btn.get('data-price'),'/assets/img/products/'+btn.get('data-sku')+'.webp','in_stock',True,canonical+'#kits')
            if d: graph.append(d)
    if graph:
        ld=etree.SubElement(doc_head,'script',type='application/ld+json')
        ld.text=json.dumps({"@context":"https://schema.org","@graph":graph},ensure_ascii=False)
    return '<!doctype html>\n'+etree.tostring(doc,encoding='unicode',method='html',pretty_print=True)

import datetime, hashlib
today=datetime.date.today().isoformat()
# Truthful <lastmod> (5 Nov 2026): a URL's date changes only when what it says changes (title, description, main text, prices),
# not on every build. scripts/lastmod.json keeps {url: [content hash, date]}.
LASTMOD_FILE=ROOT/'scripts/lastmod.json'
try: LASTMOD=json.loads(LASTMOD_FILE.read_text(encoding='utf-8'))
except FileNotFoundError: LASTMOD={}
def content_hash(page):
    d=html.fromstring(page)
    parts=[d.findtext('.//title') or '']+d.xpath('//meta[@name="description"]/@content')
    parts+= [re.sub(r'\s+',' ',m.text_content()) for m in d.xpath('//main')]
    parts+= d.xpath('//main//button[@data-price]/@data-price')+d.xpath('//main//li[@data-price]/@data-price')
    return hashlib.sha256('\n'.join(parts).encode()).hexdigest()[:16]
for filename,page_source in pages.items():
    for language in ['ka','en','ru']:
        target=PUBLIC if language=='ka' else PUBLIC/language
        target.mkdir(exist_ok=True)
        out=render(page_source,language,filename)
        (target/filename).write_text(out,encoding='utf-8')
        key=('' if language=='ka' else '/'+language)+page_path(filename)
        h=content_hash(out)
        if LASTMOD.get(key,[None])[0]!=h: LASTMOD[key]=[h,today]
LASTMOD_FILE.write_text(json.dumps(dict(sorted(LASTMOD.items())),indent=0,ensure_ascii=False)+'\n',encoding='utf-8')
urls=[]
for filename in pages:
    if filename in ('404.html','payment.html','account.html','p150-max-platform.html'):continue
    path=page_path(filename)
    alts=''.join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{BASE_URL}{"" if l in ("ka","x-default") else "/"+l}{path}"/>' for l in ['ka','en','ru','x-default'])
    for language in ['ka','en','ru']:
        prefix='' if language=='ka' else '/'+language
        urls.append(f'<url><loc>{BASE_URL}{prefix}{path}</loc><lastmod>{LASTMOD.get(prefix+path,[0,today])[1]}</lastmod>{alts}</url>')
(PUBLIC/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">'+''.join(urls)+'</urlset>',encoding='utf-8')
# /api/ = server endpoints (payments, chat, accounts): nothing to index there.
(PUBLIC/'robots.txt').write_text('User-agent: *\nAllow: /\nDisallow: /api/\nSitemap: '+BASE_URL+'/sitemap.xml\n',encoding='utf-8')
print(f'Generated {len(pages)*3} pages in ka/en/ru, with canonical origin {BASE_URL}.')
