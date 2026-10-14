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
