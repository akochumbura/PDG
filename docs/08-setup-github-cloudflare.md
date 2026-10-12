# One-time setup: GitHub + Cloudflare Pages (free)

Goal: every change saved in the project is published on https://premium-drones.ge automatically.
Menu names on these websites change from time to time; follow the idea if a label differs.

## Step 0 — Before you touch the domain
Your email (info@premium-drones.ge) may depend on the domain's DNS settings. Ask whoever manages the domain/email, or open the DNS settings at the company where you bought the domain, and **copy down every existing record** (especially MX and TXT). Keep that list. Do not change nameservers until Step 3.

## Step 1 — GitHub (stores the files and every version)
1. Create a free account at github.com.
2. Install **GitHub Desktop** (desktop.github.com) and sign in.
3. Unzip `PDG-Website-Project.zip`. In GitHub Desktop: File → Add local repository → choose the unzipped folder `PDG-Website-Ready`.
4. Click **Publish repository**. Name it `pdg-website`. **Keep this code private** (tick the box).

## Step 2 — Cloudflare Pages (publishes the site)
1. Create a free account at cloudflare.com.
2. Workers & Pages → Create → Pages → **Connect to Git** → allow GitHub → pick `pdg-website`.
3. Settings: Framework preset **None**; Build command **leave empty**; Build output directory **dist**. Save and Deploy.
4. You get a test address like `pdg-website.pages.dev`. Open it and check the site.

## Step 3 — Put your domain on it
1. In the Pages project: Custom domains → Set up a domain → `premium-drones.ge` (and `www.premium-drones.ge`).
2. Cloudflare will ask you to add the domain to Cloudflare and change the **nameservers** at your domain registrar. Before you do, confirm in Cloudflare's DNS table that all records from Step 0 (MX, TXT for email) are present. Add any that are missing.
3. Change the nameservers at the registrar to the two Cloudflare gives you. Wait (minutes to a day).
4. Check: the site opens on https://premium-drones.ge with the padlock, and send/receive a test email.

## Step 4 — Daily use with Claude
Install the Claude desktop app, open the **Code** tab, open the folder `pdg-website` (the one GitHub Desktop made), and tell Claude what to change. Ask it to run `python scripts/build.py` and to commit and push the change. Cloudflare publishes within a minute or two.
Needs on your computer: Python 3 (python.org) and, optionally, Node.js. Claude can install the rest (`pip install -r requirements.txt`).

## If something breaks
In Cloudflare Pages → Deployments you can roll back to any earlier version with one click.
