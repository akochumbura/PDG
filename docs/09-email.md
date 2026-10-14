# E-mail (info@premium-drones.ge)

Provider: OpenSRS Hosted Email (hostedemail.com), sold by domenebi.ge, paid until 19.05.2027.
DNS: Cloudflare (records listed in docs/08-go-live-cloudflare.md).

## State on 14 Oct 2026
- Sending and receiving work (tested both ways).
- mail-tester.com: 9/10. SPF pass, DMARC pass, not on blocklists.
- DKIM: the public key is published at dkim1._domainkey and is a valid 2048-bit RSA key
  (checked: correct structure, no small factors, so no typing error). But outgoing mail is NOT signed.
  Signing is switched on inside the mail provider, not in DNS.

## Fix DKIM signing (needs the mail provider side)
Option 1 - ask domenebi.ge support: "Please enable outgoing DKIM signing for premium-drones.ge, selector dkim1;
the public key is already published at dkim1._domainkey.premium-drones.ge."
Option 2 - if the mailbox has administrator rights: log in to the OpenSRS Mail Administration Console at
https://admin.a.hostedemail.com (or admin.b...) with the mailbox address and password, open the domain, DKIM section,
selector `dkim1`. The private key must match the published public key - if domenebi created the key, they hold it.
Check afterwards: send a message to the address shown on mail-tester.com; DKIM should say "signed" and score 10/10.

## Later
- When DKIM signs correctly for a few weeks: change DMARC to `v=DMARC1; p=quarantine; rua=mailto:info@premium-drones.ge`.
- DMARC sends daily summary e-mails (zipped XML) to info@. They are reports, not spam. To stop them, remove `rua=...`.
- New domains build trust slowly with Gmail: mark test mails "Not spam", send real mail to real contacts and get replies.
