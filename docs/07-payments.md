# Online payments: Bank of Georgia (card, Apple Pay, Google Pay)

Status (14 Oct 2026): PAUSED by the owner, about 80% built and NOT yet tested end to end.
Nothing shows on the site: the Pay button appears only when the bank keys are saved in Cloudflare.

Owner rules:
- Bank: Bank of Georgia (BOG online payments, hosted payment page: card, Apple Pay, Google Pay).
- Orders under 20,000 GEL: paid in full online. From 20,000 GEL: deposit online, rest by bank transfer.
  Deposit is 10% for now (scripts/site_config.py PAYMENTS) - owner has not confirmed the percentage.

Built so far:
- scripts/worker.template.js -> dist/_worker.js (Cloudflare Pages advanced mode; works with drag-and-drop upload).
  dist/_routes.json sends only /api/* to it. Prices are taken from scripts/catalog.csv on the server, never from the browser.
  /api/payments/config, /api/checkout, /api/payments/status, /api/payments/callback, /api/orders?key=ADMIN_KEY (needs KV ORDERS).
- Cart: Pay button + deposit note (shop.js), payment status page /payment (noindex), terms page /terms.

Still to do before going live:
1. Finish the end-to-end test with the simulated bank (scratch harness), incl. deposit and failed payments.
2. Owner: sign the BOG e-commerce agreement (businessmanager.bog.ge), activate Apple Pay and Google Pay there,
   get client_id and client_secret. Confirm the deposit %. Review the terms page text (returns/delivery) with an accountant/lawyer.
3. Cloudflare Pages > Settings > Variables and Secrets: BOG_CLIENT_ID, BOG_CLIENT_SECRET (encrypted), optional ADMIN_KEY;
   optional KV namespace bound as ORDERS. Upload the site again after saving them.
4. One small real payment, then refund it, before announcing.
