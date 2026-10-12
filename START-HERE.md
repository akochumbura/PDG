# Premium Drones Georgia — website project (premium-drones.ge)

The public website is the `dist/` folder (plain files, no server software). Everything else is tools to change it.

## Easiest setup: changes go live by themselves
Follow `docs/08-setup-github-cloudflare.md` once (about 30–45 minutes). After that you just tell Claude what to change.

## Daily use (after setup)
Open this folder in Claude Code (Claude desktop app, "Code" tab) and say things like:
- "Remove the Landing Gear from the shop."
- "Add a part: name, code, Agrifuture price in USD."
- "The dollar rate is now 2.70 — recalculate prices."
- "Change the Starter kit markup" / "Change the phone number."
Claude edits the files, runs `python scripts/build.py`, and saves (commits) the change. Cloudflare publishes it.

## Where things live
- Prices and products: `scripts/catalog.csv` (USD base price) + `scripts/pricing.py` (rate, +10% kits, +70% parts)
- Texts in 3 languages: `scripts/page-bodies.html` (Georgian pages) + `dist/assets/js/content.js` (EN/RU)
- Product photos: put `<code>.jpg` files in a folder, run `python scripts/import-photos.py <folder>`, then `python scripts/build.py`
- Online payments: not connected yet — see `docs/07-payments.md`
- Rebuild + check everything: `pip install -r requirements.txt` once, then `python scripts/build.py`
