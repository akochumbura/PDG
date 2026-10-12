# Online payments (Apple Pay, card, PayPal)

Status: NOT connected. The shop sends orders by WhatsApp/e-mail. The "Pay online" button stays hidden until `dist/assets/js/payments-config.js` has an `endpoint`.

Georgia notes (checked Oct 2026): Stripe does not support Georgian companies. Card + Apple Pay for a Georgian company is done through a bank gateway: Bank of Georgia iPay or TBC/Flitt (needs a business account and merchant approval). PayPal: confirm in your PayPal business account that you can RECEIVE payments in Georgia.

Server contract the front end expects (build on your FastAPI backend, keep gateway secrets there only):
POST endpoint, JSON: {items:[{sku,name,qty,price}], total, currency:"GEL", lang, customer:{name,phone,address}}
Response JSON: {url:"<hosted gateway payment page>"}  -> browser redirects. Confirm payment via the gateway callback, never from the browser.
