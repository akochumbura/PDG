# Site-wide settings used by the build. Edit, then run: python scripts/build.py
# Social pages: full address of each page. Empty ones are not shown on the site.
SOCIAL = {
    'Facebook': 'https://www.facebook.com/PremiumDronesGeorgia/',
    'Instagram': 'https://www.instagram.com/premium_drones_georgia/',
    'TikTok': 'https://www.tiktok.com/@premiumdrones',
    'YouTube': 'https://www.youtube.com/@PDG333',
}

# Online payment rules (owner, 14 Oct 2026): orders under 20,000 GEL are paid in full online (card, Apple Pay,
# Google Pay via Bank of Georgia); from 20,000 GEL the customer pays a deposit online and the rest by bank transfer.
PAYMENTS = {'threshold': 20000, 'deposit_percent': 10}

# Delivery in Georgia (owner, 16 Oct 2026): orders under 100 GEL pay 30 GEL delivery; from 100 GEL delivery is free.
# Pickup from the Tbilisi storage (by appointment) is always free.
SHIPPING = {'fee': 30, 'free_from': 100}

# Analytics (owner, 19 Oct 2026): Google Analytics 4 Measurement ID (G-XXXXXXXXXX). Empty = no Google script is loaded.
# Cloudflare Web Analytics is switched on in the Cloudflare dashboard (Pages > pdg > Metrics), not here.
GA_ID = ''
