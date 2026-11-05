# PROJECT_MEMORY — Premium Drones Georgia

განახლდა: 2026-10-14

## მიმდინარე მდგომარეობა

დამტკიცებული მინიმალური დიზაინი რეალიზებულია სტატიკური HTML/CSS/ვანილა JS-ით. ჰოსტინგზე გასაშვები დირექტორიაა `dist/`. შრიფტები ადგილობრივად ინახება: D-DIN ინგლისური ტექსტისთვის, Noto Sans Georgian ქართული ტექსტისთვის. რეალური PDG ლოგო და ფოტოები გამოყენებულია მიღებული ფაილებიდან; მთავარი P150 MAX-ის ფოტო მწარმოებლის ოფიციალური გვერდიდანაა.

ვერსია შეიცავს 8 გვერდს სამ ენაზე: ka/en/ru. დამატებულია აკადემიის ბმული, სრული გალერეა, ბლოგის სია და ორი გზამკვლევი. ენა ცალკე URL-ითაა განსაზღვრული. ინტერაქციები: მობილური მენიუ, მსუბუქი/მუქი თემა, ფოტო დიალოგი, საკონტაქტო წერილის მომზადება და სამუშაო პარამეტრების კალკულატორი.

მოწოდებული RAR ძველი სტატიკური პროექტია. მისი ჩანაწერით, FastAPI/SQLite ბექენდი არის ცალკე `C:\Projects\PDGE-Site` პროექტში, რომლის კოდი არქივში არ იყო. აქ სერვერული განაცხადების მიღება, მაღაზია და ადმინისტრატორის პანელი არ არის რეალიზებული. არსებული live სერვერი არ შეცვლილა.

## წყარო და განთავსება

ქართული მთავარი გვერდი — `dist/index.html`; დამატებითი ქართული გვერდების წყარო — `scripts/page-bodies.html`; თარგმანები — `dist/assets/js/content.js`. `scripts/build-pages.py` ქმნის გვერდებსა და SEO მეტამონაცემებს. წარმოებაში Python, Node ან build არ სჭირდება. `Dockerfile`, `compose.yaml` და `deploy/` შეიცავს განთავსების ალტერნატივებს. Docker პორტია localhost 8102, რათა არსებული 8101 პროტოტიპი არ გადაეწეროს.

კონტაქტები მფლობელის მიერ დადასტურებული წყაროდანაა: +995 550 00 43 33, info@premium-drones.ge, ლაგოდეხი. უცნობი ფასი, სერტიფიკატი, კურსის ხანგრძლივობა ან წარმომადგენლობის სტატუსი არ ემატება.

## შემოწმება

სინტაქსი, შიდა ბმულები, თარგმანები, რესურსები და შრიფტების ლიცენზიები მოწმდება `scripts/verify-site.py`-ით. ცალკე DOM ტესტები ფარავს მიმდინარე ინტერაქციებს. 2026-10-14: ბრაუზერული QA ჩატარდა (Chromium, 390px და 1440px, ka/en/ru, ღია/მუქი თემა, axe WCAG AA — დარღვევის გარეშე, კალათისა და WhatsApp შეკვეთის ტესტი).

## AI Handover Guide

1. წაიკითხეთ ეს ფაილი და `docs/06-refined-design-and-hosting.md` ცვლილებამდე.
2. შეინარჩუნეთ სტატიკური არქიტექტურა, UTF-8, რეალური ლოგო, ნამდვილი ფოტოები და მოკლე ტექსტები.
3. ქართული ტექსტი შეცვალეთ რედაქტორით; ყველა გასაღებს დაუმატეთ ინგლისური და რუსული თარგმანი.
4. გადაგენერირებისა და შემოწმებისთვის: `python scripts/build.py` (origin: https://premium-drones.ge, `scripts/pricing.py`).
5. `scripts/build.py` თავად უშვებს `node --check`-სა და `scripts/verify-site.py`-ს.
6. საჯაროდ განათავსეთ მხოლოდ `dist/`. პროექტის ინსტრუქციები, არქივი, git-ის ისტორია და ტექნიკური სტატუსი საჯარო დირექტორიაში არ გადაიტანოთ.
7. ფორმის რეალური გაგზავნის დასაკავშირებლად მიიღეთ ცალკე FastAPI პროექტი; არ გამოიგონოთ API endpoint ან წარმატებული გაგზავნა.
8. ახალი ეტაპის შემდეგ განაახლეთ ეს ფაილი და `docs/`. ვიზუალურად გადაამოწმეთ მობილური და desktop ხედები, როცა ბრაუზერის QA ხელმისაწვდომი იქნება.


## 2026-10-14 განახლება
- ჰოსტინგი: Cloudflare Pages (DNS უკვე Cloudflare-ზეა). სუფთა URL-ები (/shop), 404 გვერდი სამივე ენაზე, LocalBusiness მონაცემები მთავარ გვერდზე.
- მაღაზია: ნაწილებს აღარ აქვთ სხვა პროდუქტის ფოტო — სანამ რეალური ფოტო არ იქნება, ჩანს კატეგორიის ფილა. კომპლექტებზე ჩანს აკუმულატორებისა და დამტენების რაოდენობა. მობილური განლაგება გასწორდა. შეკვეთის 3 ნაბიჯი.
- P150 MAX გვერდი: XAG-ის ოფიციალური მახასიათებლები და კომპლექტების ცხრილი ფასებით; ზოგადი Starter/Pro/Business პაკეტები ამოღებულია.
- ჰედერში ენები: KA / EN / RU. მუქ თემაში ჰედერი თეთრი რჩება (ლოგო შავია).
- ელფოსტა: MX/SPF/DKIM/DMARC ჩანაწერები Cloudflare-შია; DKIM გასაღები ვალიდურია, მაგრამ ხელმოწერა პროვაიდერის მხარეს ჩასართავია (docs/09-email.md).

## 2026-10-14 მეორე ბრიფი (მფლობელი)
- დილერის ხაზი (ზუსტი ტექსტი): „Premium Drones Georgia არის XAG-ის ოფიციალური და ერთადერთი დილერი კავკასიის რეგიონში.“ — მთავარ გვერდზე ჰეროს ქვემოთ და About-ში.
- არანაირი დამფუძნებელი/CEO/ბიოგრაფია; ფოტოები ადამიანების გარეშე (technical-service.webp აღარ გამოიყენება; field-ready.webp მოჭრილია ჩრდილების გარეშე).
- მთავარი გვერდის რიგი: ჰერო → დილერის ხაზი → მახასიათებლები (მწარმოებლის მონაცემები) → XAG ეკოსისტემა → XAG მოდელების ხაზი (P150 MAX ხელმისაწვდომია; P100 Pro / P100 / V40 მარაგში არ არის, ბოლო პაკეტის ფასით) → კომპლექტაციები → ნაწილები და ენერგიის სისტემა → აკადემია → გალერეა → კითხვები → ბლოგი → კონტაქტი.
- სათაურებში „შესხურება“, ტექსტში „შეწამვლა“. „1000+ ჰა“ აღარ გამოიყენება.
- ნაწილებს ფოტოს გარეშე აქვთ სუფთა ტექსტური ბარათი (ნაცრისფერი ფილა აღარ არის). რუსული შრიფტი: IBM Plex Sans (Cyrillic). უარყოფითი letter-spacing აკრძალულია.
- ფოტოები საჭიროა: P150 MAX პროდუქტი, P100 Pro, P100, V40, B141050, დამტენი, გენერატორი, RTK/პულტი, საწყობი, აკადემია (ადამიანების გარეშე). ფაილი dist/assets/img/products/<SKU>.webp ავტომატურად ჩაჯდება.

## 2026-10-14 მესამე ბრიფი (მფლობელი)
- მაღაზია = მფლობელის ფასების სია (268 პროდუქტი, ფასი ₾-ით, VAT-ით): scripts/import-price-list.py → scripts/catalog.csv. თვითღირებულება და მარჟა არ ქვეყნდება.
- კომპლექტები (ფასები უცვლელი): Starter — 4 ბატარეა, 2 დამტენი; Pro — 6 ბატარეა, 2 დამტენი, RTK; Business — 8 ბატარეა, 4 დამტენი, RTK.
- ჰედერი: XAG – PDG ლოგოები (XAG-ის ოფიციალური ვექტორული ლოგო xa.com-დან). ყველა პროდუქტზე XAG ლოგო, სანამ ფოტოები არ იქნება.
- P150 MAX გვერდი: სრული „მახასიათებლები" (xa.com-იდან, 3 ენაზე).
- ფასებთან მხოლოდ ₾ ნიშანი — „ფასები ლარში" ტექსტები ამოღებულია. ჩატის ჰედერში ქვესათაური ამოღებულია.

## 2026-10-14 მეოთხე ბრიფი
- ნაწილების PDF-ები: ინვოისის კოდებთან (P0000…) ზუსტი SKU დამთხვევა არ არის. ფოტოები მიმაგრდა მხოლოდ იდენტური ოფიციალური სახელით (1:1) ან მოდელის კოდით (CM13600S); 40 ახალი ნაწილი — „ფასი მოთხოვნით“. ჩანაწერი: scripts/pdf-part-matches.csv.
- მარაგი: ინვოისი არ არის დადასტურებული საწყის ნაშთად; ნაშთის/გაყიდვების ჩანაწერი არ არსებობს.
- წინა თაობის მოდელები (P100 Pro, P100, V40) — ცალკე სექცია მაღაზიაში, „არ არის მარაგში“ + კონსულტაცია.
- კონფიგურატორი, რაოდენობის ღილაკები, მობილური ზოლი, XAG-ის შესახებ, მოკლე ჩატი, Organization/Product სქემა.


## ბრიფი 5 (14.10.2026, ღამე)
- SKU = XAG-ის მწარმოებლის კოდი (შეფუთვის სიის სვეტი „მწარმოებლის კოდი“); P0000… კოდები საიტზე აღარ ჩანს. რუკა: scripts/supplier-code-map.csv (268 კოდი, ერთი-ერთზე).
- დრონი P150 MAX ცალკე აღარ იყიდება — მხოლოდ კომპლექტებში.
- ფოტოები PDF-ებიდან ზუსტი მწარმოებლის კოდით (108 ფოტო). B141050 — PDF-ის INTL კოდი 09-017-00083, იგივე მოდელი. PDF-ში ბევრ ნაწილს სურათი საერთოდ არ აქვს (ცარიელი) — XAG ლოგო რჩება.
- ცალკე გვერდები მახასიათებლებით: B141050 აკუმულატორი, CM13600S დამტენი, GC4000+ დამუხტვის სადგური (გენერატორი).
- ლოგოები: XAG-ის ასოები ზუსტად PDG-ის ასოების სიმაღლისაა (0.8538 × PDG სურათი), ერთ ზედა ხაზზე; სურათებს ?v=hash ემატება, რომ ახალი ფერი მაშინვე ჩანდეს.
- 14.10 ღამე: კომპლექტები (მფლობელი, ზუსტად): Starter 75,999 — დრონი, SRC5 პულტი, 4 აკუმულატორი, 2 დამტენი, 2 გამაგრილებელი ავზი; Pro 87,999 — Starter + 2 აკუმულატორი + XRTK7; Business 104,999 — Pro, 8 აკუმულატორი და 4 დამტენი. თითოეულს საკუთარი გვერდი და ფოტო ზუსტი შემადგენლობით, შემდეგ P150 MAX-ის გალერეა.
- ლოგოები: XAG = PDG-ის მთლიანი ლოგოს სიმაღლე (წარწერის ჩათვლით), ცენტრში; ზედა მარცხნივ PDG ~ XAG.

## 2026-10-23 — ნავიგაცია, ფასები, პულტი, ტიპოგრაფია (preview: nav-prices)
- მენიუში პირველი ბმული „ფასები და კომპლექტაციები“ → /shop#kits; ტელეფონის მენიუში პირდაპირი ბმულები: ფასები, P150 MAX, ნაწილები, სერვისი, აკადემია, კონტაქტი.
- P150 MAX-ის გვერდის თავში: პლატფორმა ₾41,999 / სრული კომპლექტები ₾75,999-დან; პლატფორმის გვერდზე — რა შედის და რა არა (SRC5, აკუმულატორი, დამტენი, ავზი ფასებით).
- SRC5 = მიწოდებული პულტი; ACS4 მხოლოდ დეტალურ მახასიათებლებში, როგორც XAG-ის თავსებადი აქსესუარი, რომელსაც PDG არ აწვდის.
- ერთიანი ტიპოგრაფიული სკალა (style.css-ის ბოლოს). შემოწმება: 1453 ფასის შედარება კატალოგთან, კონფიგურატორთან, კალათასთან, worker-თან და ჩატთან — 0 შეცდომა; მომხმარებლის გზა 1280/390/360px — 41/41.

## 2026-11-04 — ყიდვის ნაწილის დახვეწა (preview: buying-refine)
- მაღაზიაში კონფიგურატორი მზა კომპლექტებამდეა; კომპლექტის ფასი მხოლოდ კომპლექტის არჩევის/შეთავაზების მიღების შემდეგ ვრცელდება; შეთავაზება ზოგვის თანხით, კონფიგურატორშიც და კალათაშიც.
- ტესტები: 96 ყიდვის სცენარი, 148 მობილური შემოწმება (360/390/430), 36 ინტერაქცია, 41 მომხმარებლის გზა, 1516 ფასის შედარება — ყველა წარმატებული.

## 5 Nov 2026 — SEO brief (branch seo-georgia, preview only until approved)
- Search purpose per page + technical rules: docs/13-seo.md. New: home title "PDG — Premium Drones Georgia | XAG სასოფლო-სამეურნეო დრონები";
  /shop title "სასოფლო-სამეურნეო დრონის ფასი — XAG P150 MAX კომპლექტები", H1 "ფასები და კომპლექტაციები"; /drones H1 "სასოფლო-სამეურნეო დრონები";
  /service H1 key service_h1; fuller search descriptions via data-meta (blog, gallery, articles, faq, drones, consultation, about, every product and package page
  with price incl. VAT and contents generated from the catalog). Schema: WebSite, BreadcrumbList, Organization without other brands' models, VAT in offers.
  robots.txt Disallow /api/; sitemap lastmod from content hashes (scripts/lastmod.json); helpful 404 links; GA4 add_to_cart (no personal data).
- 5 Nov 2026 audit pass (seo-georgia): search shows one result per destination (product before page) + arrow-key navigation; FAQ answers end with
  short links (.faq-links); faq_a2 says exposure is reduced, protective equipment still needed when mixing/filling; About XAG has a discreet link
  "PDG — XAG-ის ოფიციალური დისტრიბუტორი" -> xa.com/en/business/how-to-buy (XAG lists Premium Drones Georgia LLC, Tbilisi 0160); Organization has
  legalName, foundingDate 2022, postalCode 0160 (xa.com is NOT in sameAs). Cart total shows "დღგ-ს ჩათვლით". Shop cards: category, title,
  "code · XAG name" (English name dropped where it repeats the title); #partsGrid cards use content-visibility (layout ~0.4 s faster on phones);
  filters/sort/"load more" kept in history.state for back navigation. Package Product descriptions: RevoSpray 5 included, RevoCast 5 / RevoSling separate.
  _headers: no '/* no-cache' any more (it was joined onto asset rules, so fonts were revalidated on every page -> fallback-font flash); /assets/* 1 day.
  Telegram webhook secret compared in constant time. Preview chat shows the honest "unavailable" text because Preview deployments have no KV/secrets.
- (owner, 5 Nov 2026, approved "yes") /shop = premium buying page (configurator.block(), "work from the Apple site"): large package picture (products/<package SKU>.webp,
  the drone for custom builds) sticky on the left (desktop) / pinned under the header while the package rows scroll (phones); h1 "XAG P150 MAX";
  package rows (name, batteries · chargers · RTK, price 20px/600) + "ფასები დღგ-ს ჩათვლით"; "კომპლექტში შედის." list (drone and SRC5 fixed at 1, the rest steppers);
  "დამატებითი აღჭურვილობა" (examples in small text) as accessory cards with "დამატება"; summary: total, quiet saving vs item by item, "შეკვეთის გაგზავნა WhatsApp-ით"
  + next-step note (pb_next), cart button, four verified trust facts (pb_t1..4). Drone row name = "XAG P150 MAX — RevoSpray 5" (pc_platform, no "პლატფორმა").
  No separate ready-package cards on /shop (span#packages kept as an anchor). Pricing rules, ?c=/?m=/?kit= links, cart and offer unchanged.
- (owner, 5 Nov 2026 night) Buying page gallery: tightly cropped package pictures dist/assets/img/buy/<SKU>.webp (1168x708, cut from products/<SKU>.webp)
  + owner field photos buy/field-spray|field-spread|field-cargo.webp (no people). Swipe + dots on phones, thumbnails on desktop; choosing a package returns to slide 1.
  "ფასები და კომპლექტები": red in the desktop header; phones get a red strip under the header after 280px of scrolling (.price-strip, not on /shop).
- (owner, 5 Nov 2026, 22:40, LIVE) Buying page main action = red "კალათაში დამატება" (adds and opens the cart; phone bar "კალათაში"); WhatsApp = secondary outline button.
  Phone picture = full width (height (100vw-32px)*0.606, no aspect-ratio+max-height: iOS narrowed it). Red prices strip: shows while scrolling down, fades when scrolling up.
