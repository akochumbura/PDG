# Online payments (Apple Pay, card, PayPal)

Status: NOT connected. The shop sends orders by WhatsApp or e-mail; PDG confirms price, stock and delivery.
The "Pay online" button stays hidden until `dist/assets/js/payments-config.js` has an `endpoint`.

What it takes (checked Oct 2026):
- Stripe does not support companies registered in Georgia.
- Card + Apple Pay for a Georgian company goes through a bank payment gateway: Bank of Georgia (iPay) or TBC (Flitt).
  You need a business account and merchant approval from the bank; the bank gives API keys.
- PayPal: check in your PayPal business account that it can RECEIVE payments in Georgia before planning on it.

Where the server part can live: Cloudflare Pages Functions (same Cloudflare project as the site) or any small server.
Gateway keys stay on the server only, never in the website files.

Contract the shop already speaks:
POST <endpoint>  JSON {items:[{sku,name,qty,price}], total, currency:"GEL", lang, customer:{name,phone,address}}
Response JSON {url:"<bank's hosted payment page>"} -> the browser goes there.
Treat an order as paid only when the bank's server callback confirms it, never because the browser came back.
