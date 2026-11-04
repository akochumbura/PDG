# Online payments: Bank of Georgia

Status (4 Nov 2026): the full BOG Payments API integration is built and tested against a simulated bank
(api.bog.ge/docs, read 4 Nov 2026). It stays OFF until the owner has the BOG e-commerce agreement and saves the keys
in Cloudflare. Nothing changes on the site before that: no Pay button, no installment buttons, chat says online payment is not available.

Owner rules:
- Orders under 20,000 GEL: paid in full online. From 20,000 GEL: 10% deposit online, rest by bank transfer (scripts/site_config.py PAYMENTS).
- Installment / pay in parts cover the FULL order amount (no deposit); the bank sets the terms and approves. Never quote monthly amounts or interest.
- An order counts as paid only when the bank's own receipt says "completed".

What the site does (scripts/worker.template.js -> dist/_worker.js; prices always from the catalog on the server):
- Hosted BOG payment page. Full payment: no payment_method is sent, so the bank shows EVERY method activated for PDG in Business Manager
  (card, Apple Pay, Google Pay, BOG internet bank bog_p2p, MR/Plus points bog_loyalty, gift_card, and the bank's own installment options).
  Deposit: the same list without bnpl / bog_loan (fallback: card only). BOG_PAYMENT_METHODS (comma list) restricts it if ever needed.
- Installment (bog_loan) and pay in parts (bnpl): cart buttons "განვადება" / "ნაწილ-ნაწილ გადახდა" when BOG_INSTALLMENT = "loan", "bnpl" or "loan,bnpl".
  They open the official BOG calculator (webstatic.bog.ge/bog-sdk/bog-sdk.js?version=2&client_id=…); the chosen month + discount code go to
  POST /api/checkout as plan, the server creates the order with payment_method ["bog_loan"] or ["bnpl"] and config.loan {type, month}.
- Callback POST /api/payments/callback: Callback-Signature checked (SHA256withRSA, BOG public key built in; BOG_CALLBACK_KEY overrides),
  unsigned/wrong = 401 and ignored; then the status is read from the bank receipt (GET /receipt/{id}), never from the body.
- Telegram alert to the owner when an order becomes PAID, REFUNDED or PARTLY REFUNDED (method, amount, customer, items).
- /api/orders?key=ADMIN_KEY: orders with status, method, paid / refunded amounts, installment months, and a Refund form
  (empty amount = full refund, or a partial amount; tick confirm). POST /api/orders/refund -> BOG /payment/refund/{id} with Idempotency-Key.
- Payment page /payment: shows only the bank status (paid, deposit paid, pending, installment under review, refunded, failed).
- Chat: when the keys exist, the AI says online payment is available (and installment when switched on) instead of "not available".
- CSP allows *.bog.ge for the calculator (script, frame, connect, img, style, font).

To switch it on (owner):
1. Sign the BOG e-commerce agreement (businessmanager.bog.ge). Ask BOG to activate: card, Apple Pay, Google Pay, BOG internet bank (P2P),
   MR/Plus points, gift cards, and online installment + BNPL (ნაწილ-ნაწილ). Ask BOG for sandbox (test) credentials first.
2. Business Manager gives client_id and client_secret. Cloudflare -> pdg -> Settings -> Variables and Secrets (Production):
   BOG_CLIENT_ID, BOG_CLIENT_SECRET (Secret). Optional: BOG_INSTALLMENT = loan,bnpl (only after BOG activated installment).
   For a sandbox test first: also BOG_TOKEN_URL / BOG_API_URL with the sandbox addresses BOG gives (remove them for live).
3. Deployments -> ⋯ -> Retry deployment. Check https://premium-drones.ge/api/payments/config shows "enabled":true.
4. One small real payment (a cheap part, choose Tbilisi pickup), check the Telegram alert and /api/orders, refund it from /api/orders, then announce.
Emergency stop: variable PAYMENTS_ENABLED = off (then Retry deployment).
