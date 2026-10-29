#!/usr/bin/env python3
"""
Generate: 2026_INVESTITURE_LIST_AND_ACCESSORIES.docx
Requirements:  pip install python-docx
"""

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.section import WD_ORIENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ----------------------------------------------------------------------
# 1. PRICING RULES  (cost, markup, venue) — total = cost + markup + venue
# ----------------------------------------------------------------------
# All certificates share the same price: cost 15, markup 5, venue 15
PRICES = {
    'scarf_pf':     (120, 20, 10),
    'scarf_adv':    (120, 20, 10),
    'syl_scarf':    (120, 20, 10),
    'mg_pin':       (20, 20, 5),
    'syl_pin':      (20, 20, 5),
    'mg_cert':      (15, 5, 15),
    'syl_cert':     (15, 5, 15),
    'cmt_cert':     (15, 5, 15),
    'gold_cert':    (15, 5, 15),      # Gold Award certificate
    'silver_cert':  (15, 5, 15),      # Silver Award certificate
    'gold_medal':   (55, 15, 0),
    'silver_medal': (50, 10, 0),
    'wagon':        (120, 10, 0),
    'shirt':        (400, 50, 0),
}

ITEM_KEYS = ['scarf_pf','scarf_adv','syl_scarf','mg_pin','syl_pin',
             'mg_cert','syl_cert','cmt_cert','gold_cert','silver_cert',
             'gold_medal','silver_medal','wagon','shirt']

ITEM_LABELS = ['PF Scarf','Adv Scarf','SYL Scarf','MG Pin','SYL Pin',
               'MG Cert','SYL Cert','CMT Cert','Gold Cert','Silver Cert',
               'Gold Medal','Silver Medal','Wagon','Shirt']

# (label, first_item_idx, last_item_idx, [(sub_label, item_idx), ...] or None)
PRICE_GROUPS = [
    ('Scarf',            0,  1, [('Pathfinder', 0), ('Adventurer', 1)]),
    ('SYL Scarf',        2,  2, None),
    ('MG Pin',           3,  3, None),
    ('SYL Pin',          4,  4, None),
    ('Certificates',     5,  9, [('MG', 5), ('SYL', 6), ('CMT', 7),
                                 ('Gold Award', 8), ('Silver Award', 9)]),
    ('Medal',           10, 11, [('Gold', 10), ('Silver', 11)]),
    ('Metallic Wagon',  12, 12, None),
    ('Shirt',           13, 13, None),
]

CATEGORIES = ['MG', 'SYL', 'CMT', 'Award Recipient', 'Church Heritage']

# ----------------------------------------------------------------------
# 2. ITEM DETECTION
# ----------------------------------------------------------------------
def detect_items(acc, cat=''):
    a = acc.lower()
    c = cat.lower()
    items = set()

    # ---- Scarves ------------------------------------------------------
    if 'pathfinder scarf' in a or 'mg scarf' in a:
        items.add('scarf_pf')
    if 'adventurer scarf' in a:
        items.add('scarf_adv')
    if 'syl scarf' in a:
        items.add('syl_scarf')

    # ---- Pins ---------------------------------------------------------
    if 'mg pin' in a:
        items.add('mg_pin')
    elif 'pin' in a and 'syl' not in a and 'mg' in c:
        items.add('mg_pin')
    if 'syl pin' in a:
        items.add('syl_pin')
    elif 'pin' in a and 'syl' in c:
        items.add('syl_pin')

    # ---- Certificates (specific first) --------------------------------
    if 'gold award certificate' in a or 'gold certificate' in a or 'gold cert' in a:
        items.add('gold_cert')
    if 'silver award certificate' in a or 'silver certificate' in a or 'silver cert' in a:
        items.add('silver_cert')
    if 'mg certificate' in a or 'mg cert' in a:
        items.add('mg_cert')
    if 'syl certificate' in a or 'syl cert' in a:
        items.add('syl_cert')
    if 'cmt certificate' in a or 'cmt cert' in a:
        items.add('cmt_cert')
    # Fallback: lone "certificate" keyword → use category to decide
    if ('certificate' in a
            and not any(x in a for x in
                        ['mg cert','syl cert','cmt cert',
                         'gold cert','silver cert',
                         'gold award cert','silver award cert',
                         'award certificate'])):
        if 'mg' in c:
            items.add('mg_cert')
        elif 'syl' in c:
            items.add('syl_cert')
        elif 'cmt' in c:
            items.add('cmt_cert')

    # ---- Medals -------------------------------------------------------
    if 'gold award' in a:
        items.add('gold_medal')
    if 'silver award' in a:
        items.add('silver_medal')

    # ---- Others -------------------------------------------------------
    if 'metallic wagon' in a or 'mg-wagon' in a:
        items.add('wagon')
    if 'shirt' in a:
        items.add('shirt')

    return items

# ----------------------------------------------------------------------
# 3. DATA
# ----------------------------------------------------------------------
DATA = [
("AVONDALE MISSION DISTRICT", False, [
 ("Charles Nyimba","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Mupeta Mushibwe","MG","Adventurer Scarf, Silver Award, MG Certificate, MG Pin"),
 ("Ndabase Msimuko","MG","Adventurer Scarf, Silver Award, MG Certificate, MG Pin"),
 ("Simukanga Zacheus","MG","Pathfinder scarf, MG pin, MG certificate, Class A shirt"),
 ("Stephanie D.K Mwansa","Church Heritage","Certificate"),
]),
("AVONDALE SDA CHURCH", False, [
 ("Chipo Muchanga","SYL","SYL scarf, SYL pin, SYL certificate"),
 ("Chuma Hinweene","MG","Pathfinder scarf, MG pin, MG certificate"),
]),
("BEDROCK MISSION DISTRICT", False, [
 ("Beaton C. Lyambai","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
]),
("BRENTWOOD DRIVE SDA CHURCH DISTRICT", False, [
 ("Domingo Raymond Chikesenge","Award Recipient","Silver Award"),
 ("Esther M. Siankuku","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Jill Nachula","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Kasabila Kandatula","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Mable B. Nendzwe","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Maxine Mwamba","Award Recipient","Silver Award"),
 ("Mutinta Mweemba","MG","Adventurer scarf, MG pin, MG certificate, Silver Award"),
 ("Natasha C Gamela","MG","Pathfinder scarf"),
 ("Stars Mulomba","MG","Adventurer scarf, MG pin, MG certificate, Silver Award"),
 ("Thabo Bwanali","MG","Adventurer scarf, MG pin, MG certificate"),
 ("Thandiwe Ulaya","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Thukuza Z. Tembo","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
]),
("CHAINAMA SDA CHURCH", False, [
 ("Abigail Hamoonga","MG","Pathfinder scarf, MG pin, MG certificate"),
 ("Barbara Chipango","MG","Pathfinder Scarf, MG Pin, MG Certificate, Gold Award"),
 ("Beene Banji","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Bupe Faith Bwanali","MG","Pathfinder Scarf, MG pin, MG certificate, Silver Award"),
 ("Caroline Mweemba","SYL","SYL scarf, SYL pin, SYL certificate, Gold Award"),
 ("Chama Shebele","SYL","SYL scarf, SYL pin, SYL certificate, Gold Award"),
 ("Chibuye Princess","Award Recipient","Silver Award certificate, Silver Award"),
 ("Chipango Barbara","MG","Pathfinder scarf, MG pin, MG certificate, Gold Award"),
 ("Chishimba Racheal","MG","Pathfinder Scarf, MG Certificate, Silver Award"),
 ("Chisomo Kaala","Award Recipient","Gold Award certificate, Gold Award"),
 ("Constance Musonda","Award Recipient","Silver Award certificate, Silver Award"),
 ("Daniel Chongo","CMT","CMT certificate"),
 ("Dorcas Chiwawa","SYL","SYL scarf, SYL pin, SYL certificate"),
 ("Elijah Sikunga","Award Recipient","Gold Award certificate, Gold Award"),
 ("Esther Norah Mwenda","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Eunice Mulesu","MG","Silver Award"),
 ("Handson Kalunde","MG","MG Certificate, Pathfinder Scarf, Gold Award, MG Pin"),
 ("Japhet Moyo","CMT","CMT certificate"),
 ("Jasper Soko","MG","Adventurer Scarf, MG Pin, MG Certificate, Gold Award"),
 ("Kalungwe Taonga","MG","Pathfinder Scarf, MG Pin, MG Certificate, Silver Award"),
 ("Karena Mwinga","MG","Pathfinder scarf, MG pin, MG certificate"),
 ("Karren Mwinga","MG","Pathfinder Scarf, MG Pin, MG Certificate, Silver Award"),
 ("Kerren Nakaazwe","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Linda Sakayombo","SYL","SYL scarf, SYL pin, SYL certificate, Gold Award"),
 ("Lubinda Walusiku","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Lydia Chipili","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Maluba Moonde","MG","Pathfinder Scarf, MG Pin, Silver Award, MG Certificate"),
 ("Milimo Chrissy Mwinga","Award Recipient","Gold Award certificate, Gold Award"),
 ("Monica Nikhuwa","Award Recipient","Silver Award certificate, Silver Award"),
 ("Moola Maluba","Award Recipient","Silver Award certificate, Silver Award"),
 ("Moses Mukwala","CMT","CMT certificate"),
 ("Mufundisi Esther","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Musonda K Mwelwa","MG","Pathfinder scarf, MG pin, MG certificate"),
 ("MUTALE DORCAS MPUNDU","CMT","CMT certificate"),
 ("Mwale Shadrick","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Mwenya Benny","Award Recipient","Silver Award certificate, Silver Award"),
 ("Mwimbwa Mulenga","SYL","SYL scarf, SYL pin, SYL certificate, Gold Award"),
 ("Namukolo Mundia","SYL","SYL scarf, SYL pin, SYL certificate, Gold Award"),
 ("Nasalifya Shezongo","Award Recipient","Gold Award certificate, Gold Award"),
 ("Natasha Chiyuka","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Patience Siwale","SYL","SYL scarf, SYL pin, SYL certificate, Gold Award"),
 ("Peter Nkhwani","SYL","SYL scarf, SYL pin, SYL certificate, CMT certificate, Gold Award"),
 ("Rita Sianga","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Ruth Mwenya","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award, Medal"),
 ("Samuel Makungu","Award Recipient","Silver Award certificate, Silver Award"),
 ("Samuel Mufaya","Award Recipient","Silver Award certificate, Silver Award"),
 ("Sibongile Shakemba","MG","Adventurer Scarf, MG Certificate, MG Pin"),
 ("Soko Jasper","Award Recipient","Silver Award certificate, Silver Award"),
 ("Taonga Kalungwe","Award Recipient","Silver Award certificate, Silver Award"),
 ("Teddy Nawa","MG","Pathfinder scarf, MG pin, MG certificate, Gold Award"),
 ("Victor Mwambela","Award Recipient","Silver Award certificate, Silver Award"),
 ("Watopa Chipango","CMT","CMT certificate"),
]),
("CHALIMBANA MISSION DISTRICT", False, [
 ("Gamaliel Tembo","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award, Medal"),
 ("Laston Mufaya","MG","Pathfinder scarf, MG pin, MG certificate"),
]),
("CHILENJE MISSION DISTRICT", False, [
 ("Anita M. Chishala","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Bernard Mudenda","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Catherine Mpundu Chisenga","MG","Pathfinder scarf, MG pin, Silver Award, Certificate"),
 ("Chola Kabika Kakunta","MG","MG Certificate, MG Pin, Adventurer Scarf, Silver Award"),
 ("Cletus Mwanangombe","MG","Adventurer Scarf, MG Pin, Certificate, Silver Award, Metallic Wagon"),
 ("Dale Mulilo Sikute","MG","Adventurer Scarf, MG Pin, MG Certificate, Silver Award"),
 ("Emeldah Chipala","SYL","SYL scarf, SYL pin, SYL certificate"),
 ("Enock Sangandu","MG","Adventurer Scarf, MG Pin, MG Certificate, Silver Award"),
 ("Esther Malipilo","MG","Adventurer Scarf, MG Pin, MG Certificate, Silver Award"),
 ("Fridah M. Chanda","MG","Pathfinder scarf, MG pin, MG certificate, Gold Award"),
 ("Hamane Victor","MG","MG Certificate, MG Pin, Adventurer Scarf, Silver Award"),
 ("Henry Kazungo","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Hildah Nayanda","MG","Pathfinder Scarf, MG Pin, Silver Award, Certificate"),
 ("Isabel M. Lumina","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Lizzie Hacombwa","MG","Pathfinder Scarf, MG Pin, Silver Award, Certificate"),
 ("Lloyd Kapambwe","MG","Pathfinder Scarf, MG Pin, Silver Award, Certificate"),
 ("Lorna Chipeta","MG","Adventurer Scarf, MG Pin, MG Certificate, Silver Award"),
 ("Loveness Machiya","MG","Pathfinder Scarf, MG Pin, MG certificate, Silver Award"),
 ("Lucy Mooyo","SYL","SYL scarf, SYL Pin, SYL certificate, Silver Award"),
 ("Mazuba Beatrice Hambalulo","MG","Pathfinder scarf, MG pin, Silver Award"),
 ("Mislet Chirwa","MG","Pathfinder Scarf, MG Pin, Silver Award, Certificate"),
 ("Mumbi Lungu","CMT","MG pin, SYL pin, CMT certificate"),
 ("Mwinji Kaunda Lungu","MG","Adventurer Scarf, MG Pin, Silver Award, Certificate"),
 ("Ngaza Mwape Lungu","SYL","SYL Pin, SYL Scarf, Silver Award, Certificate"),
 ("Nsondo Simasokwe","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Priscilla Chisulo","SYL","SYL scarf, SYL pin, SYL certificate"),
 ("Sharon Namate","MG","Adventurer Scarf, MG Pin, Silver Award, Certificate"),
 ("Suwilanji Simuchimba","MG","Adventurer Scarf, MG Pin, Silver Award, Certificate"),
]),
("CHILIMBULU DISTRICT", False, [
 ("Faith Phiri","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Isabel Mizinga Lumina","MG","Pathfinder Scarf, MG Pin, MG certificate, Silver Award"),
 ("Muchindu Habeenzu","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Nasla Moonga","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Mulondole Mapenzi","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Stelia Kamocha","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
]),
("CHIPAPA DISTRICT", False, [
 ("Chimuka Chigabiwa","CMT","CMT certificate course; Counselor and Instructor"),
 ("Elvis Mutale","SYL","SYL scarf, SYL pin, SYL certificate"),
 ("Ivy Precious Mwinga","SYL","SYL scarf, SYL pin, SYL certificate"),
]),
("CHONGWE MISSION DISTRICT", False, [
 ("Jacob Nakiube","MG","Adventurer scarf, MG pin, MG certificate"),
 ("Kondwani Kondowe","MG","Pathfinder scarf, Certificate and Pin"),
 ("Phanuel Chishiba","MG","Pathfinder scarf, MG pin, MG certificate"),
 ("Ruth Njobvu","MG","Pathfinder scarf, MG pin, MG certificate"),
 ("Sikute Mate","Church Heritage","Church Heritage certificate, October 2021 (reprint)"),
]),
("GOLFVIEW MISSION DISTRICT", False, [
 ("Angela Namweene Mwanskaba","MG","Pathfinder scarf, MG pin, MG certificate, Gold Award"),
 ("Annie Mumba","Award Recipient","Silver Award"),
 ("Betty Chilala","SYL","SYL scarf, SYL pin, SYL certificate, Gold Award"),
 ("Brenda Nakawala","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Brian Mulubwa Lukafu","MG","Adventurer Scarf, MG Pin, MG Certificate, Silver Award"),
 ("Cecilia Mubanga Chileshe","MG","Pathfinder scarf, MG pin, MG certificate, Gold Award"),
 ("Collard Mulongo","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Dalitso Magula","SYL","SYL scarf, SYL pin, SYL certificate, Gold Award"),
 ("Ilishebo Mwang elwa","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Esther Mumba","Award Recipient","Silver Award"),
 ("Eukeria Ng'andu","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Isaac Chumamunda","MG","Pathfinder scarf, MG pin, MG certificate"),
 ("Josiah Handiya","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Mercy Muleya","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Mirriam Bupe","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Misa Siandyomba","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Oscar Mudenda","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Patrick Kashimoto","Award Recipient","Gold Award"),
 ("Precious Kabinga","SYL","SYL scarf, SYL pin, SYL certificate, Gold Award"),
 ("Prisca Musanka","Award Recipient","Silver Award"),
 ("Saul Mwinga","MG","Adventurer Scarf, MG Pin, MG Certificate, Silver Award"),
 ("Silungwe Nkho ma","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Sophie Kango","Award Recipient","Silver Award"),
 ("Tozinah Fredrico","MG","Adventurer scarf, MG pin, MG certificate, Silver Award"),
 ("Vincent Muzoka","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Vitas Simutowe","CMT","CMT certificate"),
 ("Wornied Siabatwa","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
]),
("HIGHLANDS MISSION DISTRICT", False, [
 ("Funwell Habeene","SYL","SYL scarf, SYL pin, SYL certificate, CMT certificate"),
 ("Gregory Mukunto","SYL","SYL scarf, SYL pin, SYL certificate"),
 ("Humphrey Mumbali","SYL","SYL scarf, SYL pin, SYL certificate"),
 ("Lenard Chawa","SYL","SYL scarf, SYL pin, SYL certificate"),
 ("Maxwell Phiri","CMT","CMT Certificate only"),
 ("Mercy Makala","SYL","SYL scarf, SYL pin, SYL certificate"),
 ("Ruth Musonda","SYL","SYL scarf, SYL pin, SYL certificate"),
]),
("HORIZON CHURCH", False, [
 ("Brian Siakabeya","MG","Adventurer Scarf, MG Pin, MG Certificate, Gold Award"),
 ("Catherine Mulenga Mumba","MG","Adventurer Scarf, MG Pin, MG Certificate"),
 ("Diana Liseli Hatimbula","MG","Pathfinder scarf, MG pin, MG certificate"),
 ("Dollin Lisa Mutaka","MG","Adventurer Scarf, MG Pin, MG Certificate, Gold Award"),
 ("Highvie H. Hamududu","MG","Pathfinder scarf, MG pin, MG certificate"),
 ("Luyando Moonga","MG","Adventurer Scarf, MG Pin, MG Certificate, Gold Award"),
 ("Makala Muchoni","MG","Pathfinder scarf, MG pin, MG certificate"),
 ("Milimo Chooma","SYL","SYL scarf, SYL pin, SYL certificate, Gold Award"),
 ("Rejoice Muimui","MG","Adventurer Scarf, MG Pin, MG Certificate"),
 ("Sylvia Chibuye","MG","Adventurer Scarf, MG Pin, MG Certificate"),
 ("Thandie Maano","MG","Adventurer Scarf, MG Pin, MG Certificate, Gold Award"),
]),
("IBEX MISSION DISTRICT", False, [
 ("Artwel Kasengo","MG","MG Scarf and Certificate"),
 ("Artwell Kasengu","MG","Pathfinder scarf, MG pin, MG certificate"),
 ("Bwela Nchimunya Moombe","MG","Pathfinder Scarf, MG Pin, MG Certificate, Silver Award"),
 ("Chipo Chombela","SYL","SYL Scarf, SYL Pin, SYL Certificate, Silver Award"),
 ("Dora Malambo","MG","Pathfinder scarf, MG pin, Silver Award, MG certificate"),
 ("Evelyn Chomba","SYL","SYL Scarf, SYL Pin, SYL Certificate, Silver Award, CMT Certificate"),
 ("Felistus Chakwiya","MG","Pathfinder scarf, MG pin, Silver Award, MG certificate"),
 ("Fred Muleya","MG","Pathfinder scarf, MG pin, MG certificate"),
 ("Gift Chinga","MG","Pathfinder scarf, MG pin, MG certificate, Gold Award"),
 ("Nsamwa Njobvu","MG","Pathfinder Scarf, MG Pin, MG Certificate, Silver Award"),
 ("Priscilla Mukungu","MG","Pathfinder Scarf, MG Pin, MG Certificate, Silver Award"),
]),
("KABULONGA DISTRICT", False, [
 ("John B. Sikazwe","CMT","CMT certificate"),
 ("Mapiki Hamusonde","SYL","SYL scarf, SYL pin, SYL certificate, Silver Award"),
 ("Tricia Sikwati","SYL","SYL scarf, SYL pin, SYL certificate"),
 ("Beene Hamasamu","SYL","SYL scarf, SYL pin, SYL certificate, Gold Award"),
 ("Belgravia Mubanga","SYL","SYL scarf, SYL pin, SYL certificate, Gold Award"),
 ("Billy Siambizi","SYL","SYL scarf, SYL pin, SYL certificate, Gold Award"),
 ("Chansa Mukanga","SYL","SYL scarf, SYL pin, SYL certificate, Gold Award"),
 ("Chiedza Munyimani","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Chomba Chileshe","SYL","SYL scarf, SYL pin, SYL certificate, Gold Award"),
 ("Donvan Ngoma","MG","Pathfinder scarf, MG pin, MG certificate"),
 ("Doreen Musese","SYL","SYL scarf, SYL pin, SYL certificate"),
 ("Enoch Sinumbwa Sinumbwa","SYL","SYL scarf, SYL pin, SYL certificate"),
 ("Evans Kaamba","CMT","CMT certificate"),
 ("George Mushiba","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Howard Chiluba","SYL","SYL Certificate, SYL Pin, Gold Award"),
 ("Jam Ng'andu","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Kanunga Kazila","SYL","SYL scarf, SYL pin, SYL certificate, Gold Award"),
 ("Koyuma Siachombe","SYL","SYL scarf, SYL pin, SYL certificate, Gold Award"),
 ("Lotty Mario Chongo","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Lumbwe Mweendalubi","SYL","SYL scarf, SYL pin, SYL certificate, Gold Award"),
 ("Maureen Kasempa","MG","Pathfinder scarf, MG pin, MG certificate"),
 ("Melody Phiri","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Modia Sibbumbe","SYL","SYL scarf, SYL pin, SYL certificate, Gold Award"),
 ("Naomi Hamamba","SYL","SYL scarf, SYL pin, SYL certificate, Gold Award"),
 ("Nowanga Mubiana","SYL","SYL scarf, SYL pin, SYL certificate, Gold Award"),
 ("Penelope Hamoonga","SYL","SYL scarf, SYL pin, SYL certificate, Gold Award"),
 ("Phaides Moonga","SYL","SYL scarf, SYL pin, SYL certificate, Gold Award"),
 ("Pretty Siamwanja","SYL","SYL scarf, SYL pin, SYL certificate, Gold Award"),
 ("Rebecca Biyela","SYL","SYL scarf, SYL pin, SYL certificate, Gold Award"),
 ("Rowena Hamoonga","SYL","SYL scarf, SYL pin, SYL certificate, Gold Award"),
 ("Rutendo Munyimani","MG","Pathfinder Scarf, Pin, Certificate, Silver Award"),
 ("Shastry Maambo","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Walter Machona","SYL","SYL scarf, SYL pin, SYL certificate, Gold Award"),
 ("Watson Hachilutu","SYL","SYL scarf, SYL pin, SYL certificate, Gold Award"),
]),
("KAFUE MISSION DISTRICT", False, [
 ("Angela Mwitumwa","SYL","Award"),
 ("Annie Mwaakwe","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Banda Peter Remnant","Award Recipient","Gold Award"),
 ("Besa Chitunga","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Collet Matimba","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Collins Frederick Miyoba","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Elizabeth Banda","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Emmanuel Cheelo","MG","Adventurer Scarf, MG Pin, MG Certificate, Silver Award"),
 ("Huldah Malaw","SYL","SYL scarf, SYL pin, SYL certificate"),
 ("Idah Mutinta Halob","Award Recipient","Gold Award"),
 ("John Mapulanga","SYL","SYL scarf, SYL pin, SYL certificate"),
 ("John Simunji","MG","Adventurer Scarf, MG Pin, MG Certificate"),
 ("Joyce Shumba","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Kerryson Kaale","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Malama Kambele","MG","Pathfinder Scarf, MG Pin, MG Certificate, Silver Award"),
 ("Maranatha Chamalombo","Award Recipient","Silver Award"),
 ("Mary Mweele","MG","Pathfinder Scarf, Silver Award, MG Certificate, MG-wagon"),
 ("Mercy Sepiso","SYL","SYL scarf, SYL pin, SYL certificate"),
 ("Milimo Chinjila Katila","MG","Pathfinder scarf, MG pin, MG certificate"),
 ("Milimo Katila","Award Recipient","Silver Award"),
 ("Morai Malambo","SYL","SYL scarf, SYL pin, SYL certificate"),
 ("Moses Nalungwana","MG","Adventurer Scarf, MG Pin, MG Certificate, Silver Award"),
 ("Muleya Hamalube","MG","Adventurer Scarf, MG Pin, MG Certificate, Silver Award"),
 ("Namweemba Mubotu Muumba","SYL","SYL scarf, SYL pin, SYL certificate, Gold Award"),
 ("Nchimunya Hankalu","MG","Adventurer Scarf, MG Pin, MG Certificate, Silver Award"),
 ("Ndele Augustine","Award Recipient","Silver Award"),
 ("Nzale Kazubwe","MG","Adventurer Scarf, MG Pin, MG Certificate, Silver Award"),
 ("Olipa Mweemba","Award Recipient","Silver Award"),
 ("Pamela Chulu","Award Recipient","Silver Award"),
 ("Patrick Mabbe","MG","Pathfinder scarf, MG pin, MG certificate"),
 ("Raymond Kaima","Award Recipient","Silver Award"),
 ("Regina Kaima","Award Recipient","Silver Award"),
 ("Santrona Musonda","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Setrina Daka","Award Recipient","Silver Award"),
 ("Silio Sililo","Award Recipient","Gold Award"),
]),
("LIBALA DISTRICT", False, [
 ("Alice Matanda","SYL","SYL scarf, SYL pin, SYL certificate"),
 ("Blessings Mweemba","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Cynthia Hamweene","MG","Adventurer scarf, MG pin, MG certificate, Silver Award"),
 ("Esther Namwinga","SYL","SYL scarf, SYL pin, SYL certificate"),
 ("Judith Malambo","SYL","SYL scarf, SYL pin, SYL certificate"),
 ("Luo Mwanabene","SYL","SYL scarf, SYL pin, SYL certificate"),
 ("Melody M. Mbewe","CMT","CMT certificate"),
 ("Namooiya Maambo Malungo","SYL","SYL scarf, SYL pin, SYL certificate, Silver Award"),
 ("Noah Mwanauta","MG","MG certificate, Silver Award"),
 ("Saliya Musulwe","SYL","SYL scarf, SYL pin, SYL certificate"),
 ("Angela Malyango","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Annetty Chidrukula","MG","Adventurer scarf, MG pin, MG certificate, Silver Award"),
 ("Astridah Sikwalulwa","SYL","SYL scarf, SYL pin, SYL certificate"),
 ("Dismas K Musonda","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Esther Kunda","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Florence Kunda","SYL","SYL scarf, SYL pin, SYL certificate, Gold Award"),
 ("Loveness Chanda","SYL","SYL scarf, SYL pin, SYL certificate, Gold Award"),
 ("Mercy Mapenzi Hamoonga","MG","Adventurer scarf, MG pin, MG certificate, Silver Award"),
 ("Musenge Mato","SYL","Adventurer scarf, SYL pin, SYL certificate, Gold Award"),
 ("Naomi Namukonda","SYL","SYL scarf, SYL pin, SYL certificate"),
 ("Peggy Chibulamukowa","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Ruth Namukonda","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Susan Chilufya","SYL","SYL scarf, SYL pin, SYL certificate"),
 ("Victor Shangala","SYL","SYL scarf, SYL pin, SYL certificate"),
 ("Mudenda Gillian","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award, Gold Award"),
 ("Sakala Sophia","MG","Pathfinder scarf, MG pin, MG certificate, Gold Award, Silver Award"),
]),
("LWIIMBA MISSION DISTRICT", False, [
 ("Emmanuel H Munga","MG","MG scarf, MG pin, MG certificate, Silver Award"),
 ("Simon Hachoona","MG","MG scarf, MG pin, MG certificate, Silver Award"),
]),
("MTENDERE MISSION DISTRICT", False, [
 ("Kasamba Gwanu","MG","Pathfinder scarf, MG pin, MG certificate"),
 ("Lynn Bbilika","SYL","SYL scarf, SYL pin, SYL certificate, Gold Award"),
 ("Racheal B. Mweemba","Award Recipient","Silver Award"),
]),
("NJANJI MISSION DISTRICT", False, [
 ("Abigail Mwenda","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Barnabas Nikhosi","MG","Adventurer scarf, MG pin, MG certificate, Silver Award"),
 ("Bridget Mwamba","Award Recipient","Silver Award"),
 ("Brina Milambo","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Chewe Nkamba","MG","Adventurer scarf, MG pin, MG certificate, Silver Award"),
 ("Cushi Mweemba","MG","Adventurer scarf, MG pin, MG certificate, Silver Award"),
 ("Deborah Mwale","MG","Adventurer scarf, MG pin, MG certificate, Silver Award"),
 ("Gloria L. Kazenene","Award Recipient","Silver Award"),
 ("Kelvin Chipi","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Messiah Choonga Chisanga","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Mona Jempa","Award Recipient","Silver Award"),
 ("Mutepa S Banda","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Mutinta Maundu","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Mwangala Mundanya","Award Recipient","Silver Award"),
 ("Namwambwa Nchimunya Mweene","SYL","SYL scarf, SYL pin, SYL certificate, Gold Award"),
 ("Sarah Msimuko Kaanga","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Thandiwe Ng'onomo","SYL","SYL scarf, SYL pin, SYL certificate, Gold Award"),
 ("Wilson Ng'onomo","MG","Adventurer scarf, MG pin, MG certificate, Silver Award"),
]),
("PARKVIEW SDA CHURCH", False, [
 ("Caphard Saichinji","SYL","SYL scarf, SYL pin, SYL certificate, Gold Award"),
 ("Christencia Musonda","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Elgar Mbulo","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Faith Saichinji","SYL","SYL scarf, SYL pin, SYL certificate, Gold Award"),
 ("Joyce Chikondi Zulu","MG","Adventurer scarf, MG pin, Certificate, Silver Award"),
 ("Malawao Saichinji","SYL","SYL scarf, SYL pin, SYL certificate, Gold Award"),
 ("Newton Bwalya","MG","Pathfinder scarf, MG pin, MG certificate"),
 ("Precious Kaziya","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Tracy Kabiwe","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Treviah Hamabele","SYL","SYL scarf, SYL pin, SYL certificate, Gold Award"),
]),
("PCM", True, [
 ("Ackim Kanyomeka","Woodlands University College PCM","MG","Pathfinder scarf, MG pin, MG certificate"),
 ("Agatha Kamema","Cavendish University Longacres PCM","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Bethel C. Mwila","Woodlands University College PCM","MG","Pathfinder scarf, MG pin, MG certificate"),
 ("Blisswell Mweene","Kafue PCM","MG","Pathfinder scarf, MG pin, MG certificate"),
 ("Brian Ngwadzai","","MG","Pathfinder Scarf, MG Pin, MG Certificate, Silver Award"),
 ("Bwalya Besa","","MG","Adventurer Scarf, MG Certificate, MG Pin"),
 ("Cephas Chimusanya","St Luke's PCM","Award Recipient","Gold Award"),
 ("Chipo Chanda","","SYL","SYL Scarf, SYL Pin, SYL Certificate"),
 ("Chishomyo Ng'andu","Cavendish University Longacres PCM","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Chishomyo Ngandu","","MG","Adventurer Scarf, MG Certificate, MG Pin"),
 ("Chiyambi Zulu","","CMT","CMT Certificate"),
 ("Christabel Chilele","ICU PCM","MG","Pathfinder scarf, MG pin, MG certificate, Gold Award"),
 ("Fedson Munsanje","","MG","Pathfinder Scarf, MG Pin, MG Certificate, Silver Award"),
 ("Gift Mushiba","","SYL","SYL Pin, SYL Scarf, SYL Certificate, Silver Award Certificate and Medal"),
 ("Ivy Sianguba","Kafue PCM","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Jenipher Sakala","Kafue PCM","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Joel Kanjenje","","MG","Adventurer Scarf, MG Pin, MG Certificate"),
 ("Kambinda Vitumbo","","MG","Adventurer Scarf, MG Pin, MG Certificate, Gold Award"),
 ("Kholman Mwinga","Cavendish University Longacres PCM","SYL","SYL scarf, SYL pin, SYL certificate, Gold Award, Silver Award"),
 ("Luhanga Lingwell","","MG","Adventurer Scarf, MG Pin, MG Certificate, Silver Award"),
 ("Mackson Munkombwe","Cavendish University Longacres PCM","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Mandi Siabatwa","","MG","Pathfinder Scarf, MG Pin, MG Certificate, Silver Award"),
 ("Mirriam Gaamani","ICU PCM","SYL","SYL scarf, SYL pin, SYL certificate, Gold Award"),
 ("Monica Namwinga","Cavendish University Longacres PCM","SYL","SYL scarf, SYL pin, SYL certificate, Gold Award"),
 ("Mundia Matomola","Cavendish University Longacres PCM","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Nelson Zabangana","","MG","Pathfinder Scarf, MG Pin, MG certificate, Gold Award"),
 ("Owen Siamalala","Cavendish University Longacres PCM","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Patson Tembo","ICU PCM","CMT","CMT certificate"),
 ("Reason Miyanda","","SYL","SYL Pin, SYL Scarf, SYL Certificate, Gold Award"),
 ("Simbeye Isaac","","MG","Pathfinder Scarf, MG Pin, MG Certificate, Gold Award"),
 ("Simungala Cared","","MG","Pathfinder Scarf, MG Certificate, MG Pin, Gold Award, Silver Award, Metallic Wagon"),
 ("Winfridah Simataa","Kafue PCM","Award Recipient","Silver Award"),
]),
("RUFUNSA DISTRICT", False, [
 ("Charles Tembo","CMT","CMT certificate"),
 ("Chipo Mudaaala","SYL","SYL pin, SYL scarf, SYL certificate, Gold Award Certificate, Gold Award"),
 ("Christopher Mumpanshya","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Derrick Mutale","SYL","SYL scarf, SYL pin, SYL certificate, Silver Award"),
 ("Erick Biyela","CMT","CMT certificate"),
 ("Ignitius Mumba","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Linda Hatwaambo","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
]),
("SHANTUMBU MISSION DISTRICT", False, [
 ("Friday Munyenyya","SYL","SYL scarf, SYL pin, SYL certificate, Gold Award"),
 ("Joyce Chipakata","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
 ("Priscilla Hamainda","MG","Pathfinder scarf, MG pin, MG certificate, Silver Award"),
]),
("STATELODGE", False, [
 ("Micah Chisenga","CMT","Pathfinder scarf, Silver Award"),
 ("Nataziya Silungwe","MG","Adventurer scarf"),
 ("O'Brian Chibuye","MG","Pathfinder scarf"),
 ("Ruth Chibale","MG","Pathfinder scarf"),
 ("Sr. Sepiso Sitenge","SYL","SYL scarf, SYL pin, SYL certificate, Gold Award"),
]),
("WOODLANDS CENTRAL", False, [
 ("Alice Tembo","MG","Adventurer Scarf, MG Pin, MG Certificate, Silver Award"),
 ("Amusa Zaza","SYL","SYL scarf, certificate, Gold Award"),
 ("Julie Dabali","MG","Adventurer Scarf, MG Pin, MG Certificate, Silver Award"),
 ("Justina Chimuka","MG","Adventurer Scarf, MG Pin, MG Certificate, Silver Award"),
 ("Mable Kabisa","MG","Adventurer scarf, MG pin, certificate, Silver Award"),
 ("Mary T.C. Mutapa","MG","Adventurer Scarf, MG Pin, MG Certificate, Silver Award"),
 ("Mercy Mulando","MG","Adventurer scarf, MG pin, MG certificate, Silver Award"),
 ("Mervis Mukuwa","SYL","SYL scarf, SYL pin, certificate, Gold Award"),
 ("Moore Imasiku","MG","Pathfinder Scarf, MG Pin, MG Certificate, Silver Award"),
 ("Muleya Mwansa","MG","Adventurer scarf, MG pin, certificate, Silver Award"),
 ("Mulima N. Sapanoi","MG","Adventurer scarf, MG pin, certificate, Silver Award"),
 ("Mwape Seya","MG","Adventurer Scarf, MG Pin, MG Certificate, Silver Award"),
 ("Nchimunya Zaza","SYL","SYL scarf, SYL certificate, Gold Award"),
 ("Ngosa Funda Funda Lungu","MG","Adventurer Scarf, MG Pin, MG Certificate, Silver Award"),
 ("Obert Kasimbo","MG","Adventurer Scarf, MG Pin, MG Certificate, Silver Award"),
 ("Peggy Michello","MG","Adventurer Scarf, MG Pin, MG Certificate, Silver Award"),
 ("Priscilla Simvula","MG","Pathfinder Scarf, MG Pin, MG Certificate, Silver Award"),
 ("Saliya Syakateyo","SYL","SYL scarf, SYL pin, certificate, Gold Award and Silver Award"),
 ("Wilson Banda","MG","Pathfinder Scarf, MG Pin, MG Certificate, Silver Award"),
]),
]

# ----------------------------------------------------------------------
# 4. WORD HELPERS
# ----------------------------------------------------------------------
def set_cell_text(cell, text, bold=False, size=5, align='center', color=None, italic=False):
    cell.text = ''
    p = cell.paragraphs[0]
    p.alignment = {'center': WD_ALIGN_PARAGRAPH.CENTER,
                   'left':   WD_ALIGN_PARAGRAPH.LEFT,
                   'right':  WD_ALIGN_PARAGRAPH.RIGHT}[align]
    pf = p.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.line_spacing = 1.0
    run = p.add_run(str(text))
    run.bold = bold
    run.italic = italic
    run.font.size = Pt(size)
    run.font.name = 'Calibri'
    if color is not None:
        run.font.color.rgb = color
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER


def set_col_widths(table, widths_cm):
    table.autofit = False
    for row in table.rows:
        for i, w in enumerate(widths_cm):
            if i < len(row.cells):
                row.cells[i].width = Cm(w)


def shade(cell, color_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), color_hex)
    tcPr.append(shd)


def set_repeat_header(row):
    tr = row._tr
    trPr = tr.get_or_add_trPr()
    tblHeader = OxmlElement('w:tblHeader')
    tblHeader.set(qn('w:val'), 'true')
    trPr.append(tblHeader)


def add_page_number(paragraph):
    run = paragraph.add_run()
    fld1 = OxmlElement('w:fldChar'); fld1.set(qn('w:fldCharType'), 'begin')
    instr = OxmlElement('w:instrText'); instr.set(qn('xml:space'), 'preserve')
    instr.text = 'PAGE'
    fld2 = OxmlElement('w:fldChar'); fld2.set(qn('w:fldCharType'), 'end')
    run._r.append(fld1); run._r.append(instr); run._r.append(fld2)
    run.font.size = Pt(9)

# ----------------------------------------------------------------------
# 5. TABLE BUILDER
# ----------------------------------------------------------------------
def build_table(doc, rows_data, is_pcm):
    n_items     = len(ITEM_KEYS)                        # 14 items
    n_cats      = len(CATEGORIES)
    cat_start   = 3 if is_pcm else 2
    price_start = cat_start + n_cats
    price_cols  = n_items * 4                            # 56 price sub-columns
    acc_col     = price_start + price_cols
    n_cols      = acc_col + 1
    n_header    = 4
    n_cand      = len(rows_data)
    n_rows      = n_header + n_cand + 1                  # + totals row

    tbl = doc.add_table(rows=n_rows, cols=n_cols)
    tbl.style = 'Table Grid'
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER

    # ---- Header row 0 -------------------------------------------------
    tbl.cell(0, 0).merge(tbl.cell(3, 0))
    set_cell_text(tbl.cell(0, 0), '#', bold=True, size=7)

    tbl.cell(0, 1).merge(tbl.cell(3, 1))
    set_cell_text(tbl.cell(0, 1), 'Candidate Name', bold=True, size=7)

    if is_pcm:
        tbl.cell(0, 2).merge(tbl.cell(3, 2))
        set_cell_text(tbl.cell(0, 2), 'Location', bold=True, size=7)

    # Category main header
    tbl.cell(0, cat_start).merge(tbl.cell(0, cat_start + n_cats - 1))
    set_cell_text(tbl.cell(0, cat_start), 'Category', bold=True, size=7)

    for i, cat in enumerate(CATEGORIES):
        c = cat_start + i
        tbl.cell(1, c).merge(tbl.cell(3, c))
        set_cell_text(tbl.cell(1, c), cat, bold=True, size=5)

    # Prices main header
    tbl.cell(0, price_start).merge(tbl.cell(0, price_start + price_cols - 1))
    set_cell_text(tbl.cell(0, price_start), 'Prices (K)', bold=True, size=7)

    # Price group headers
    for label, s_idx, e_idx, subs in PRICE_GROUPS:
        cs = price_start + s_idx * 4
        ce = price_start + e_idx * 4 + 3
        if subs is None:
            tbl.cell(1, cs).merge(tbl.cell(2, ce))
            set_cell_text(tbl.cell(1, cs), label, bold=True, size=5)
        else:
            tbl.cell(1, cs).merge(tbl.cell(1, ce))
            set_cell_text(tbl.cell(1, cs), label, bold=True, size=5)
            for sub_label, idx in subs:
                cs2 = price_start + idx * 4
                ce2 = cs2 + 3
                tbl.cell(2, cs2).merge(tbl.cell(2, ce2))
                set_cell_text(tbl.cell(2, cs2), sub_label, bold=True, size=4)

    # Cost / Mkup / Venue / Total
    for i in range(n_items):
        base = price_start + i * 4
        set_cell_text(tbl.cell(3, base),     'Cost',  bold=True, size=3.5)
        set_cell_text(tbl.cell(3, base + 1), 'Mkup',  bold=True, size=3.5)
        set_cell_text(tbl.cell(3, base + 2), 'Venue', bold=True, size=3.5)
        set_cell_text(tbl.cell(3, base + 3), 'Total', bold=True, size=3.5)

    # Accessories main header
    tbl.cell(0, acc_col).merge(tbl.cell(3, acc_col))
    set_cell_text(tbl.cell(0, acc_col), 'Accessories / Awards', bold=True, size=7)

    # Shade + repeat header rows
    for r in range(n_header):
        for c in range(n_cols):
            try:
                shade(tbl.cell(r, c), 'D9E2F3')
            except Exception:
                pass
        try:
            set_repeat_header(tbl.rows[r])
        except Exception:
            pass

    # ---- Data rows ----------------------------------------------------
    tot_cost   = [0] * n_items
    tot_markup = [0] * n_items
    tot_venue  = [0] * n_items
    tot_total  = [0] * n_items
    item_count = [0] * n_items
    grand_cost = grand_markup = grand_venue = grand_total = 0

    for i, row in enumerate(rows_data):
        r = n_header + i
        if is_pcm:
            name, loc, cat, acc = row
        else:
            name, cat, acc = row
            loc = ''
        set_cell_text(tbl.cell(r, 0), str(i + 1), size=5)
        set_cell_text(tbl.cell(r, 1), name, size=5, align='left')
        if is_pcm:
            set_cell_text(tbl.cell(r, 2), loc, size=5, align='left')

        cat_u = cat.upper()
        ticks = {
            'MG':             'MG' in cat_u and 'CMT' not in cat_u,
            'SYL':            'SYL' in cat_u,
            'CMT':            'CMT' in cat_u,
            'Award Recipient':('AWARD' in cat_u) or ('RECIPIENT' in cat_u),
            'Church Heritage':'CHURCH HERITAGE' in cat_u,
        }
        for k, cname in enumerate(CATEGORIES):
            set_cell_text(tbl.cell(r, cat_start + k),
                          '✓' if ticks[cname] else '', size=6)

        items = detect_items(acc, cat)
        for k, key in enumerate(ITEM_KEYS):
            base = price_start + k * 4
            if key in items:
                c_, m_, v_ = PRICES[key]
                t_ = c_ + m_ + v_
                set_cell_text(tbl.cell(r, base),     str(c_), size=4)
                set_cell_text(tbl.cell(r, base + 1), str(m_), size=4)
                set_cell_text(tbl.cell(r, base + 2), str(v_), size=4)
                set_cell_text(tbl.cell(r, base + 3), str(t_), size=4)
                tot_cost[k]   += c_
                tot_markup[k] += m_
                tot_venue[k]  += v_
                tot_total[k]  += t_
                item_count[k] += 1
                grand_cost    += c_
                grand_markup  += m_
                grand_venue   += v_
                grand_total   += t_

        set_cell_text(tbl.cell(r, acc_col), acc, size=5, align='left')

    # ---- Totals row ---------------------------------------------------
    r = n_header + n_cand
    set_cell_text(tbl.cell(r, 0), '', size=5)
    set_cell_text(tbl.cell(r, 1), 'TOTAL', bold=True, size=6)
    if is_pcm:
        set_cell_text(tbl.cell(r, 2), '', size=5)
    for k in range(n_items):
        base = price_start + k * 4
        set_cell_text(tbl.cell(r, base),     str(tot_cost[k]),   bold=True, size=4)
        set_cell_text(tbl.cell(r, base + 1), str(tot_markup[k]), bold=True, size=4)
        set_cell_text(tbl.cell(r, base + 2), str(tot_venue[k]),  bold=True, size=4)
        set_cell_text(tbl.cell(r, base + 3), str(tot_total[k]),  bold=True, size=4)
    for c in range(n_cols):
        try:
            shade(tbl.cell(r, c), 'FFF2CC')
        except Exception:
            pass

    # ---- Column widths ------------------------------------------------
    if is_pcm:
        widths = ([0.30, 1.7, 1.3] + [0.32] * n_cats
                  + [0.36] * price_cols + [2.0])
    else:
        widths = ([0.30, 2.0] + [0.32] * n_cats
                  + [0.36] * price_cols + [2.2])
    widths = widths[:n_cols]
    while len(widths) < n_cols:
        widths.append(0.36)
    set_col_widths(tbl, widths)

    return {
        'candidates':  n_cand,
        'cost':        grand_cost,
        'markup':      grand_markup,
        'venue':       grand_venue,
        'total':       grand_total,
        'net':         grand_markup + grand_venue,
        'item_count':  item_count,
        'tot_cost':    tot_cost,
        'tot_markup':  tot_markup,
        'tot_venue':   tot_venue,
        'tot_total':   tot_total,
    }

# ----------------------------------------------------------------------
# 6. NOTES BELOW EACH TABLE
# ----------------------------------------------------------------------
def add_summary(doc, s, label=''):
    # Line 1 – headline totals
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after  = Pt(1)
    r = p.add_run(
        f"{label}"
        f"Candidates: {s['candidates']}   |   "
        f"Cost Price: K{s['cost']}   |   "
        f"Markup: K{s['markup']}   |   "
        f"Venue: K{s['venue']}   |   "
        f"Total Paid: K{s['total']}   |   "
        f"Net profit (Markup + Venue): K{s['net']}"
    )
    r.font.size = Pt(8)
    r.bold = True
    r.font.color.rgb = RGBColor(0x1F, 0x37, 0x64)

    # Line 2 – item counts
    p2 = doc.add_paragraph()
    p2.paragraph_format.space_before = Pt(0)
    p2.paragraph_format.space_after  = Pt(3)
    counts_str = '   |   '.join(
        f"{lbl}: {s['item_count'][i]}" for i, lbl in enumerate(ITEM_LABELS)
    )
    r2 = p2.add_run(f"Item counts: {counts_str}")
    r2.font.size = Pt(7)
    r2.italic = True
    r2.font.color.rgb = RGBColor(0x40, 0x40, 0x40)

    # Line 3 – per-item money breakdown
    p3 = doc.add_paragraph()
    p3.paragraph_format.space_before = Pt(0)
    p3.paragraph_format.space_after  = Pt(3)
    parts = []
    for i, lbl in enumerate(ITEM_LABELS):
        if s['item_count'][i] > 0:
            parts.append(
                f"{lbl}: cost K{s['tot_cost'][i]} / mkup K{s['tot_markup'][i]} "
                f"/ venue K{s['tot_venue'][i]} / total K{s['tot_total'][i]}"
            )
    if parts:
        r3 = p3.add_run("Per-item breakdown:  " + "   •   ".join(parts))
        r3.font.size = Pt(6.5)
        r3.font.color.rgb = RGBColor(0x60, 0x60, 0x60)

# ----------------------------------------------------------------------
# 7. BUILD DOCUMENT
# ----------------------------------------------------------------------
def main():
    doc = Document()

    section = doc.sections[0]
    section.orientation = WD_ORIENT.LANDSCAPE
    section.page_width  = Cm(29.7)
    section.page_height = Cm(21.0)
    section.left_margin   = Cm(0.6)
    section.right_margin  = Cm(0.6)
    section.top_margin    = Cm(0.7)
    section.bottom_margin = Cm(0.7)

    # ---------- Title block ----------
    h = doc.add_heading('2026 INVESTITURE LIST AND ACCESSORIES', level=0)
    h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in h.runs:
        run.font.color.rgb = RGBColor(0x1F, 0x37, 0x64)
        run.font.size = Pt(22)

    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rr = sub.add_run('ALL DISTRICTS / CHURCHES  —  UPDATED WITH ALL CORRECTIONS AND ADDITIONS')
    rr.italic = True
    rr.font.size = Pt(10)
    rr.font.color.rgb = RGBColor(0x40, 0x40, 0x40)

    # ---------- Legend ----------
    leg = doc.add_paragraph()
    leg.alignment = WD_ALIGN_PARAGRAPH.CENTER
    lr = leg.add_run(
        "How to read each table:  Category columns carry a tick (✓).  "
        "In the Prices block, each item has four sub-columns — "
        "Cost (base price), Mkup (markup), Venue (venue-hire contribution) and Total (= Cost + Mkup + Venue).  "
        "The Certificates group covers MG, SYL, CMT, Gold Award and Silver Award certificates (all priced the same).  "
        "Per-table notes list totals, item counts and per-item money breakdown."
    )
    lr.font.size = Pt(8)
    lr.italic = True
    lr.font.color.rgb = RGBColor(0x70, 0x70, 0x70)

    # ---------- Footer with page number ----------
    footer = section.footer
    fp = footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pre = fp.add_run('Page '); pre.font.size = Pt(9)
    add_page_number(fp)
    post = fp.add_run('  |  2026 Investiture List'); post.font.size = Pt(9)

    # ---------- Cumulative accumulator ----------
    n_items = len(ITEM_KEYS)
    cumulative = {
        'candidates': 0,
        'cost':       0,
        'markup':     0,
        'venue':      0,
        'total':      0,
        'net':        0,
        'item_count': [0] * n_items,
        'tot_cost':   [0] * n_items,
        'tot_markup': [0] * n_items,
        'tot_venue':  [0] * n_items,
        'tot_total':  [0] * n_items,
    }

    # ---------- District tables ----------
    for district_name, is_pcm, rows in DATA:
        hp = doc.add_heading(district_name, level=2)
        hp.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for run in hp.runs:
            run.font.color.rgb = RGBColor(0x1F, 0x37, 0x64)
            run.font.size = Pt(12)

        s = build_table(doc, rows, is_pcm)
        add_summary(doc, s, label=f"{district_name} — ")

        cumulative['candidates'] += s['candidates']
        cumulative['cost']       += s['cost']
        cumulative['markup']     += s['markup']
        cumulative['venue']      += s['venue']
        cumulative['total']      += s['total']
        cumulative['net']        += s['net']
        for i in range(n_items):
            cumulative['item_count'][i] += s['item_count'][i]
            cumulative['tot_cost'][i]   += s['tot_cost'][i]
            cumulative['tot_markup'][i] += s['tot_markup'][i]
            cumulative['tot_venue'][i]  += s['tot_venue'][i]
            cumulative['tot_total'][i]  += s['tot_total'][i]

        doc.add_paragraph()

    # ---------- GRAND TOTALS ----------
    doc.add_page_break()

    gh = doc.add_heading('CUMULATIVE TOTALS — ALL DISTRICTS / CHURCHES', level=1)
    gh.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in gh.runs:
        run.font.color.rgb = RGBColor(0x1F, 0x37, 0x64)

    add_summary(doc, cumulative, label='GRAND TOTAL — ')

    # ---- Big summary table for grand totals ----------------------------
    gt = doc.add_table(rows=2, cols=6)
    gt.style = 'Table Grid'
    gt.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = ['Candidates', 'Total Cost (K)', 'Total Markup (K)',
           'Total Venue (K)', 'Total Paid (K)', 'Net Profit (K)']
    vals = [cumulative['candidates'],
            cumulative['cost'],
            cumulative['markup'],
            cumulative['venue'],
            cumulative['total'],
            cumulative['net']]
    for i, h_ in enumerate(hdr):
        set_cell_text(gt.cell(0, i), h_, bold=True, size=10,
                      color=RGBColor(0x1F, 0x37, 0x64))
        shade(gt.cell(0, i), 'D9E2F3')
    for i, v in enumerate(vals):
        set_cell_text(gt.cell(1, i), str(v), bold=True, size=11)
        shade(gt.cell(1, i), 'FFF2CC')

    doc.add_paragraph()

    # ---- Grand per-item money table ------------------------------------
    ip = doc.add_paragraph()
    ipr = ip.add_run('Per-item totals across all tables')
    ipr.bold = True
    ipr.font.size = Pt(10)
    ipr.font.color.rgb = RGBColor(0x1F, 0x37, 0x64)

    it = doc.add_table(rows=1, cols=1 + n_items)
    it.style = 'Table Grid'
    it.alignment = WD_TABLE_ALIGNMENT.CENTER

    set_cell_text(it.cell(0, 0), 'Metric', bold=True, size=8)
    shade(it.cell(0, 0), 'D9E2F3')
    for i, lbl in enumerate(ITEM_LABELS):
        set_cell_text(it.cell(0, i + 1), lbl, bold=True, size=6.5)
        shade(it.cell(0, i + 1), 'D9E2F3')

    for label, key in [('Count', 'item_count'),
                       ('Cost (K)', 'tot_cost'),
                       ('Markup (K)', 'tot_markup'),
                       ('Venue (K)', 'tot_venue'),
                       ('Total (K)', 'tot_total')]:
        row = it.add_row()
        set_cell_text(row.cells[0], label, bold=True, size=8)
        shade(row.cells[0], 'FFF2CC')
        for i in range(n_items):
            set_cell_text(row.cells[i + 1], str(cumulative[key][i]), size=7)

    out = '2026_INVESTITURE_LIST_AND_ACCESSORIES.docx'
    doc.save(out)
    print(f'Saved: {out}')


if __name__ == '__main__':
    main()