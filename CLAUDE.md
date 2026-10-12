# Premium Drones Georgia

Read PROJECT_MEMORY.md before editing. Keep this project buildless: HTML, CSS,
vanilla JavaScript and self-hosted font/photo assets. Preserve the owner's supplied
logo exactly. Georgian source is UTF-8 in dist/index.html and scripts/page-bodies.html;
English and Russian counterparts belong in dist/assets/js/content.js. Regenerate
prebuilt pages with scripts/build-pages.py, then run scripts/verify-site.py and
node --check for both JavaScript files. Publish only dist. Update project memory
and stage documentation after significant changes. Never describe the mailto form
as a server inbox. The separately referenced FastAPI project was not included.

## Workflow added Oct 2026 (shop, 3 languages, premium-drones.ge)
- Domain premium-drones.ge; contact email info@premium-drones.ge; WhatsApp/phone +995 550 00 43 33.
- Rebuild and verify EVERYTHING with `python scripts/build.py` (regenerates shop from scripts/catalog.csv + scripts/pricing.py, then pages, then verify). Never edit generated dist/*.html pages by hand except dist/index.html (source of the Georgian home page).
- Prices: shop price = Agrifuture USD base x markup x RATE, rounded to whole GEL. Kits/drones x1.10, parts x1.70. Change only scripts/pricing.py or catalog.csv.
- Products: add/remove rows in scripts/catalog.csv (group: power|spray|control|acc|spare|kit). Product photos: dist/assets/img/products/<SKU>.webp via scripts/import-photos.py.
- Every new UI string needs ka (in the HTML), en and ru keys in dist/assets/js/content.js.
- Payments are NOT connected; never claim a payment succeeded. Orders go by WhatsApp/e-mail. See docs/07-payments.md.
- Fonts: D-DIN (Latin, like xa.com), Noto Sans Georgian, Roboto Cyrillic. Keep font licences in dist/assets/fonts.
- Do not mark PDG as an "authorized XAG distributor" on the site unless the owner gives the exact allowed wording.
