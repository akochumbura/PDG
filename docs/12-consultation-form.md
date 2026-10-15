# Consultation form (/consultation) — server-side since 15 Oct 2026

POST /api/contact (dist/_worker.js, from scripts/worker.template.js). The page shows success ONLY after the server answers {ok:true}.

Checks: JSON only, same-origin (Origin header), 10 kB limit, name 2-100 chars, phone 9-15 digits, topic whitelist, max 2 links,
hidden "website" honeypot (filled -> silently dropped), at least 2.5 s between page load and submit, 4 requests / 10 min per IP per
isolate, 5 / hour per visitor and 200 / day for the whole form in KV (CONTACT_DAILY_LIMIT), the same phone+message twice in 15 min = one request.

Delivery (a request is "accepted" when at least one of these worked):
1. Stored in KV (binding PDG_DATA, already connected): read at /api/contact/inbox (sign-in with ADMIN_KEY, same key as the chat inbox).
2. E-mailed to CONTACT_TO (default info@premium-drones.ge) through Resend when the secret RESEND_API_KEY exists.
   CONTACT_FROM must be a sender on a domain verified in Resend (default "Premium Drones Georgia <no-reply@premium-drones.ge>").
3. Alerts to Telegram / WhatsApp (CallMeBot) with the same settings as the chat.
No KV and no RESEND_API_KEY -> 503 and the page tells the visitor to call or use WhatsApp.

Missing as of 15 Oct 2026: RESEND_API_KEY (create at resend.com, add and verify premium-drones.ge with the DNS records they show,
then add the secret on Pages project "pdg" and retry the deployment). Until then requests are stored in the inbox only.
Keep the existing mail DNS records (docs/09-email.md): Resend asks for its own DKIM/SPF records next to them.
