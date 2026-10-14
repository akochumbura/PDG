"""Previous-generation XAG agricultural drones (owner, 14 Oct 2026: shown as a separate shop category, not for sale,
"არ არის მარაგში" + consultation). No prices (do not invent historical prices) and no Offer schema.
Specs verified on the official XAG spec pages (read 14 Oct 2026):
  https://www.xa.com/en/p100pro/p100prospecs, https://www.xa.com/en/p100/p100specs, https://www.xa.com/en/v40/v40specs
No official clean product photo was available, so the cards show the XAG logo until the owner supplies photos
(dist/assets/img/products/<sku>.webp is picked up automatically).
"""

MODELS = [
    {'sku': 'XAG-P100PRO', 'name': 'XAG P100 Pro Agricultural Drone', 'name_ka': 'XAG P100 Pro სასოფლო-სამეურნეო დრონი',
     'specs': ('ავზი 50 ლ · ტვირთი 50 კგ · ხარჯი 22 ლ/წთ · გრანულები 80 ლ · 13.8 მ/წმ · IPX6K',
               'Tank 50 L · payload 50 kg · flow 22 L/min · granules 80 L · 13.8 m/s · IPX6K',
               'Бак 50 л · нагрузка 50 кг · расход 22 л/мин · гранулы 80 л · 13.8 м/с · IPX6K')},
    {'sku': 'XAG-P100', 'name': 'XAG P100 Agricultural Drone', 'name_ka': 'XAG P100 სასოფლო-სამეურნეო დრონი',
     'specs': ('ავზი 40 ლ · გრანულები 60 ლ (40 კგ) · ხარჯი 12 ლ/წთ · 13.8 მ/წმ · IPX7',
               'Tank 40 L · granules 60 L (40 kg) · flow 12 L/min · 13.8 m/s · IPX7',
               'Бак 40 л · гранулы 60 л (40 кг) · расход 12 л/мин · 13.8 м/с · IPX7')},
    {'sku': 'XAG-V40', 'name': 'XAG V40 Agricultural Drone', 'name_ka': 'XAG V40 სასოფლო-სამეურნეო დრონი',
     'specs': ('ავზი 16 ლ · გრანულები 25 ლ · ხარჯი 10 ლ/წთ · 8 მ/წმ',
               'Tank 16 L · granules 25 L · flow 10 L/min · 8 m/s',
               'Бак 16 л · гранулы 25 л · расход 10 л/мин · 8 м/с')},
]
