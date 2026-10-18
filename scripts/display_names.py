"""Short Georgian display names for shop cards, the cart and search results (audit, 19 Oct 2026).

catalog.csv keeps the full Georgian name from the owner's price list (name_ka); build-shop.py shows short_ka() instead and
build-search.py keeps the full name as a search keyword, so every old wording still finds the part.
Rules: drop the repeated "სასოფლო-სამეურნეო დრონის" / "... ან მისი სამუშაო სისტემის სათადარიგო ნაწილი:" wording,
shorten the ESC phrase, and remove internal supplier notes ("; ... დასაზუსტებელია მომწოდებელთან").
Model, side, colour, version, size and part numbers always stay, so different parts never look the same.
"""
import re

# Main items: the concise names the owner's brief asks for (model code + what it is).
OVERRIDES = {
    '05-002-02725': 'XAG SRC5 მართვის პულტი',
    '09-017-00073': 'XAG B141050 აკუმულატორი',
    '09-017-00069': 'XAG CM13600S დამტენი',
    '09-017-00065': 'XAG აკუმულატორის გამაგრილებელი ავზი (2024, INTL)',
    '09-016-00083': 'XAG XRTK7 მობილური RTK სადგური (INTL)',
    '09-017-00109': 'XAG GC4000+ დამუხტვის სადგური (გენერატორი, III თაობა)',
    '09-023-00145': 'XAG RevoCast 5 გრანულების გამფანტველი სისტემა (P150 MAX, შნეკი L)',
    '05-002-02640': 'XAG P150 MAX 4-საქშენიანი განახლების კომპლექტი (INTL)',
    '05-002-02682': 'XAG RevoSling ტვირთის საკიდი სისტემა + შასი 05-002-02683 (INTL)',
    '09-027-00003': 'XAG 90 ვტ LED ფარი',
    '02-001-11558': 'XAG P150 MAX წინა ნაწილის დამჭერი (Head card holder)',
    '05-002-02313': 'XAG სათადარიგო ძრავა',
    '09-017-00064': 'XAG B13970S აკუმულატორი',
}

_RULES = [
    (r'\s*;\s*[^;]*დასაზუსტებ[^;]*$', ''),  # internal supplier note, never public
    (r'სასოფლო-სამეურნეო დრონის ან მისი სამუშაო სისტემის სათადარიგო ნაწილი:\s*', ''),
    (r'\s*,?\s*სასოფლო-სამეურნეო დრონის\s+(ელექტროკვებისთვის|სამართავად|აკუმულატორების დასატენად|აკუმულატორების გასაგრილებლად|ზუსტი პოზიციონირებისთვის)$', ''),
    (r'\s*,\s*სასოფლო-სამეურნეო დრონის[^,]*$', ''),
    (r'\s+სასოფლო-სამეურნეო დრონის\s+', ' '),
    (r'ბრუნვის ელექტრონული რეგულატორის \(ESC\)', 'რეგულატორის (ESC)'),
    (r'ბრუნვის ელექტრონული რეგულატორი \(ESC\)', 'რეგულატორი (ESC)'),
    (r'\bP150 Max\b', 'P150 MAX'),
    (r'\s{2,}', ' '),
]


def short_ka(sku, name_ka):
    name = (name_ka or '').strip()
    if not name:
        return name
    if sku in OVERRIDES:
        return OVERRIDES[sku]
    for pat, rep in _RULES:
        name = re.sub(pat, rep, name)
    return name.strip(' ,;')
