# Customer accounts

Page: /account (ka), /en/account, /ru/account. Header: person icon next to search and cart.
Customers register (name, email, phone, company, password), sign in, keep their details (filled into the cart
automatically) and see their order history: online payments and orders they sent by WhatsApp or e-mail while signed in.

Status: built and tested end to end (register, sign in, wrong password, lockout after 8 tries for 15 minutes,
profile update, cart prefill, order history, admin password reset). It shows "accounts are opening soon" until storage exists.

To switch it on (Cloudflare Pages -> the site -> Settings):
1. Workers & Pages -> KV -> create a namespace, e.g. "pdg-data".
2. The Pages project -> Settings -> Bindings -> add KV namespace binding, variable name PDG_DATA -> pdg-data.
3. Variables and Secrets -> ADMIN_KEY = a long random text (20+ characters, keep it private).
4. Upload the site again.

Security: passwords are stored only as PBKDF2-SHA256 hashes (100,000 rounds, random salt); sessions are random
tokens in an HttpOnly, Secure, SameSite=Lax cookie for 30 days; requests from other websites are refused.

Forgotten password: no e-mail service is connected, so the customer writes on WhatsApp. Open
https://premium-drones.ge/api/admin/reset?key=ADMIN_KEY&email=CUSTOMER_EMAIL and send them the temporary password.
All orders and the number of accounts: https://premium-drones.ge/api/orders?key=ADMIN_KEY
Later improvement: connect an e-mail service (for example Resend) for self-service password reset and order e-mails.
