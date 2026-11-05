# SEO: search purpose per page (5 Nov 2026)

Rules: no keyword lists on pages, no hidden text, no near-identical pages for spellings or towns. Farmer spellings
(აგროდრონი, აგრო დრონი) appear only in search descriptions, meta keywords, site-search synonyms and FAQ wording.

| Search group | Page | Title / H1 / description carry |
|---|---|---|
| PDG, Premium Drones Georgia, საქართველოს პრემიუმ დრონები | / (home), /about, /consultation | "PDG — Premium Drones Georgia" in the home title; Organization + WebSite schema with alternate names |
| XAG, XAG საქართველო, XAG Georgia, XAG დრონები | /, /drones, /about | home title "XAG სასოფლო-სამეურნეო დრონები", /drones title "XAG სასოფლო-სამეურნეო დრონები საქართველოში" |
| აგრო დრონი, აგროდრონი, სასოფლო-სამეურნეო დრონი(ები) | /drones, /p150-max, /faq | H1 "სასოფლო-სამეურნეო დრონები"; descriptions with "აგროდრონი"; FAQ "რა არის აგროდრონი" |
| აგრო დრონის ფასი, სასოფლო-სამეურნეო დრონის ფასი, XAG P150 MAX ფასი, P150 MAX კომპლექტები | /shop (prices, configurator), /p150-max, package pages | /shop title "სასოფლო-სამეურნეო დრონის ფასი — XAG P150 MAX კომპლექტები", H1 "ფასები და კომპლექტაციები"; package descriptions = price incl. VAT + exact contents |
| XAG P150 MAX | /p150-max | title "XAG P150 MAX — ფასი და კომპლექტაციები საქართველოში" (unchanged) |
| XAG ნაწილები, XAG აკუმულატორები, SKU searches | /shop#parts, product pages (/b141050-battery …) | product descriptions = name, price incl. VAT, stock; every card shows the XAG manufacturer code |
| XAG სერვისი, აგრო დრონის შეკეთება | /service | H1 "XAG დრონების სერვისი და შეკეთება" |
| აგრო დრონის მართვის სწავლება | /academy | title "სასოფლო-სამეურნეო დრონის მართვის სწავლება — PDG აკადემია" |

Technical (build-pages.py): canonical = clean production URL (query strings such as ?c=, ?kit=, ?q=, utm_ are not indexed separately);
reciprocal hreflang ka/en/ru + x-default; previews on *.pages.dev send X-Robots-Tag: noindex; robots.txt disallows /api/;
sitemap lastmod changes only when a page's title, description, main text or prices change (scripts/lastmod.json);
BreadcrumbList on inner pages, WebSite + Organization on home; Offers carry priceSpecification valueAddedTaxIncluded = true.
Analytics events: call_click, whatsapp_click, messenger_click, email_click, chat_open = clicks; add_to_cart = cart intent;
whatsapp_order / email_order = order message opened (not a confirmed order); generate_lead = consultation form accepted by the server (a real lead).
