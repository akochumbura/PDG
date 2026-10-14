# Premium Drones Georgia - premium-drones.ge

The public website is the `dist/` folder: plain files, no server software.
- Publish: docs/08-go-live-cloudflare.md  (iPhone drag-and-drop or GitHub)
- E-mail status and DKIM fix: docs/09-email.md
- Payments (not connected yet): docs/07-payments.md
- SEO and social: titles, structured data, FAQ, share image and llms.txt are built in. Setup steps and post templates are in the "PDG SEO & Social Playbook" doc.

## Change things by asking Claude
Attach `PDG-Website-Project.zip` (or open this folder in Claude Code) and say what to change, for example:
- "Remove the Landing Gear from the shop." / "Add a part: name, code, Agrifuture price in USD."
- "The dollar rate is now 2.70 - recalculate prices." / "Change the kit markup to 12%."
- "Here are photos named by part code - add them to the shop."
Claude edits, runs `python scripts/build.py` (rebuild + checks), and gives back a new hosting zip.

## Where things live
- Products and USD base prices: `scripts/catalog.csv` (group: kit|power|spray|control|acc|spare; image = kit photo)
- Social pages (Facebook, Instagram, TikTok, YouTube): paste the addresses into `scripts/site_config.py`; empty ones stay hidden
- Exchange rate and markups (+10% kits, +70% parts): `scripts/pricing.py`
- Georgian text: `dist/index.html` (home) and `scripts/page-bodies.html` (other pages); English/Russian: `dist/assets/js/content.js`
- Product photos: `python scripts/import-photos.py <folder>` with files named by part code, then `python scripts/build.py`
- Preview like Cloudflare: `python scripts/serve.py` then open http://localhost:8000
- First time on a computer: `pip install -r requirements.txt`
