# Premium Drones Georgia

Read PROJECT_MEMORY.md before editing. Keep this project buildless: HTML, CSS,
vanilla JavaScript and self-hosted font/photo assets. Preserve the owner's supplied
logo exactly. Georgian source is UTF-8 in dist/index.html and scripts/page-bodies.html;
English and Russian counterparts belong in dist/assets/js/content.js. Regenerate
and check everything with `python scripts/build.py`. Publish only dist. Update project memory
and stage documentation after significant changes. Never describe the mailto form
as a server inbox. The separately referenced FastAPI project was not included.

## Workflow (updated 14 Oct 2026: shop, 3 languages, premium-drones.ge on Cloudflare Pages)
- Domain premium-drones.ge (DNS on Cloudflare); contact info@premium-drones.ge; WhatsApp/phone +995 550 00 43 33.
- Rebuild and verify EVERYTHING with `python scripts/build.py` (shop cards + P150 kit table from catalog.csv/pricing.py,
  then pages, then checks). Never hand-edit generated dist/*.html except dist/index.html (source of the Georgian home page).
- Hosting is Cloudflare Pages: it serves /shop.html as /shop. The build writes clean URLs (no .html) in links,
  canonicals and the sitemap; verify fails on any internal .html link. 404.html exists per language (noindex).
  Local preview that behaves the same: `python scripts/serve.py`.
- Prices: a fixed GEL price in the catalog `gel` column wins (packages, B141050 battery 5999, XAG generator 5899).
  Otherwise shop price = Agrifuture USD x markup x RATE (parts x1.70). Change only scripts/pricing.py or scripts/catalog.csv.
- Packages (owner, 14 Oct 2026): only three - Starter 75,999 (drone, 4 batteries, 2 chargers), Pro 85,999 (drone, 6 batteries,
  2 chargers, RTK station), Business 104,999 (drone, 8 batteries, 2 chargers, 2 generators). Contents = catalog columns.
- Spraying (owner brief 14 Oct 2026): headings use შესხურება, explanatory text uses შეწამვლა; combined line
  "ზუსტი შესხურება / შეწამვლა რეალურ საველე პირობებში." Experience: "thousands of hectares in real field conditions"
  (optional quiet "2,900+ ha in the 2026 season"); never "1000+ ha". Worked with XAG V40, P100, P100 Pro; focus P150 MAX.
  Locations: Tbilisi = storage and service (Panaskerteli-Tsitsishvili St 12, by appointment, not a showroom);
  Lagodekhi = field operations. No hidden SEO text; model names only in meta/structured data/llms.txt.
- Model range on home: P150 MAX available; P100 Pro 72,500 / P100 70,220 (drone + 4 batteries), V40 38,500 (drone + 2)
  are out of stock and show "Last package price".
- Product photos: dist/assets/img/products/<SKU>.webp is picked up at build time. Parts without their own photo show a
  text-only card (no grey placeholder). Never show a photo of a different product on a part card (verify enforces this).
- No people or faces in any photo, no founder name, no CEO, no personal biography (verify blocks technical-service.webp,
  'founder', 'CEO', '1000+'). Product and equipment photos only; no DJI images in XAG sections; no AI images.
- No negative letter-spacing anywhere (verify enforces); no decorative gradients; no loud badges.
- P150 MAX specs on the site are from xa.com/en/p150max/p150maxspecs (Oct 2026). Do not add unverified specs.
- Every new UI string needs ka (in the HTML), en and ru keys in dist/assets/js/content.js.
- Payments: Bank of Georgia via dist/_worker.js, PAUSED and not live (see docs/07-payments.md). Never claim a payment succeeded
  unless the bank receipt says completed. Under 20,000 GEL full payment, from 20,000 GEL deposit + bank transfer.
- Home page must stay short and simple (owner): hero, dealer line, key specs, ecosystem, packages, contact. Detail lives on other pages.
- Fonts: D-DIN (Latin, like xa.com), Noto Sans Georgian, IBM Plex Sans (Cyrillic). Keep font licences in dist/assets/fonts.
  Logo: pdg-logo-light.png / pdg-logo-dark.png are transparent cut-outs of the supplied logo (owner asked for this);
  header, footer and logo follow the light/dark theme (default = phone setting).
- Dealer claim, exact owner wording only: "Premium Drones Georgia is the official and exclusive XAG dealer in the Caucasus
  region." (ka/en/ru key dealer_line). Make no other official claims.
- E-mail on the site: only info@premium-drones.ge.
- Company name in Georgian text is "საქართველოს პრემიუმ დრონები" (owner, 14 Oct 2026); Latin "Premium Drones Georgia" in en/ru,
  the logo and structured data (with alternateName).
- E-mail DNS records in Cloudflare must not be removed (docs/09-email.md).
