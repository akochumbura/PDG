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

## Google and Apple sign-in (19 Oct 2026)

Buttons "Google-ით შესვლა" / "Apple-ით შესვლა" sit above the e-mail forms on /account. Each button appears only when its
secrets exist (GET /api/account/config shows google / apple true). Accounts are matched by e-mail: a customer who signs in with
Google and later with Apple (same e-mail) lands in the same account; a password account with that e-mail is the same account too.
Google/Apple do not give a phone number, so the profile asks for it ("შეკვეთისთვის დაამატეთ ტელეფონის ნომერი").
Code: socialAuth() in scripts/worker.template.js; routes /api/auth/google|apple/start and /callback.

Google (free):
1. console.cloud.google.com → new project "Premium Drones Georgia".
2. APIs & Services → OAuth consent screen (Google Auth Platform): External, app name "Premium Drones Georgia", support e-mail,
   authorised domain premium-drones.ge, scopes: openid, email, profile. Publish the app ("In production").
3. Clients → Create client → Web application. Authorised JavaScript origin: https://premium-drones.ge
   Authorised redirect URI: https://premium-drones.ge/api/auth/google/callback
4. Cloudflare → pdg → Settings → Variables and secrets: GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET (type Secret) → redeploy.

Apple (needs a paid Apple Developer Program membership, 99 USD a year; an organisation membership needs a D-U-N-S number):
1. developer.apple.com → Certificates, Identifiers & Profiles → Identifiers → App ID (e.g. ge.premium-drones.app) with "Sign in with Apple".
2. Identifiers → Services IDs → new, e.g. ge.premium-drones.signin, description "Premium Drones Georgia" (customers see this name);
   enable Sign in with Apple → Configure: primary App ID from step 1, domain premium-drones.ge,
   return URL https://premium-drones.ge/api/auth/apple/callback
3. Keys → new key with "Sign in with Apple" (linked to the App ID) → download the .p8 file (only once) and note the Key ID.
4. Cloudflare secrets: APPLE_SERVICES_ID (the Services ID), APPLE_TEAM_ID (top right of the developer account),
   APPLE_KEY_ID, APPLE_PRIVATE_KEY (the whole text of the .p8 file) → redeploy.
Apple may give a private relay e-mail (…@privaterelay.appleid.com) when the customer hides their e-mail; it still works for sign-in.
