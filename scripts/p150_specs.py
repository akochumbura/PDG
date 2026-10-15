"""XAG P150 MAX full specifications (source: https://www.xa.com/en/p150max/p150maxspecs, read 14 Oct 2026).
Used by scripts/build-specs.py to fill the "მახასიათებლები" section of the P150 MAX page in ka / en / ru.
Each row: (label, value). A label or value is either a plain string (same in every language) or a (ka, en, ru) tuple.
Edit here only; do not add specs that are not on the official XAG page.
"""

T = tuple  # readability: T(('ka', 'en', 'ru'))

# Frequently used words
MM = ('მმ', 'mm', 'мм')


def u(n, unit):
    """Number + unit in three languages."""
    ka, en, ru = unit
    return (f'{n} {ka}', f'{n} {en}', f'{n} {ru}')


KG, L, M, MS, W, A, V, C = ('კგ', 'kg', 'кг'), ('ლ', 'L', 'л'), ('მ', 'm', 'м'), ('მ/წმ', 'm/s', 'м/с'), ('ვტ', 'W', 'Вт'), ('ა', 'A', 'А'), ('ვ', 'V', 'В'), ('℃', '℃', '℃')
QTY = ('რაოდენობა', 'Quantity', 'Количество')
MODEL = ('მოდელი', 'Model', 'Модель')
OPT = ('სამუშაო ტემპერატურა', 'Operating temperature', 'Рабочая температура')
CHT = ('დამუხტვის გარემოს ტემპერატურა', 'Charging ambient temperature', 'Температура среды при зарядке')
OPV = ('სამუშაო ძაბვა', 'Operating voltage', 'Рабочее напряжение')
EIRP = ('ეფექტური გამოსხივების სიმძლავრე (EIRP)', 'Effective isotropic radiated power (EIRP)', 'Эффективная изотропная мощность излучения (EIRP)')
EIRP_V = '2.4000–2.4835 GHz: < 33 dBm (FCC), < 20 dBm (CE/SRRC/MIC); 5.725–5.850 GHz: < 33 dBm (FCC), < 30 dBm (SRRC), < 14 dBm (CE)'

SPECS = [
    {'id': 'platform', 'title': ('საჰაერო პლატფორმა', 'Aerial platform', 'Летная платформа'), 'blocks': [
        (('ძირითადი პარამეტრები', 'Basic parameters', 'Основные параметры'), [
            (('გაბარიტები', 'Overall dimensions', 'Габариты'), (
                '1799×1808×767 მმ (პროპელერები დაკეცილი, RevoSpray 5-ით)\n1799×1808×989 მმ (პროპელერები დაკეცილი, RevoCast 5-ით)\n1057×1017×817 მმ (პროპელერები და მკლავები დაკეცილი, RevoSpray 5-ით)\n3252×3257×767 მმ (პროპელერები და მკლავები გაშლილი, RevoSpray 5-ით)',
                '1799×1808×767 mm (propellers folded, RevoSpray 5)\n1799×1808×989 mm (propellers folded, RevoCast 5)\n1057×1017×817 mm (propellers & arms folded, RevoSpray 5)\n3252×3257×767 mm (propellers & arms unfolded, RevoSpray 5)',
                '1799×1808×767 мм (винты сложены, RevoSpray 5)\n1799×1808×989 мм (винты сложены, RevoCast 5)\n1057×1017×817 мм (винты и лучи сложены, RevoSpray 5)\n3252×3257×767 мм (винты и лучи разложены, RevoSpray 5)')),
            (('წონა (ცარიელი)', 'Empty weight', 'Масса без нагрузки'), (
                '56 კგ (RevoSpray სისტემით და B141050 ბატარეებით)\n60 კგ (RevoCast 5-ით და B141050 ბატარეებით, შესხურების ღეროების გარეშე)',
                '56 kg (with RevoSpray system & B141050 batteries)\n60 kg (with RevoCast 5 & B141050 batteries; no spray rods)',
                '56 кг (с системой RevoSpray и батареями B141050)\n60 кг (с RevoCast 5 и батареями B141050, без штанг)')),
            (('ძრავების დიაგონალური ღერძთაშორისი', 'Diagonal motor wheelbase', 'Диагональная колесная база моторов'), u(2335, MM)),
            (('მკლავის მასალა', 'Arm material', 'Материал лучей'), ('ალუმინის შენადნობი', 'Aluminium alloy', 'Алюминиевый сплав')),
            (('დაცვის კლასი', 'Protection rating', 'Класс защиты'), 'IPX6K'),
            (('მაქს. ასაფრენი წონა', 'Maximum takeoff weight', 'Максимальная взлетная масса'), (
                '136 კგ (შეწამვლისას)\n140 კგ (გაფანტვისას, ღეროების გარეშე)',
                '136 kg (spraying)\n140 kg (spreading, spray rods excluded)',
                '136 кг (опрыскивание)\n140 кг (разбрасывание, без штанг)')),
        ]),
        (('ფრენის პარამეტრები', 'Flight parameters', 'Параметры полета'), [
            (('ზუსტი პოზიციონირება RTK მონაცემების დაყოვნებისას', 'High-precision positioning with RTK data latency', 'Точное позиционирование при задержке данных RTK'), ('≤ 600 წმ', '≤ 600 s', '≤ 600 с')),
            (('მაქს. ფრენის მანძილი', 'Maximum flight distance', 'Максимальная дальность полета'), u(2000, M)),
            (('მაქს. ფრენის სიჩქარე', 'Maximum flight speed', 'Максимальная скорость полета'), (
                '20 მ/წმ (70 კმ/სთ) ¹', '20 m/s (70 km/h) ¹', '20 м/с (70 км/ч) ¹')),
            (('რეკომენდებული სამუშაო ტემპერატურა', 'Recommended operating temperature', 'Рекомендуемая рабочая температура'), '0 ~ 40 ℃'),
            (('ჰოვერის სიზუსტე (კარგი GNSS სიგნალი)', 'Hovering precision (good GNSS signal)', 'Точность зависания (хороший сигнал GNSS)'), (
                'RTK ჩართული: ± 10 სმ (ჰორიზ.), ± 10 სმ (ვერტ.)\nRTK გამორთული: ± 0.6 მ (ჰორიზ.), ± 0.3 მ (ვერტ.)',
                'RTK enabled: ± 10 cm (horizontal), ± 10 cm (vertical)\nRTK disabled: ± 0.6 m (horizontal), ± 0.3 m (vertical)',
                'RTK включен: ± 10 см (гориз.), ± 10 см (верт.)\nRTK выключен: ± 0.6 м (гориз.), ± 0.3 м (верт.)')),
            (('მაქს. ფრენის სიმაღლე', 'Maximum flight height', 'Максимальная высота полета'), u(100, M)),
        ]),
    ]},
    {'id': 'propulsion', 'title': ('სამოძრაო სისტემა', 'Propulsion system', 'Силовая установка'), 'blocks': [
        (('ძრავა', 'Motor', 'Мотор'), [
            (QTY, '4'),
            (('მაქს. წევა (ერთი ძრავა)', 'Maximum thrust (single motor)', 'Максимальная тяга (один мотор)'), u(56, KG)),
            (('ნომინალური სიმძლავრე (ერთი ძრავა)', 'Rated power (single motor)', 'Номинальная мощность (один мотор)'), u(4850, W)),
        ]),
        (('სიჩქარის ელექტრონული რეგულატორი (ESC)', 'Electronic speed controller (ESC)', 'Электронный регулятор скорости (ESC)'), [
            (('მაქს. გამომავალი დენი (30 წმ)', 'Maximum output current (30 s)', 'Максимальный выходной ток (30 с)'), u(380, A)),
            (('უწყვეტი სამუშაო დენი', 'Continuous operating current', 'Длительный рабочий ток'), u(140, A)),
        ]),
        (('დასაკეცი პროპელერი', 'Foldable propeller', 'Складной винт'), [
            (('მასალა', 'Material', 'Материал'), ('ნახშირბადის ბოჭკოს კომპოზიტი', 'Carbon fiber composite', 'Углепластиковый композит')),
            (('დიამეტრი', 'Diameter', 'Диаметр'), u(1600, MM)),
        ]),
    ]},
    {'id': 'revospray', 'title': ('XAG RevoSpray 5 — შეწამვლის სისტემა', 'XAG RevoSpray 5 — spraying system', 'XAG RevoSpray 5 — система опрыскивания'), 'blocks': [
        (('ჭკვიანი ავზი', 'Smart liquid tank', 'Умный бак'), [
            (('ნომინალური მოცულობა', 'Rated capacity', 'Номинальный объем'), u(80, L)),
            (('მაქს. ტვირთი', 'Maximum payload', 'Максимальная нагрузка'), u(80, KG)),
        ]),
        (('ცენტრიდანული საქშენი', 'Centrifugal atomizing nozzle', 'Центробежная форсунка'), [
            (QTY, '2'),
            (('წვეთის ზომა', 'Droplet size', 'Размер капли'), ('60 ~ 1500 μm (დამოკიდებულია გარემოსა და ხარჯზე)', '60 ~ 1500 μm (depends on environment, flow and other factors)', '60 ~ 1500 мкм (зависит от условий и расхода)')),
            (('დისკის ბრუნვის სიჩქარე', 'Spray disc rotational speed', 'Скорость вращения диска'), '1500 ~ 16000 RPM'),
            (('შეწამვლის სიგანე', 'Spray width', 'Ширина опрыскивания'), ('5 ~ 10 მ (დამოკიდებულია სიმაღლეზე, დოზაზე, გარემოზე)', '5 ~ 10 m (subject to flight height, dosage, environment)', '5 ~ 10 м (зависит от высоты, нормы, условий)')),
        ]),
        (('იმპელერიანი ტუმბო', 'Flexible impeller pump', 'Импеллерный насос'), [
            (QTY, '2'),
            (('ძაბვა', 'Voltage', 'Напряжение'), u(50, V)),
            (('მაქს. სამუშაო ხარჯი', 'Maximum operating flow rate', 'Максимальный рабочий расход'), ('32 ლ/წთ (ორი ტუმბო)', '32 L/min (dual pumps)', '32 л/мин (два насоса)')),
            (('მაქს. ხარჯი (ერთი ტუმბო)', 'Maximum flow rate (single pump)', 'Максимальный расход (один насос)'), ('0.5 ~ 16.0 ლ/წთ', '0.5 ~ 16.0 L/min', '0.5 ~ 16.0 л/мин')),
        ]),
    ]},
    {'id': 'revocast', 'title': ('XAG RevoCast 5 — გაფანტვის სისტემა', 'XAG RevoCast 5 — spreading system', 'XAG RevoCast 5 — система разбрасывания'), 'blocks': [
        (('გრანულების კონტეინერი', 'Granule container', 'Контейнер для гранул'), [
            (('ნომინალური მოცულობა', 'Rated capacity', 'Номинальный объем'), u(115, L)),
            (('მაქს. ტვირთი', 'Maximum load', 'Максимальная загрузка'), u(80, KG)),
        ]),
        (('ჭკვიანი ხრახნული მიმწოდებელი', 'Smart screw feeder', 'Умный шнековый питатель'), [
            (QTY, '1'),
            (('მაქს. ბრუნვის სიჩქარე', 'Maximum rotational speed', 'Максимальная скорость вращения'), '17000 RPM'),
            (('მაქს. გაფანტვის სიჩქარე', 'Maximum spread rate', 'Максимальная производительность'), ('300 კგ/წთ (შარდოვანით ტესტირებისას)', '300 kg/min (tested with urea)', '300 кг/мин (при испытании с карбамидом)')),
            (OPT, '0 ~ 40 ℃'),
            (('შენახვის ტემპერატურა', 'Storage temperature', 'Температура хранения'), '0 ~ 40 ℃'),
            (('გრანულის ზომა', 'Applicable granule size', 'Размер гранул'), ('1–10 მმ (მშრალი, მყარი გრანულები)', '1–10 mm (dry, solid granules)', '1–10 мм (сухие твердые гранулы)')),
        ]),
        (('ცენტრიდანული გამფანტავი დისკი', 'Centrifugal spreading disc', 'Центробежный разбрасывающий диск'), [
            (QTY, '1'),
            (('ეფექტური სიგანე', 'Effective spread width', 'Эффективная ширина'), ('5–9 მ (დამოკიდებულია სიმაღლეზე, გრანულაზე, დოზაზე)', '5–9 m (subject to flight height, granules, dosage)', '5–9 м (зависит от высоты, гранул, нормы)')),
        ]),
    ]},
    {'id': 'revosling', 'title': ('XAG RevoSling — ტვირთის გადატანა', 'XAG RevoSling — cargo', 'XAG RevoSling — перевозка груза'), 'blocks': [
        (None, [
            (('მაქს. ტვირთი', 'Maximum payload', 'Максимальная нагрузка'), u(80, KG)),
            (('წონა', 'Weight', 'Масса'), u(5.6, KG)),
            (('ზომები', 'Dimensions', 'Размеры'), ('859×595×532 მმ (მხოლოდ შასი)\n300×76×59 მმ (მხოლოდ ჭკვიანი კაუჭი)', '859×595×532 mm (landing gear only)\n300×76×59 mm (smart hook only)', '859×595×532 мм (только шасси)\n300×76×59 мм (только умный крюк)')),
            (OPT, '10 ~ 45 ℃'),
            (('თოკის საჭირო სიგრძე', 'Required rope length', 'Необходимая длина троса'), ('5 ~ 15 მ', '5 ~ 15 m', '5 ~ 15 м')),
            (('შენახვის ტემპერატურა', 'Storage temperature', 'Температура хранения'), '-20 ~ 60 ℃'),
            (('დამუხტვის ძაბვა / დენი', 'Charging voltage / current', 'Напряжение / ток зарядки'), '5 V / 2 A'),
            (('თავსებადი პულტი', 'Compatible remote controller', 'Совместимый пульт'), 'XAG SRC5, XAG SRC4'),
            (('თავსებადი დრონი', 'Compatible drone', 'Совместимый дрон'), 'XAG P150 Max, XAG P150 2024'),
        ]),
    ]},
    {'id': 'sensing', 'title': ('აღქმისა და დაბრკოლებების არიდების სისტემა', 'Sensing & avoidance system', 'Система обнаружения и облета препятствий'), 'blocks': [
        (('4D გამოსახულების რადარი', '4D imaging radar', '4D-радар'), [
            (MODEL, 'RD2488_25'),
            (('აღქმის დიაპაზონი', 'Sensing range', 'Дальность обнаружения'), ('1.5 ~ 100 მ', '1.5 ~ 100 m', '1.5 ~ 100 м')),
            (OPV, u(24, V)),
            (('ხედვის არე (FOV)', 'Field of view (FOV)', 'Поле зрения (FOV)'), ('ჰორიზ.: ±40°; ვერტ.: ±115°', 'Horizontal: ±40°; vertical: ±115°', 'Гориз.: ±40°; верт.: ±115°')),
            (('სიმძლავრე', 'Power', 'Мощность'), ('< 15 ვტ', '< 15 W', '< 15 Вт')),
            (('დაბრკოლების ფარდობითი სიმაღლე', 'Relative height of obstacle avoidance', 'Относительная высота облета'), ('≥ 1.5 მ', '≥ 1.5 m', '≥ 1.5 м')),
            (('სამუშაო სიხშირე', 'Operating frequency', 'Рабочая частота'), '24 GHz'),
            (('დაბრკოლების არიდების მანძილი', 'Obstacle avoidance distance', 'Дистанция облета'), ('2.5 მ (პროპელერის ბოლოდან დაბრკოლებამდე დამუხრუჭების შემდეგ)', '2.5 m (propeller tip to obstacle after braking to hover)', '2.5 м (от кончика винта до препятствия после торможения)')),
            (('აღქმის რეჟიმი', 'Sensing mode', 'Режим обнаружения'), 'Beamforming, 4D imaging'),
            (('არიდების მაქს. ფარდობითი სიჩქარე', 'Maximum relative speed of obstacle avoidance', 'Макс. относительная скорость облета'), ('≤ 13.8 მ/წმ ¹', '≤ 13.8 m/s ¹', '≤ 13.8 м/с ¹')),
        ]),
        (('FPV კამერა', 'FPV camera', 'FPV-камера'), [
            (('გარჩევადობა', 'Resolution', 'Разрешение'), '1920 × 1080'),
            (OPV, u(24, V)),
            (('კადრების სიხშირე', 'Frame rate', 'Частота кадров'), '30 fps'),
            (('ვიდეოს კოდირება', 'Video coding format', 'Формат кодирования'), 'H.265'),
            (('სენსორი', 'Image sensor', 'Сенсор'), ('1/2.7" CMOS-RGB, 5 MP', '1/2.7" CMOS-RGB, 5 MP effective', '1/2.7" CMOS-RGB, 5 Мп')),
            (('ფოკუსური მანძილი', 'Focal length', 'Фокусное расстояние'), u(1.83, MM)),
        ]),
    ]},
    {'id': 'power', 'title': ('ენერგოსისტემა', 'Power system', 'Система питания'), 'blocks': [
        (('XAG B141050 ჭკვიანი ბატარეა (SuperCharge)', 'XAG B141050 Smart SuperCharge Battery', 'Умная батарея XAG B141050 (SuperCharge)'), [
            (MODEL, 'M1PPA141050AH'),
            (('ნომინალური გამომავალი', 'Rated output', 'Номинальный выход'), '52.5 V / 140 A'),
            (('ტიპი', 'Type', 'Тип'), ('ლითიუმ-იონური პოლიმერული', 'Lithium-ion polymer', 'Литий-ионная полимерная')),
            (('მაქს. დამუხტვის დენი', 'Maximum charging current', 'Максимальный ток зарядки'), u(120, A)),
            (('ნომინალური ტევადობა', 'Rated capacity', 'Номинальная емкость'), '20000 mAh'),
            (CHT, '10 ~ 45 ℃'),
        ]),
        (('XAG CM13600S დამტენი', 'XAG CM13600S Charger', 'Зарядное устройство XAG CM13600S'), [
            (MODEL, 'M2CM13600CH'),
            (('შემავალი ძაბვა', 'Input voltage', 'Входное напряжение'), 'AC 100–120 V ~ 50/60 Hz, 15.0 A\nAC 220–240 V ~ 50/60 Hz, 16.0 A'),
            (('დამუხტვის ადაპტერი', 'Charging adaptor quantity', 'Количество адаптеров'), '1'),
            (('გამომავალი ძაბვა', 'Output voltage', 'Выходное напряжение'), '59.92 V ⎓ 21 A\n59.92 V ⎓ 55 A'),
            (OPT, '-20 ~ 40 ℃'),
        ]),
        (('XAG GC4000+ დამუხტვის სადგური (გენერატორი)', 'XAG GC4000+ Auto SuperCharge Station', 'Зарядная станция XAG GC4000+ (генератор)'), [
            (MODEL, 'GC4000+'),
            (('წონა', 'Net weight', 'Масса нетто'), u(31.5, KG)),
            (('საწვავის ავზი', 'Fuel tank capacity', 'Топливный бак'), u(15, L)),
            (('ძრავის მოცულობა', 'Total displacement', 'Рабочий объем'), '223 cc'),
            (OPV, '56.6 V DC'),
            (('ნომინალური დენი', 'Rated current', 'Номинальный ток'), '75 ± 3 A'),
            (('ნომინალური დამუხტვის სიმძლავრე', 'Rated charging power', 'Номинальная мощность зарядки'), u(3400, W)),
            (('მაქს. გამომავალი სიმძლავრე', 'Maximum power output', 'Максимальная выходная мощность'), u(5100, W)),
        ]),
        (('ბატარეის გამაგრილებელი კოშკი', 'Battery cooling tower', 'Охлаждающая башня для батарей'), [
            (MODEL, 'M8BC5B'),
            (('გამოსასვლელები', 'Output plugs', 'Выходные разъемы'), '1'),
            (('მაქს. მოცულობა', 'Max capacity', 'Максимальный объем'), u(5, L)),
            (('შემავალი ძაბვა', 'Input voltage', 'Входное напряжение'), '39 ~ 60 V'),
            (('სიმძლავრე', 'Power', 'Мощность'), u(80, W)),
            (('წყლის ხარჯი', 'Water consumption', 'Расход воды'), ('≤ 500 მლ/სთ', '≤ 500 ml/h', '≤ 500 мл/ч')),
        ]),
    ]},
    {'id': 'control', 'title': ('კავშირი და მართვა', 'Communication & control', 'Связь и управление'), 'blocks': [
        (('XAG ACS4 მართვის ჯოისტიკი', 'XAG ACS4 Control Stick', 'Джойстик управления XAG ACS4'), [
            (MODEL, 'M3ACS4AH'),
            (('სამუშაო სიხშირე', 'Operating frequency', 'Рабочая частота'), '2.400–2.4835 GHz; 5.725–5.850 GHz'),
            (('ბატარეის ტევადობა', 'Battery capacity', 'Емкость батареи'), '2600 mAh'),
            (('სიგნალის დიაპაზონი (ჩარევის გარეშე)', 'Signal range (no interference)', 'Дальность сигнала (без помех)'), 'FCC: 2000 m; SRRC: 2000 m; CE/MIC: 1000 m'),
            (EIRP, EIRP_V),
            (OPT, '-10 ~ 40 ℃'),
            (CHT, '5 ~ 40 ℃'),
            (('თავსებადი', 'Compatible products', 'Совместимость'), 'XAG P150 Max, XAG P150, XAG P60'),
        ]),
        (('XAG SRC5 ჭკვიანი მართვის პულტი', 'XAG SRC5 Smart Remote Controller', 'Умный пульт XAG SRC5'), [
            (MODEL, 'M3SRC5A'),
            (('სამუშაო სიხშირე', 'Operating frequency', 'Рабочая частота'), '2.4000–2.4835 GHz; 5.725–5.850 GHz'),
            (('ბატარეის ტევადობა', 'Battery capacity', 'Емкость батареи'), '20000 mAh'),
            (EIRP, EIRP_V),
            (OPT, '-10 ~ 40 ℃'),
            (CHT, '5 ~ 40 ℃'),
            (('თავსებადი', 'Compatible products', 'Совместимость'), 'XAG P150 Max'),
        ]),
        (('XAG XRTK7 მობილური სადგური', 'XAG XRTK7 Mobile Station', 'Мобильная станция XAG XRTK7'), [
            (MODEL, 'M3RTK7AH'),
            (('დამუხტვის ძაბვა', 'Charging voltage', 'Напряжение зарядки'), '5 V 3 A / 15 V 2 A'),
            (('დაცვის კლასი', 'Protection rating', 'Класс защиты'), 'IP65'),
            (('ბატარეის ტევადობა', 'Battery capacity', 'Емкость батареи'), '10000 mAh'),
            (('სიგნალის დიაპაზონი (ჩარევის გარეშე)', 'Signal range (no interference)', 'Дальность сигнала (без помех)'), u(2000, M)),
        ]),
    ]},
]

NOTE = (
    '¹ მაქსიმალური სიჩქარისას დაიცავით ადგილობრივი კანონები. 13.8 მ/წმ-ზე მეტ სიჩქარეზე დაბრკოლების არიდების წარუმატებლობის ალბათობა იზრდება — ფრენამდე მონიშნეთ ყველა დაბრკოლება. მახასიათებლები შეიძლება განსხვავდებოდეს გარემოს, ტემპერატურისა და გამოყენების მიხედვით. წყარო: XAG-ის ოფიციალური მახასიათებლები.',
    '¹ Observe local laws when flying at maximum speed. Above 13.8 m/s the probability of obstacle avoidance failure increases — mark all obstacles before operation. Performance may vary with environment, temperature and use. Source: official XAG specifications.',
    '¹ На максимальной скорости соблюдайте местное законодательство. При скорости выше 13.8 м/с вероятность сбоя облета препятствий растет — отметьте все препятствия перед работой. Характеристики могут меняться в зависимости от условий, температуры и эксплуатации. Источник: официальные характеристики XAG.',
)
HEADING = ('მახასიათებლები', 'Specifications', 'Характеристики')
INTRO = ('XAG P150 MAX-ის სრული ტექნიკური მახასიათებლები — დრონი, შეწამვლის და გაფანტვის სისტემები, ენერგია და მართვა.',
         'Full technical specifications of the XAG P150 MAX — drone, spraying and spreading systems, power and control.',
         'Полные технические характеристики XAG P150 MAX — дрон, системы опрыскивания и разбрасывания, питание и управление.')
