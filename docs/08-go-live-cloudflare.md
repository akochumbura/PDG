# Go live on Cloudflare Pages (free)

Status (14 Oct 2026): premium-drones.ge already uses Cloudflare (nameservers kristina/miguel.ns.cloudflare.com),
and the e-mail records are in Cloudflare DNS. The website itself is not published yet.

## A. From an iPhone (no computer needed) - recommended now
1. Save `PDG-Website-HOSTING.zip` to the Files app. Do not unzip it.
2. Cloudflare dashboard -> Workers & Pages -> Create application -> Get started -> Drag and drop your files
   (on an iPhone: tap to select the zip from Files). Project name: `pdg-website`. Deploy.
3. Open the test address Cloudflare shows (pdg-website.pages.dev) and check the site.
4. In the project: Custom domains -> Set up a custom domain -> `premium-drones.ge` -> Activate.
   Repeat for `www.premium-drones.ge`. Cloudflare adds the DNS records itself.
5. Wait for "Active" (minutes to an hour), then open https://premium-drones.ge.

Updating later: Workers & Pages -> pdg-website -> Create a new deployment -> upload the new zip.
Undo: Deployments -> pick an older deployment -> Rollback.
Note: a drag-and-drop project cannot be switched to GitHub later; for automatic updates you would make a
new GitHub-connected project and move the custom domain to it.

## B. With a computer: GitHub + automatic publishing (optional, later)
1. Free github.com account; install GitHub Desktop; File -> Add local repository -> this folder -> Publish (private).
2. Cloudflare: Workers & Pages -> Create -> Pages -> Connect to Git -> pick the repository.
   Framework preset: None. Build command: empty. Build output directory: `dist`.
3. Move the custom domains from project A to this project.
After that, each saved change (commit + push) publishes by itself in a minute or two.

## Do not touch these DNS records (they run the e-mail)
| Type | Name | Content |
|---|---|---|
| MX | premium-drones.ge | mx.premium-drones.ge.cust.hostedemail.com (priority 0) |
| TXT | premium-drones.ge | v=spf1 include:_spf.hostedemail.com ~all |
| TXT | dkim1._domainkey | v=DKIM1; h=sha256; k=rsa; s=email; p=MIIBIjAN... (2048-bit key, verified valid) |
| TXT | _dmarc | v=DMARC1; p=none; rua=mailto:info@premium-drones.ge |
Keep them "DNS only" (grey cloud). See docs/09-email.md.

## www.premium-drones.ge (added 14 Oct 2026)
The site's main address stays https://premium-drones.ge (canonical links, sitemap). www must work and send visitors there:
1. Cloudflare -> Workers & Pages -> the site -> Custom domains -> Set up a custom domain -> premium-drones.ge (if not done)
   and again -> www.premium-drones.ge. DNS is on Cloudflare, so it creates the www record itself.
2. Cloudflare -> premium-drones.ge -> Rules -> Redirect Rules -> Create rule -> template "Redirect from WWW to root":
   www.premium-drones.ge/* -> https://premium-drones.ge/${1}, 301, keep query string. Save.
3. Test on the phone: www.premium-drones.ge and www.premium-drones.ge/shop must open premium-drones.ge.
Do not touch the MX, SPF, DKIM or DMARC e-mail records while doing this.
