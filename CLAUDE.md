# Premium Drones Georgia

Read PROJECT_MEMORY.md before editing. Keep this project buildless: HTML, CSS,
vanilla JavaScript and self-hosted font/photo assets. Preserve the owner's supplied
logo exactly. Georgian source is UTF-8 in dist/index.html and scripts/page-bodies.html;
English and Russian counterparts belong in dist/assets/js/content.js. Regenerate
and check everything with `python scripts/build.py`. Publish only dist. Update project memory
and stage documentation after significant changes. The consultation form is server-side (docs/12-consultation-form.md): say "received" only after the server
accepts it; before RESEND_API_KEY exists requests only land in /api/contact/inbox. The separately referenced FastAPI project was not included.

## Workflow (updated 14 Oct 2026: shop, 3 languages, premium-drones.ge on Cloudflare Pages)
- Domain premium-drones.ge (DNS on Cloudflare); contact info@premium-drones.ge; WhatsApp/phone +995 550 00 43 33.
- Rebuild and verify EVERYTHING with `python scripts/build.py` (shop cards + P150 kit table from catalog.csv/pricing.py,
  then pages, then checks). Never hand-edit generated dist/*.html except dist/index.html (source of the Georgian home page).
- Hosting is Cloudflare Pages: it serves /shop.html as /shop. The build writes clean URLs (no .html) in links,
  canonicals and the sitemap; verify fails on any internal .html link. 404.html exists per language (noindex).
  Local preview that behaves the same: `python scripts/serve.py`.
- Prices (owner, 14 Oct 2026): the shop = the owner's price list PDG_XAG_Complete_Item_Price_List_With_Margins.xlsx (268 items,
  sheet "Full Item Price List", Retail incl. VAT GEL) imported into scripts/catalog.csv by scripts/import-price-list.py (SKU = XAG manufacturer code
  "მწარმოებლის კოდი" e.g. 09-017-00073, looked up from the invoice Code P0000… in scripts/supplier-code-map.csv, made from
  PDG_Invoice_Packing_List_Georgian.xlsx; never show the P0000 codes; name = Original item, name_ka = Georgian item). Cost/margin columns are internal and never published. A new list: rerun the import.
  Prices show only the ₾ sign; no "prices in GEL / ლარში / в лари" texts anywhere (owner).
- Packages (owner, 14 Oct 2026 night, LATEST APPROVED, exact contents): Starter 75,999 = drone (RevoSpray 5), SRC5 remote,
  4 B141050 batteries, 2 CM13600S chargers, 2 battery cooling tanks ("cooling tanks"). Pro 87,999 = Starter + 2 batteries (6) + XRTK7.
  Business 104,999 = Pro with 8 batteries and 4 chargers. Contents = catalog columns (drones, remotes, batteries, chargers, towers, rtk).
  No ACS4 control stick in any package (the handheld item in the XAG combo picture is the XRTK7).
  Each package has its own page (/p150-max-starter, -pro, -business): first picture = combo picture with exactly those contents
  (dist/assets/img/products/PDG-P150MAX-*.webp, made by scripts/tools/package-pictures.py), then the P150 MAX gallery.
- Spraying (owner brief 14 Oct 2026): headings use შესხურება, explanatory text uses შეწამვლა; combined line
  "ზუსტი შესხურება / შეწამვლა რეალურ საველე პირობებში." Experience: "thousands of hectares in real field conditions"
  (optional quiet "2,900+ ha in the 2026 season"); never "1000+ ha". Worked with XAG V40, P100, P100 Pro; focus P150 MAX.
  Locations: Tbilisi = storage and service (Panaskerteli-Tsitsishvili St 12, by appointment, not a showroom);
  Lagodekhi = warehouse and field operations. No hidden SEO text; model names only in meta/structured data/llms.txt.
- Model range on home: P150 MAX available; P100 Pro 72,500 / P100 70,220 (drone + 4 batteries), V40 38,500 (drone + 2)
  are out of stock and show "Last package price".
- Product photos: dist/assets/img/products/<SKU>.webp is picked up at build time. Until then EVERY product card (packages too)
  shows the official XAG logo (owner, 14 Oct 2026). Never show a photo of a different product on a part card (verify enforces this).
- No people or faces in any photo, no founder name, no CEO, no personal biography (verify blocks technical-service.webp,
  'founder', 'CEO', '1000+'). Product and equipment photos only; no DJI images in XAG sections; no AI images.
- No negative letter-spacing anywhere (verify enforces); no decorative gradients; no loud badges.
- P150 MAX specs on the site are from xa.com/en/p150max/p150maxspecs (Oct 2026). Do not add unverified specs.
  Full spec table ("მახასიათებლები", 109 rows, ka/en/ru) lives in scripts/p150_specs.py, built by scripts/build-specs.py.
- Every new UI string needs ka (in the HTML), en and ru keys in dist/assets/js/content.js.
- Payments: Bank of Georgia via dist/_worker.js, PAUSED and not live (see docs/07-payments.md). Never claim a payment succeeded
  unless the bank receipt says completed. Under 20,000 GEL full payment, from 20,000 GEL deposit + bank transfer.
- Server part: dist/_worker.js is GENERATED from scripts/worker.template.js by build-shop.py (prices + chat knowledge
  from the catalog). /api/*: payments (docs/07), AI chat (docs/10), accounts (docs/11). Each stays off until its
  Cloudflare secret/binding exists. Header: Home + Products/Services/Media (blog, gallery) mega menu, search (scripts/build-search.py), account, cart.
- Home page must stay short and simple (owner): hero, dealer line, key specs, ecosystem, packages, contact. Detail lives on other pages.
- Fonts: D-DIN (Latin, like xa.com), Noto Sans Georgian, IBM Plex Sans (Cyrillic). Keep font licences in dist/assets/fonts.
  Header logo = "PDG ~ XAG" lockup: official XAG vector logo (dist/assets/img/xag-logo.svg / xag-logo-white.svg, from xa.com) + dash + PDG logo.
  Logo: pdg-logo-light.png / pdg-logo-dark.png are transparent cut-outs of the supplied logo (owner asked for this);
  header, footer and logo follow the light/dark theme (default = phone setting).
- Dealer claim, exact owner wording only: "Premium Drones Georgia is the official and exclusive XAG dealer in the Caucasus
  region." (ka/en/ru key dealer_line). Make no other official claims.
- E-mail on the site: only info@premium-drones.ge.
- Company name in Georgian text is "საქართველოს პრემიუმ დრონები" (owner, 14 Oct 2026); Latin "Premium Drones Georgia" in en/ru,
  the logo and structured data (with alternateName).
- E-mail DNS records in Cloudflare must not be removed (docs/09-email.md).

## Wording and SEO (2026-10-14)
- Visible Georgian wording: "სასოფლო-სამეურნეო დრონი/პლატფორმა", "შეწამვლა" (never "შესხურება"), "გრანულების გაფანტვა", "ტვირთის გადატანა". Do not show "აგრო დრონი" on pages.
- Farmer search words (შეწამვლა, აგროდრონი, აგრო დრონი, შესაწამლი დრონი…) live only in meta keywords, search synonyms (scripts/build-search.py) and FAQ wording — never as visible keyword lists.
- P150 MAX positioning: world-class flagship agricultural platform for spraying, granule spreading, cargo transport and field mapping
  (owner, 15 Oct 2026: mapping must be visible — home 4th card 'რუკის შედგენა' 30 ha per flight (owner 15 Oct: mapping up to 30 ha; droplet 60~1500 µm; 20 m/s = 72 km/h exact; warranty = official XAG 1 year, batteries 1 year or 1500 cycles); maps by itself with its camera, built-in AI recognises obstacles).
- GC4000+ photo = owner-supplied render (09-017-00109.webp). The dimension drawing he sent (RevoSpray 4 / RevoCast 4 / RealTerra 3, 3118×3110 mm) is the P100 Pro, NOT the P150 MAX: not used on P150 MAX pages.
- Header: language dropdown (#langBtn/#langList), About us in the top menu, light theme by default.
- Chat = website conversation first (stored in PDG_DATA, team answers at /api/chat/inbox). AI: OpenAI (OPENAI_API_KEY, CHAT_MODEL gpt-6-luna,
  CHAT_EFFORT medium in Cloudflare) or Anthropic; answers every message, pauses 30 min after a team reply, learns from team replies. No subtitle in
  the chat header (owner). AI explains why PDG chose XAG (since 2007, global leader, No.1 patent holder per XAG, next-gen; comparative part = "we believe"). WhatsApp / Messenger / Call are secondary, shown after the first message. Keep the small "replies are generated by AI" note when AI is on.
- P150 MAX: 80 L tank, 32 L/min (two pumps), 46 L/min with the XAG 4-Nozzle Upgrade Kit (orchards and vineyards), 115 L granule container, 80 kg payload.
- No calculator page (removed on request).
- Site is published by pushing to GitHub akochumbura/PDG (main); Cloudflare Pages project "pdg" builds with `pip install lxml && python3 scripts/build.py`, output `dist`.
- P150 MAX facts (owner + xa.com/en/p150max): 80 L tank, 32 L/min (2 pumps), 46 L/min with the 4-Nozzle Upgrade Kit (recommended for orchards and vineyards), granule container 115 L (owner confirmed; not 120), 300 kg/min, 9 m spread width, 80 kg payload, 20 m/s, RealTerra mapping up to 30 ha/flight (owner), 4D radar 1.5–100 m, B141050 1050 Wh / 1500 cycles, IPX6K.
- No calculator page (removed by owner request).

## Catalog, stock and shop rules (owner brief 14 Oct 2026, evening)
- Parts PDFs (AgriFuture XAG P150 Max category pages) use XAG part numbers; the invoice uses P0000… codes: NO exact SKU overlap.
  scripts/pdf-part-matches.csv records every PDF part: A = identical official name, one-to-one (photo attached to the invoice item),
  A-model = same model code (CM13600S), B = ambiguous, C = probable duplicate (not added), D = not in invoice (added as quote-only).
  Never attach a picture shared by several part numbers, placeholders or drawings. Do not match by similar names.
- catalog.csv column avail: '' = price-list item (shown "საწყობშია"; quantities in scripts/stock.csv from the packing list),
  quote = no approved price ("ფასი მოთხოვნით" + WhatsApp quote, never in cart/checkout), legacy rows come from scripts/legacy_models.py
  (P100 Pro, P100, V40: "არ არის მარაგში" + consultation, no price, no Offer schema; specs from xa.com spec pages; owner photos XAG-*.webp).
- Quantity steppers on cards, kit table and cart (positive whole numbers; data-max only when a verified stock limit exists).
- P150 MAX configurator (P150 MAX page, built by build-shop.py): presets = package rows; extras = B141050, CM13600S, XRTK7, GC4000+
  at their shop price; fewer components than the preset = "ფასი მოთხოვნით". WhatsApp message + add to cart.
- Header: PDG logo first, then XAG logo, equal containers. Home dealer line uses the XAG logo image. About page has "XAG-ის შესახებ" (xa.com, no claims).
- Mobile bar (≤768px): call + chat (see 15 Oct additions), safe-area aware. Chat: one-line welcome, 4 quick actions, 1–3 sentence answers.
- Schema: Organization with Tbilisi + Lagodekhi locations (no HQ or village address; contactPoint hours = owner 19 Oct 2026: Mon–Fri 09–21, Sat 09–15, Sun closed; visits by appointment only, footer contact_hours + visit_note); Product/Offer only for in-stock priced items
  with own photo + packages; quote-only and previous models have no Offer. verify-site.py blocks ₾0 cart buttons, bad tel links, cost data.

## Logos and home hero (owner, 14 Oct 2026, late)
- Logo colours = official XAG file (xa.com xag-icon.svg): black #3D3C38, red #CC0000. pdg-logo-light.png / pdg-logo-dark.png and the
  app icon / favicon were recoloured to exactly these values (dark version: #F4F3EF + #CC0000). pdg-logo.png = untouched original.
- Header: PDG ~ XAG (literal "~", equal logo heights). Strip below the hero: PDG ~ XAG (owner 15 Oct: PDG first, like the header) (literal "~"), then exactly
  "საქართველოს პრემიუმ დრონები არის XAG-ის ოფიციალური და ერთადერთი დილერი კავკასიაში." (key dealer_strip). No extra slogans.
- Hero (owner, 14 Oct 2026 final): photo as before, text on the LEFT, centred vertically: small bold tagline
  "სწრაფი, ზუსტი, საიმედო" (hero_tagline) above "XAG P150 MAX" in Barlow Bold (OFL, self-hosted), then sentence and buttons.
  Do not redesign the hero.

## STATUS — 2026-10-14 (read this first in a new chat)
Live: premium-drones.ge on Cloudflare Pages project "pdg" (account ako.chumburidze@gmail.com), auto-deploys from GitHub akochumbura/PDG main.
Build: dist/ is built locally with `python3 scripts/build.py` and COMMITTED; on Cloudflare (CF_PAGES set) build.py exits at once and dist/ is published as is.
www/http → https://premium-drones.ge: ONE Redirect Rule, target concat("https://premium-drones.ge", http.request.uri), 301 (fixed 19 Oct 2026; never wildcard_replace on "https://www.*" — it looped for http://www). Details: docs/08-go-live-cloudflare.md.
Owner is non-technical, works from iPhone/Windows; wants Claude to do Cloudflare steps for him (use the desktop-app browser when available).

TODO in Cloudflare (dashboard, owner's account):
1. DONE 14 Oct 2026: KV binding on pdg Production = variable name "PDG" -> KV namespace "PDG_DATA" (id 8cd5cc39…).
   The worker accepts PDG_DATA, ORDERS or PDG as the variable name (kv() in scripts/worker.template.js).
   Check bindings per deployment: Deployments → Details → Functions → "KV namespace bindings" (Variable name column).
2. DONE: Secret ADMIN_KEY exists (owner set the value). Team inbox: https://premium-drones.ge/api/chat/inbox?key=ADMIN_KEY
   Check: https://premium-drones.ge/api/chat/config must show "live":true.
3. Optional WhatsApp alert (CallMeBot): secrets WHATSAPP_ALERT_PHONE (+995550004333) and WHATSAPP_ALERT_KEY (from CallMeBot after sending "I allow callmebot to send me messages").
4. After adding bindings/secrets: Deployments → ⋯ → Retry deployment.
6. AI replies: owner must create ANTHROPIC_API_KEY (console.anthropic.com, set a monthly limit) and add it as a Secret on pdg, then redeploy. AI answers all messages, pauses 30 min after a team reply, learns from team replies (KV learn:index). Greeting = "გამარჯობა! რით შეგვიძლია დაგეხმაროთ?" (owner: no "ჩვენი გუნდი გიპასუხებთ ამავე ჩატში").
7. Inbox: open /api/chat/inbox without ?key — sign-in box.
5. Later: Bank of Georgia e-commerce agreement → secrets BOG_CLIENT_ID, BOG_CLIENT_SECRET (payments). Optional ANTHROPIC_API_KEY for AI replies in chat.
Pending from owner: product photos (no people), BOG agreement, deposit % (10% assumed), other payment options (asked: TBC, installments, invoice?).

## Manufacturer codes, photos, product pages (owner, 14 Oct 2026, night)
- Every SKU on the site = XAG manufacturer code (packing list column "მწარმოებლის კოდი"); 268 invoice codes map one-to-one.
- (owner, 16 Oct 2026; replaces 'drone only in packages') The P150 MAX drone (09-007-00188) is ALSO sold as the standalone platform, 41,999 GEL (price list),
  RevoSpray 5 only — no SRC5, batteries or chargers. The packages stay unchanged. See the 16 Oct platform notes below.
- Product photos = the parts PDFs, matched by EXACT manufacturer code (scripts/pdf-part-matches.csv). A picture shared by
  different part numbers (screw kits, CW/CCW gaskets, 1&2 / 3&4 cables) is never used; one shared only by versions of the same
  part (same name) is. Exception: B141050 picture = PDF code 09-017-00083 (INTL) for invoice 09-017-00073 (same model).
  Many PDF parts have no picture in the PDF (blank lazy-loaded image): those keep the XAG logo.
- Product pages (scripts/product_pages.py → build-products.py): /b141050-battery, /cm13600s-charger, /gc4000-plus-generator,
  specs from p150_specs.py 'power'. Cards, home part list and search open them. Only items with verified xa.com specs get a page
  (B13970S: no verified specs, no page).
- Page titles (owner SEO brief, 19 Oct 2026 evening; replaces "titles start with Premium Drones Georgia —"): "<topic> | Premium Drones Georgia" (build-pages.py adds the suffix); never all capitals.
- Logo lockups (owner, 14 Oct 2026 night): the XAG logo is exactly the height of the whole PDG logo (incl. the PREMIUM DRONES
  GEORGIA line), aspect ratios kept, centred; header = PDG ~ XAG with a literal "~", strip = PDG ~ XAG; "~" in --xag-black. build.py adds ?v=hash to /assets/img URLs so changed logos/photos reach visitors at once.
- Home hero (owner, 14 Oct 2026 night): heading, sentence and buttons at the top with equal gaps (32px desktop, 24px phone);
  the whole drone must stay visible (wide screens: photo right of the text, hero ≤ 56vw tall; ≤1240px: text above the full photo).
- Home page <title> + share preview (owner final brief, 19 Oct 2026, overrides earlier) = exactly "Premium Drones Georgia | XAG P150 Max" in ka/en/ru. Brand text is never written in capitals (the logo image is unchanged).
- (owner, 14 Oct 2026, 23:15) Parts not on the packing list (avail=quote) = "არ არის მარაგში" + price on request (not "მარაგი დაზუსტდება").
  Screws and similar fasteners = 5-15 GEL by invoice landed cost (cost x 2.5 + 3.5, clamped; import-price-list.py: 02-004-*, nut/bolt/circlip, M-size gaskets).
  Package contents link to their pages: drone → /p150-max, SRC5, B141050, CM13600S, cooling tank, XRTK7 (product_pages.py).
  Parts list has sorting (recommended / price ↑ / price ↓ / name) and min / max price.
- Phone menu (owner, 15 Oct 2026): while open, the page behind is locked (html/body.nav-lock) and the menu scrolls by itself; closing restores the scroll position.
- (owner, 15 Oct 2026) RevoSling 05-002-02682 + Landing Gear 05-002-02683 = ONE system: one shop item 05-002-02682, price = sum (₾3,498),
  merged by import-price-list.py (MERGE). Configurator extras also include RevoCast 5 spreader (09-023-00145) and the RevoSling system (max 1 each).

## 15 Oct 2026 (morning) additions
- Purchasing today: cart -> WhatsApp/e-mail -> PDG confirms -> invoice -> bank transfer. Online card payment is off; terms (terms_p2/p3/p5/p7) describe that, the card/deposit paragraph (#termsOnline, terms_online) and cart pay/deposit notes appear only when /api/payments/config says enabled. Chat knowledge says online payment is NOT available.
- Mobile (<=768px): bar = "დარეკვა" (tel) + "მოგვწერეთ" (data-chat-open, opens chat; falls back to /consultation without JS). Chat bubble hidden on phones, bar hidden while chat is open, chat panel follows visualViewport (keyboard). Desktop keeps the bubble.
- Security: build.py writes CSP (script hashes of the inline theme script) + HSTS into dist/_headers; worker adds nosniff/HSTS/CSP on /api responses, bounded body reads, KV hourly/daily chat, live-chat and registration limits, constant-time admin key check.
- Home strip: PDG ~ XAG, dealer sentence, small xag_intro line, link "XAG-ის შესახებ →" to /about#about-xag.
- (owner, 15 Oct 2026) Everything on the price list is in stock (nothing sold yet); quantities: see STOCK below. Deposit 10% for orders from 20,000 GEL is the confirmed policy (applies once online payment is live; today the site only takes WhatsApp/e-mail orders). "Use official photos": xa.com is not reachable from the build environment, so official photos must be supplied as files (dist/assets/img/products/<SKU>.webp; legacy models P100 Pro / P100 / V40 need their own images).
- (owner, 15 Oct 2026) STOCK = scripts/stock.csv, quantities from the NIK Electronics packing list Shipment-0060920 (all 266 shop parts + 10 drones; nothing sold yet). build-shop.py sets max on every qty input (packages = complete sets the stock allows), configurator max, and the worker rejects orders above stock (CATALOG[sku][2]). After sales, update stock.csv. Limits are per item, not shared across package + loose parts.
- (owner, 15 Oct 2026) Legacy model photos supplied by the owner: XAG-P100.webp (flying), XAG-V40.webp (on grass), XAG-P100PRO.webp (studio render). Not used: a P100 expo photo with a person in it (no people in photos) and a second V40 close-up.
- (15 Oct 2026, full-site audit) Cart drawer scrolls as one piece and shows names in the visitor's language (pn_ keys incl. ka);
  product/package pages carry stock max; product page h1 = short name (pd_<slug>_h1); Russian texts use the Latin "Premium Drones Georgia";
  catalog names normalised "Station (INTL)"; hero image recompressed (q82) and preloaded per viewport; search ranks items with their own page first;
  terms/payment pages styled; quote-only cards wrap; tap targets ≥40px on phones (footer, back links, logo); hero scroll hint removed.
- (owner, 15 Oct 2026) Feature ORDER everywhere: mapping, spraying, spreading, cargo (home cards + title, hero sentence, P150 MAX chapters 01 RealTerra..04 RevoSling, stats strip, meta descriptions, chat prompt). Keep this order in new texts.
- (owner, 15 Oct 2026) Previous models P100 Pro / P100 / V40 have own pages (/xag-p100-pro, /xag-p100, /xag-v40) with photo galleries (dist/assets/img/models/, made by scripts/tools/model-pictures.py; legacy list in product_pages.py LEGACY). No price, no Offer schema. The P100 expo photo is cropped so no person shows. More photos: add to LEGACY pics + the tool script.
- (16 Oct 2026, Search Console merchant listings) Every Product has a description and every Offer has itemCondition New + hasMerchantReturnPolicy
  (14 days, GE, link to /terms, from terms_p5; no return fee/method claimed) + shippingDetails (GE, ₾30 if the item is under ₾100, else ₾0).
- (owner, 16 Oct 2026) Delivery in Georgia: ₾30 for orders under ₾100, free from ₾100; pickup from Tbilisi storage free (site_config.SHIPPING).
  Cart has a delivery/pickup choice + products/delivery/total lines; the worker adds the same fee as a DELIVERY basket line (server rule, not the browser's).
  terms_p4 (ka/en/ru) states the rule in words: if SHIPPING changes, update terms_p4 too.
- (owner, 16 Oct 2026, second brief — replaces the first platform notes) One purpose per page: /p150-max = model presentation (NO configurator;
  one link under the intro "კონფიგურაციის აწყობა — ₾41,999-დან" + note, generated at <!--platformLink-->); /p150-max-platform = the ONLY configurator;
  /shop = catalog (one .platform-row ABOVE the 3 packages, owner 17 Oct 2026). Platform page first screen: gallery left (object-fit contain, whole drone; owner front render +
  field photo via scripts/tools/platform-pictures.py, which also makes products/thumbs/<sku>.webp), right: XAG P150 MAX, "სასოფლო-სამეურნეო დრონი · RevoSpray 5",
  price incl. VAT, calm notice pp_notice, stock, one primary CTA, subordinate links; SKU in the details list. Mobile: name, image, price, action.
  Configurator (scripts/configurator.py + shop.js #platformConfig): presets (მხოლოდ პლატფორმა / Starter / Pro / Business), core rows visible
  (SRC5, B141050, CM13600S, cooling tank), 'დამატებითი აღჭურვილობა' always visible (owner 17 Oct 2026; GC4000+, XRTK7, RevoCast 5, RevoSling, 4-Nozzle kit).
  Pricing is AUTOMATIC: lowest of item-by-item and (package + extras) for every package fully contained; at most one package; no switch button,
  no comparison cards; note "გამოყენებულია {name} კომპლექტის ფასი". Summary, mobile bar, cart (package SKU + extras) and WhatsApp use one state.
  Links: ?c=batteries-4_chargers-2 and package pages' ?kit=starter (now pointing to /p150-max-platform). Mobile bar replaces the call/chat bar
  (body.pcfg-bar-on) while options are on screen and the summary total is not. Verified totals: 41,999 / 46,998 / 75,999 / 87,999 / 104,999 /
  79,998 / 87,997 / 99,797 / 116,797.
- (owner, 18 Oct 2026) Platform-only listing is FIRST wherever the packages are: shop (.platform-row), home (<!--homePlatform--> above #homePackages),
  P150 MAX page kit table (platform_kit_row, links to the configurator; no cart button/Offer there). Configurator extras include the 90 W LED headlight (09-027-00003).
  Return policy (terms_p5 + schema): 14 days; Tbilisi storage drop-off or courier; return shipping paid by the customer, free if faulty/wrong item
  (returnFees CustomerResponsibility, itemDefectReturnFees FreeReturn, returnMethod InStore+ByMail). Delivery (terms_p4 + schema deliveryTime):
  after confirmation Tbilisi same/next day, regions 1-3 days (handling 0, transit 0-3). No reviews/aggregateRating: never invent reviews.
- (owner, 18 Oct 2026) Alerts via Telegram (CallMeBot had no free slots): secret TELEGRAM_BOT_TOKEN only; the chat id is captured by
  /api/telegram/setup?key=ADMIN_KEY (stored in KV tg:chat; TELEGRAM_CHAT_ID still overrides). tgSend() is used by chat and consultation alerts. Steps: docs/10-ai-chat.md.
- (owner, 18 Oct 2026) Chat AI: never "შესხურება" in any form, always "შეწამვლა" (rule in chatSystem). The word stays only in meta keywords /
  search synonyms (what farmers type). Chat alerts now fire on every visitor message, max one per conversation per minute (th.alertAt).
- (owner, 18 Oct 2026) Georgian: "მინდორი / მინდორზე / მინდვრის" everywhere instead of "ველი / ველზე / საველე" (form-field texts form_check /
  error_required keep "ველი" = input field). Battery texts: no "1500 ციკლამდე" / cycle-life claim; only the warranty "1 წელი ან 1500 ციკლი" stays
  (P150 MAX power chapter stat "ციკლი 1500" removed). The chat AI follows both rules (chatSystem).
- (owner, 18 Oct 2026) Person requests: instant hand-off text (HANDOFF ka/en/ru) + waiting list (th.wait), AI silent until a team reply; never
  "PDG გუნდი ამ ჩატს კითხულობს". Two-way Telegram: owner replies to an alert → teamAnswer() posts it to the website chat (docs/10-ai-chat.md).
  LED headlight photo = owner render (products/09-027-00003.webp).
- (owner, 18 Oct 2026) About page XAG model range: P100 Pro / P100 / V40 cards show their first gallery photo (models/*-1.webp) and link to their pages.
- (owner, 19 Oct 2026) About "XAG-ის შესახებ": XAG = "მსოფლიო ლიდერი" / "world leader" (never "largest"); patents only as "according to XAG"; goal = agricultural infrastructure for the next 100 years (owner sentence).

## Audit 19 Oct 2026 (owner brief)
- Short Georgian product names: scripts/display_names.py (short_ka + OVERRIDES) used by build-shop (cards, cart, chat) and build-search;
  catalog.csv keeps the full price-list name (searchable via data-k on cards and the search keywords). Internal supplier notes are stripped.
- Copy: P150 MAX speed 20 m/s = 72 km/h (exact). "4-საქშენიანი განახლების კომპლექტი (იყიდება ცალკე)" — never "additional 4 nozzles".
  Pumps = "იმპელერიანი ტუმბო" (not "მოქნილი ტუმბო"). RevoCast 5 and RevoSling are always marked optional ("იყიდება ცალკე") near capability texts.
  Max values are manufacturer figures (note on the P150 MAX page). Company facts: founded 2022, field work since 2023.
- About: company story once (about-story + facts row with hectares and locations); models section heading "XAG-ის დრონები", P150 MAX card
  (available, in stock) first, then label "წინა თაობის მოდელები — მარაგში აღარ არის" and the 3 old-model cards. Every section must deliver what its heading says.
- Service / Academy: 3-step "how it works" (.order-steps), CTA to /consultation?topic=service|academy; no invented durations, prices, warranty or turnaround.
- Phone menu: body pinned with position:fixed at the scroll offset, scroll restored on close (script.js lockPage).
- Tools: scripts/tools/set_text.py sets a key in ka (HTML) + en/ru (content.js).

## Brief 2, 19 Oct 2026 (night)
- Configurator state lives in the URL (?c=…, shop.js pcRemember via history.replaceState); language links are rebuilt on click (script.js langHref),
  so a selection survives ka/en/ru switches. Verified: Pro + 2 GC4000+ = 99,797 in all three languages.
- Home hero: tagline, XAG P150 MAX, "სასოფლო-სამეურნეო დრონი" (also on desktop), feature sentence, hero_local line (desktop), primary red
  "ფასები და კომპლექტაციები" → #packages, secondary "კონსულტაცია". Phone: tagline, title, kind, primary button only.
- Home "რატომ PDG?" (#why-pdg) right before #packages: team trained at XAG Academy (China), field work since 2023, local stock, support after purchase.
  Never say training/repair/support is free or included. Home XAG strip line = owner sentence (xag_intro, 19 Oct 2026).
- Package comparison (build-shop compare(): only differing columns + "all three include" line + GC4000+ sold separately / suitable power source note):
  home (<!--homeCompare-->) and P150 MAX page (#compare, <!--pmCompare-->) before the technical chapters; P150 MAX hero has section links.
- Menu: no "XAG მოდელების ხაზი" entry (/about#models anchor kept); P150 promo → /p150-max#kits; "კონფიგურაციის აწყობა" link added.
  About model cards: no historical package prices (shop legacy cards unchanged).
- Honeypot wrapper: aria-hidden + inert. About/Academy/Service mention XAG Academy training, XAG trainer / technician qualifications in the team
  (owner statement; exact certificate names still to be confirmed).
- (owner, 19 Oct 2026, 02:30) Package comparison v2: NO "ყველა კომპლექტში შედის" line and NO generator note in it (that belongs in the configurator, kit photos and
  descriptions). Only Starter / Pro / Business, batteries, chargers, RTK (— when not included), price, "კომპლექტაციის ნახვა". Desktop table, phone = 3 stacked
  cards; Pro accented in red. Package contents labels are the short names (XAG SRC5 მართვის პულტი etc.).
- (owner, 19 Oct 2026, 02:42) Home page has NO packages section (no platform row, kit cards or comparison): hero, dealer strip, capabilities, ecosystem, why PDG, contact. Hero primary 'ფასები და კომპლექტაციები' → /shop#kits. Comparison stays on /p150-max (#compare).

- (owner, 19 Oct 2026) Google + Apple sign-in on /account (socialAuth in worker.template.js, account.js, docs/11-accounts.md). Off until secrets:
  GOOGLE_CLIENT_ID/GOOGLE_CLIENT_SECRET; APPLE_SERVICES_ID/APPLE_TEAM_ID/APPLE_KEY_ID/APPLE_PRIVATE_KEY. Accounts keyed by verified e-mail; profile asks for phone.
  Menu: 'ყველა ნაწილი' is the first link under 'ნაწილები და ენერგია'. Home hero button text = 'კომპლექტაციები'.

- (owner, 19 Oct 2026) Analytics: Cloudflare Web Analytics (dashboard toggle, CSP already allows its beacon) + Google Analytics 4 via scripts/site_config.py GA_ID (build writes dist/assets/js/analytics.js and opens the CSP for Google only when GA_ID is set). No cookie banner yet.

- (owner brief, 19 Oct 2026, SEO audit) Search Console: sitemap.xml was never submitted (submitted 19 Oct). P150 MAX page now has its own FAQ (pf_* keys: what is an agricultural drone/აგროდრონი, where to buy in Georgia, Starter/Pro/Business difference); shop + P150 meta descriptions lengthened. EN/RU home <title> stays the owner's exact Georgian-brand title (open question: owner may want a descriptive English/Russian title).
- (owner SEO brief, 19 Oct 2026 evening) P150 MAX page: semantic h1 = "XAG P150 MAX · სასოფლო-სამეურნეო დრონი" styled as the eyebrow (h1.eyebrow.pm-h1); slogan = p.pm-slogan with the former h1 look.
  Service/academy have fuller search descriptions via data-meta (service_meta, academy_meta) while the visible intro stays short. Product schema: items with their own page
  (packages, battery, charger...) share that page's @id and Offer URL (product_pages.url). Hero desktop image has a 2048w variant (srcset + matching preload).
  GA4 events: call_click, whatsapp_click, messenger_click, email_click (link_location), chat_open, generate_lead (consultation, topic), whatsapp_order, email_order.
  Owner confirmed all existing business/product claims are correct: do not weaken them. No homepage sections/keyword blocks for SEO.
  Consultation topic "demo" (topic_demo, ?topic=demo) = field demonstration requests; GA generate_lead carries the topic.
- (owner final brief, 19 Oct 2026) P150 MAX page: the text comparison table and the text kit table are REPLACED by one image-led section #kits (anchor #compare kept):
  four listings Platform / Starter / Pro / Business (build-shop tiles(): photo, name, short contents line from the catalog columns, price, link to its own page; Pro accent).
  Package Product schema on that page reads the tiles (data-kit="1"). Pages load content-<lang>.js (own language + ka fallback), generated by build.py from content.js.
- (owner, 19 Oct 2026, design-preview branch) Account page: one panel with tabs (sign in / register), password eye buttons, errors only after submit,
  mobile bar hidden while typing (body.acc-typing). Password reset by e-mail: POST /api/account/forgot (same answer for any e-mail, rate-limited) and
  /api/account/reset (token reset:<sha256>, 1 hour, single use; older sessions invalid via user.pwAt). Needs RESEND_API_KEY (+ verified sender domain);
  'დაგავიწყდათ პაროლი?' only shows when /api/account/config says reset:true. Google/Apple buttons only show when their secrets exist.
  Procurement topic (gov) hidden from menu and form (worker still accepts it; link kept as an HTML comment in dist/index.html).
  Working hours live only on /consultation (.contact-hours: hours_*, visit_note); footer has no hours.
