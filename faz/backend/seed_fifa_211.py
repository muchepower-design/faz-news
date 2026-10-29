# ============================================================
# seed_fifa_211.py
#
# Seeds:
#   - 211 FIFA member associations
#   - 211 Senior Men's National Teams
#   - 211 Senior Women's National Teams
#
# Total:
#   422 national team records
#
# Requirements:
#   - countries table must already be populated
#   - Country model must contain:
#         id
#         name
#         short_name
#
#   - NationalTeam model must contain:
#         id
#         country_id
#         name
#         short_name
#         gender
#         age
#         nickname
#         fifa_code
#         flag_image_url
#
# ============================================================

import sys
import os

# Add backend directory to Python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


# ------------------------------------------------------------
# IMPORT FLASK APPLICATION
# ------------------------------------------------------------

from app import create_app, db

from app.models.country import Country
from app.models.national_team import NationalTeam


# ============================================================
# FIFA MEMBER ASSOCIATIONS
# ============================================================

FIFA_ASSOCIATIONS = [

    # ========================================================
    # AFRICA - CAF (54)
    # ========================================================

    {
        "name": "Algeria",
        "short_name": "ALG",
        "continent": "Africa",
        "male_nickname": "Les Fennecs",
        "female_nickname": "Les Fennecs"
    },
    {
        "name": "Angola",
        "short_name": "ANG",
        "continent": "Africa",
        "male_nickname": "Palancas Negras",
        "female_nickname": "Palancas Negras"
    },
    {
        "name": "Benin",
        "short_name": "BEN",
        "continent": "Africa",
        "male_nickname": "The Cheetahs",
        "female_nickname": "The Cheetahs"
    },
    {
        "name": "Botswana",
        "short_name": "BOT",
        "continent": "Africa",
        "male_nickname": "The Zebras",
        "female_nickname": "The Mares"
    },
    {
        "name": "Burkina Faso",
        "short_name": "BFA",
        "continent": "Africa",
        "male_nickname": "The Stallions",
        "female_nickname": "The Stallions"
    },
    {
        "name": "Burundi",
        "short_name": "BDI",
        "continent": "Africa",
        "male_nickname": "The Swallows",
        "female_nickname": "The Swallows"
    },
    {
        "name": "Cameroon",
        "short_name": "CMR",
        "continent": "Africa",
        "male_nickname": "Indomitable Lions",
        "female_nickname": "Indomitable Lionesses"
    },
    {
        "name": "Cape Verde",
        "short_name": "CPV",
        "continent": "Africa",
        "male_nickname": "Blue Sharks",
        "female_nickname": "Blue Sharks"
    },
    {
        "name": "Central African Republic",
        "short_name": "CTA",
        "continent": "Africa",
        "male_nickname": "The Fauves",
        "female_nickname": "The Fauves"
    },
    {
        "name": "Chad",
        "short_name": "CHA",
        "continent": "Africa",
        "male_nickname": "The Sao",
        "female_nickname": "The Sao"
    },
    {
        "name": "Comoros",
        "short_name": "COM",
        "continent": "Africa",
        "male_nickname": "The Coelacanths",
        "female_nickname": "The Coelacanths"
    },
    {
        "name": "Congo",
        "short_name": "CGO",
        "continent": "Africa",
        "male_nickname": "The Red Devils",
        "female_nickname": "The Red Devils"
    },
    {
        "name": "Democratic Republic of the Congo",
        "short_name": "COD",
        "continent": "Africa",
        "male_nickname": "The Leopards",
        "female_nickname": "The Leopards"
    },
    {
        "name": "Djibouti",
        "short_name": "DJI",
        "continent": "Africa",
        "male_nickname": "The Shoremen",
        "female_nickname": "The Shorewomen"
    },
    {
        "name": "Egypt",
        "short_name": "EGY",
        "continent": "Africa",
        "male_nickname": "The Pharaohs",
        "female_nickname": "The Pharaohs"
    },
    {
        "name": "Equatorial Guinea",
        "short_name": "EQG",
        "continent": "Africa",
        "male_nickname": "Nzalang Nacional",
        "female_nickname": "Nzalang Nacional"
    },
    {
        "name": "Eritrea",
        "short_name": "ERI",
        "continent": "Africa",
        "male_nickname": "The Red Sea Boys",
        "female_nickname": "The Red Sea Girls"
    },
    {
        "name": "Eswatini",
        "short_name": "SWZ",
        "continent": "Africa",
        "male_nickname": "Sihlangu Semnikati",
        "female_nickname": "Sitsebe Sa Maseko"
    },
    {
        "name": "Ethiopia",
        "short_name": "ETH",
        "continent": "Africa",
        "male_nickname": "Walias",
        "female_nickname": "Lucy"
    },
    {
        "name": "Gabon",
        "short_name": "GAB",
        "continent": "Africa",
        "male_nickname": "The Panthers",
        "female_nickname": "The Panthers"
    },
    {
        "name": "Gambia",
        "short_name": "GAM",
        "continent": "Africa",
        "male_nickname": "The Scorpions",
        "female_nickname": "The Scorpions"
    },
    {
        "name": "Ghana",
        "short_name": "GHA",
        "continent": "Africa",
        "male_nickname": "Black Stars",
        "female_nickname": "Black Queens"
    },
    {
        "name": "Guinea",
        "short_name": "GUI",
        "continent": "Africa",
        "male_nickname": "Syli National",
        "female_nickname": "Syli National"
    },
    {
        "name": "Guinea-Bissau",
        "short_name": "GNB",
        "continent": "Africa",
        "male_nickname": "Djurtus",
        "female_nickname": "Djurtus"
    },
    {
        "name": "Ivory Coast",
        "short_name": "CIV",
        "continent": "Africa",
        "male_nickname": "The Elephants",
        "female_nickname": "The Elephants"
    },
    {
        "name": "Kenya",
        "short_name": "KEN",
        "continent": "Africa",
        "male_nickname": "Harambee Stars",
        "female_nickname": "Harambee Starlets"
    },
    {
        "name": "Lesotho",
        "short_name": "LES",
        "continent": "Africa",
        "male_nickname": "Likuena",
        "female_nickname": "Mehalalitoe"
    },
    {
        "name": "Liberia",
        "short_name": "LBR",
        "continent": "Africa",
        "male_nickname": "Lone Stars",
        "female_nickname": "Lone Stars"
    },
    {
        "name": "Libya",
        "short_name": "LBY",
        "continent": "Africa",
        "male_nickname": "The Mediterranean Knights",
        "female_nickname": "The Mediterranean Knights"
    },
    {
        "name": "Madagascar",
        "short_name": "MAD",
        "continent": "Africa",
        "male_nickname": "Barea",
        "female_nickname": "Barea"
    },
    {
        "name": "Malawi",
        "short_name": "MWI",
        "continent": "Africa",
        "male_nickname": "The Flames",
        "female_nickname": "The Scorchers"
    },
    {
        "name": "Mali",
        "short_name": "MLI",
        "continent": "Africa",
        "male_nickname": "The Eagles",
        "female_nickname": "The Eagles"
    },
    {
        "name": "Mauritania",
        "short_name": "MTN",
        "continent": "Africa",
        "male_nickname": "Al-Murabitun",
        "female_nickname": "Al-Murabitun"
    },
    {
        "name": "Mauritius",
        "short_name": "MRI",
        "continent": "Africa",
        "male_nickname": "Club M",
        "female_nickname": "Club M"
    },
    {
        "name": "Morocco",
        "short_name": "MAR",
        "continent": "Africa",
        "male_nickname": "Atlas Lions",
        "female_nickname": "Atlas Lionesses"
    },
    {
        "name": "Mozambique",
        "short_name": "MOZ",
        "continent": "Africa",
        "male_nickname": "The Mambas",
        "female_nickname": "The Mambas"
    },
    {
        "name": "Namibia",
        "short_name": "NAM",
        "continent": "Africa",
        "male_nickname": "Brave Warriors",
        "female_nickname": "Brave Gladiators"
    },
    {
        "name": "Niger",
        "short_name": "NIG",
        "continent": "Africa",
        "male_nickname": "Menas",
        "female_nickname": "Menas"
    },
    {
        "name": "Nigeria",
        "short_name": "NGA",
        "continent": "Africa",
        "male_nickname": "Super Eagles",
        "female_nickname": "Super Falcons"
    },
    {
        "name": "Rwanda",
        "short_name": "RWA",
        "continent": "Africa",
        "male_nickname": "Amavubi",
        "female_nickname": "She-Amavubi"
    },
    {
        "name": "Sao Tome and Principe",
        "short_name": "STP",
        "continent": "Africa",
        "male_nickname": "The Falcons and Parrots",
        "female_nickname": "The Falcons and Parrots"
    },
    {
        "name": "Senegal",
        "short_name": "SEN",
        "continent": "Africa",
        "male_nickname": "Teranga Lions",
        "female_nickname": "Teranga Lionesses"
    },
    {
        "name": "Seychelles",
        "short_name": "SEY",
        "continent": "Africa",
        "male_nickname": "The Pirates",
        "female_nickname": "The Pirates"
    },
    {
        "name": "Sierra Leone",
        "short_name": "SLE",
        "continent": "Africa",
        "male_nickname": "Leone Stars",
        "female_nickname": "Sierra Queens"
    },
    {
        "name": "Somalia",
        "short_name": "SOM",
        "continent": "Africa",
        "male_nickname": "The Ocean Stars",
        "female_nickname": "The Ocean Stars"
    },
    {
        "name": "South Africa",
        "short_name": "RSA",
        "continent": "Africa",
        "male_nickname": "Bafana Bafana",
        "female_nickname": "Banyana Banyana"
    },
    {
        "name": "South Sudan",
        "short_name": "SSD",
        "continent": "Africa",
        "male_nickname": "Bright Stars",
        "female_nickname": "Bright Stars"
    },
    {
        "name": "Sudan",
        "short_name": "SDN",
        "continent": "Africa",
        "male_nickname": "Falcons of Jediane",
        "female_nickname": "Falcons of Jediane"
    },
    {
        "name": "Tanzania",
        "short_name": "TAN",
        "continent": "Africa",
        "male_nickname": "Taifa Stars",
        "female_nickname": "Twiga Stars"
    },
    {
        "name": "Togo",
        "short_name": "TOG",
        "continent": "Africa",
        "male_nickname": "The Sparrow Hawks",
        "female_nickname": "The Sparrow Hawks"
    },
    {
        "name": "Tunisia",
        "short_name": "TUN",
        "continent": "Africa",
        "male_nickname": "Carthage Eagles",
        "female_nickname": "Carthage Eagles"
    },
    {
        "name": "Uganda",
        "short_name": "UGA",
        "continent": "Africa",
        "male_nickname": "The Cranes",
        "female_nickname": "The Crested Cranes"
    },
    {
        "name": "Zambia",
        "short_name": "ZAM",
        "continent": "Africa",
        "male_nickname": "Chipolopolo",
        "female_nickname": "Copper Queens"
    },
    {
        "name": "Zimbabwe",
        "short_name": "ZIM",
        "continent": "Africa",
        "male_nickname": "The Warriors",
        "female_nickname": "Mighty Warriors"
    },

    # ========================================================
    # ASIA - AFC (46)
    # ========================================================

    {
        "name": "Afghanistan",
        "short_name": "AFG",
        "continent": "Asia",
        "male_nickname": "The Lions of Khorasan",
        "female_nickname": "The Lions of Khorasan"
    },
    {
        "name": "Australia",
        "short_name": "AUS",
        "continent": "Asia",
        "male_nickname": "Socceroos",
        "female_nickname": "Matildas"
    },
    {
        "name": "Bahrain",
        "short_name": "BHR",
        "continent": "Asia",
        "male_nickname": "The Reds",
        "female_nickname": "The Reds"
    },
    {
        "name": "Bangladesh",
        "short_name": "BAN",
        "continent": "Asia",
        "male_nickname": "The Bengal Tigers",
        "female_nickname": "The Bengal Tigresses"
    },
    {
        "name": "Bhutan",
        "short_name": "BHU",
        "continent": "Asia",
        "male_nickname": "The Dragons",
        "female_nickname": "The Dragon Girls"
    },
    {
        "name": "Brunei",
        "short_name": "BRU",
        "continent": "Asia",
        "male_nickname": "Tabuan",
        "female_nickname": "Tabuan"
    },
    {
        "name": "Cambodia",
        "short_name": "CAM",
        "continent": "Asia",
        "male_nickname": "Angkor Warriors",
        "female_nickname": "Angkor Warriors"
    },
    {
        "name": "China",
        "short_name": "CHN",
        "continent": "Asia",
        "male_nickname": "Team Dragon",
        "female_nickname": "Steel Roses"
    },
    {
        "name": "Chinese Taipei",
        "short_name": "TPE",
        "continent": "Asia",
        "male_nickname": "The Blue Magpies",
        "female_nickname": "Mulan"
    },
    {
        "name": "Guam",
        "short_name": "GUM",
        "continent": "Asia",
        "male_nickname": "Matao",
        "female_nickname": "Masakåda"
    },
    {
        "name": "Hong Kong",
        "short_name": "HKG",
        "continent": "Asia",
        "male_nickname": "The Dragons",
        "female_nickname": "The Dragons"
    },
    {
        "name": "India",
        "short_name": "IND",
        "continent": "Asia",
        "male_nickname": "The Blue Tigers",
        "female_nickname": "The Blue Tigresses"
    },
    {
        "name": "Indonesia",
        "short_name": "IDN",
        "continent": "Asia",
        "male_nickname": "Garuda",
        "female_nickname": "Garuda Pertiwi"
    },
    {
        "name": "Iran",
        "short_name": "IRN",
        "continent": "Asia",
        "male_nickname": "Team Melli",
        "female_nickname": "Team Melli"
    },
    {
        "name": "Iraq",
        "short_name": "IRQ",
        "continent": "Asia",
        "male_nickname": "Lions of Mesopotamia",
        "female_nickname": "Lions of Mesopotamia"
    },
    {
        "name": "Japan",
        "short_name": "JPN",
        "continent": "Asia",
        "male_nickname": "Samurai Blue",
        "female_nickname": "Nadeshiko Japan"
    },
    {
        "name": "Jordan",
        "short_name": "JOR",
        "continent": "Asia",
        "male_nickname": "Al-Nashama",
        "female_nickname": "Al-Nashama"
    },
    {
        "name": "Korea DPR",
        "short_name": "PRK",
        "continent": "Asia",
        "male_nickname": "Chollima",
        "female_nickname": "Chollima"
    },
    {
        "name": "Korea Republic",
        "short_name": "KOR",
        "continent": "Asia",
        "male_nickname": "Taegeuk Warriors",
        "female_nickname": "Taegeuk Ladies"
    },
    {
        "name": "Kuwait",
        "short_name": "KUW",
        "continent": "Asia",
        "male_nickname": "The Blue Wave",
        "female_nickname": "The Blue Wave"
    },
    {
        "name": "Kyrgyzstan",
        "short_name": "KGZ",
        "continent": "Asia",
        "male_nickname": "White Falcons",
        "female_nickname": "White Falcons"
    },
    {
        "name": "Laos",
        "short_name": "LAO",
        "continent": "Asia",
        "male_nickname": "Thimsad",
        "female_nickname": "Thimsad"
    },
    {
        "name": "Lebanon",
        "short_name": "LBN",
        "continent": "Asia",
        "male_nickname": "The Cedars",
        "female_nickname": "The Cedars"
    },
    {
        "name": "Macau",
        "short_name": "MAC",
        "continent": "Asia",
        "male_nickname": "The Green and Whites",
        "female_nickname": "The Green and Whites"
    },
    {
        "name": "Malaysia",
        "short_name": "MAS",
        "continent": "Asia",
        "male_nickname": "Harimau Malaya",
        "female_nickname": "Malayan Tigresses"
    },
    {
        "name": "Maldives",
        "short_name": "MDV",
        "continent": "Asia",
        "male_nickname": "The Red Snappers",
        "female_nickname": "The Red Snappers"
    },
    {
        "name": "Mongolia",
        "short_name": "MNG",
        "continent": "Asia",
        "male_nickname": "The Blue Wolves",
        "female_nickname": "The Blue Wolves"
    },
    {
        "name": "Myanmar",
        "short_name": "MYA",
        "continent": "Asia",
        "male_nickname": "The Asian Lions",
        "female_nickname": "The Asian Lions"
    },
    {
        "name": "Nepal",
        "short_name": "NEP",
        "continent": "Asia",
        "male_nickname": "The Gorkhalis",
        "female_nickname": "The Gorkhalis"
    },
    {
        "name": "Oman",
        "short_name": "OMA",
        "continent": "Asia",
        "male_nickname": "The Reds",
        "female_nickname": "The Reds"
    },
    {
        "name": "Pakistan",
        "short_name": "PAK",
        "continent": "Asia",
        "male_nickname": "The Shaheens",
        "female_nickname": "The Shaheens"
    },
    {
        "name": "Palestine",
        "short_name": "PLE",
        "continent": "Asia",
        "male_nickname": "The Fedayeen",
        "female_nickname": "The Fedayeen"
    },
    {
        "name": "Philippines",
        "short_name": "PHI",
        "continent": "Asia",
        "male_nickname": "Azkals",
        "female_nickname": "Filipinas"
    },
    {
        "name": "Qatar",
        "short_name": "QAT",
        "continent": "Asia",
        "male_nickname": "The Maroons",
        "female_nickname": "The Maroons"
    },
    {
        "name": "Saudi Arabia",
        "short_name": "KSA",
        "continent": "Asia",
        "male_nickname": "The Green Falcons",
        "female_nickname": "The Green Falcons"
    },
    {
        "name": "Singapore",
        "short_name": "SIN",
        "continent": "Asia",
        "male_nickname": "The Lions",
        "female_nickname": "The Lionesses"
    },
    {
        "name": "Sri Lanka",
        "short_name": "SRI",
        "continent": "Asia",
        "male_nickname": "The Golden Army",
        "female_nickname": "The Golden Army"
    },
    {
        "name": "Syria",
        "short_name": "SYR",
        "continent": "Asia",
        "male_nickname": "The Qasioun Eagles",
        "female_nickname": "The Qasioun Eagles"
    },
    {
        "name": "Tajikistan",
        "short_name": "TJK",
        "continent": "Asia",
        "male_nickname": "The Crown",
        "female_nickname": "The Crown"
    },
    {
        "name": "Thailand",
        "short_name": "THA",
        "continent": "Asia",
        "male_nickname": "War Elephants",
        "female_nickname": "Chaba Kaew"
    },
    {
        "name": "Timor-Leste",
        "short_name": "TLS",
        "continent": "Asia",
        "male_nickname": "The O Sol Nascente",
        "female_nickname": "The O Sol Nascente"
    },
    {
        "name": "Turkmenistan",
        "short_name": "TKM",
        "continent": "Asia",
        "male_nickname": "The Green Men",
        "female_nickname": "The Green Men"
    },
    {
        "name": "United Arab Emirates",
        "short_name": "UAE",
        "continent": "Asia",
        "male_nickname": "The Whites",
        "female_nickname": "The Whites"
    },
    {
        "name": "Uzbekistan",
        "short_name": "UZB",
        "continent": "Asia",
        "male_nickname": "The White Wolves",
        "female_nickname": "The White Wolves"
    },
    {
        "name": "Vietnam",
        "short_name": "VIE",
        "continent": "Asia",
        "male_nickname": "Golden Star Warriors",
        "female_nickname": "The Golden Girls"
    },
    {
        "name": "Yemen",
        "short_name": "YEM",
        "continent": "Asia",
        "male_nickname": "The Red Devils",
        "female_nickname": "The Red Devils"
    },

    # ========================================================
    # EUROPE - UEFA (55)
    # ========================================================

    {
        "name": "Albania",
        "short_name": "ALB",
        "continent": "Europe",
        "male_nickname": "Kuq e Zinjtë",
        "female_nickname": "Kuq e Zinjtë"
    },
    {
        "name": "Andorra",
        "short_name": "AND",
        "continent": "Europe",
        "male_nickname": "The Tricolours",
        "female_nickname": "The Tricolours"
    },
    {
        "name": "Armenia",
        "short_name": "ARM",
        "continent": "Europe",
        "male_nickname": "The Collectives",
        "female_nickname": "The Collectives"
    },
    {
        "name": "Austria",
        "short_name": "AUT",
        "continent": "Europe",
        "male_nickname": "Das Team",
        "female_nickname": "The Team"
    },
    {
        "name": "Azerbaijan",
        "short_name": "AZE",
        "continent": "Europe",
        "male_nickname": "The Milli",
        "female_nickname": "The Milli"
    },
    {
        "name": "Belarus",
        "short_name": "BLR",
        "continent": "Europe",
        "male_nickname": "The White Wings",
        "female_nickname": "The White Wings"
    },
    {
        "name": "Belgium",
        "short_name": "BEL",
        "continent": "Europe",
        "male_nickname": "Red Devils",
        "female_nickname": "Red Flames"
    },
    {
        "name": "Bosnia and Herzegovina",
        "short_name": "BIH",
        "continent": "Europe",
        "male_nickname": "Dragons",
        "female_nickname": "Dragon Ladies"
    },
    {
        "name": "Bulgaria",
        "short_name": "BUL",
        "continent": "Europe",
        "male_nickname": "The Lions",
        "female_nickname": "The Lions"
    },
    {
        "name": "Croatia",
        "short_name": "CRO",
        "continent": "Europe",
        "male_nickname": "Vatreni",
        "female_nickname": "Vatrene"
    },
    {
        "name": "Cyprus",
        "short_name": "CYP",
        "continent": "Europe",
        "male_nickname": "The Blues",
        "female_nickname": "The Blues"
    },
    {
        "name": "Czech Republic",
        "short_name": "CZE",
        "continent": "Europe",
        "male_nickname": "The Locomotive",
        "female_nickname": "The Locomotive"
    },
    {
        "name": "Denmark",
        "short_name": "DEN",
        "continent": "Europe",
        "male_nickname": "Danish Dynamite",
        "female_nickname": "Danish Dynamite"
    },
    {
        "name": "England",
        "short_name": "ENG",
        "continent": "Europe",
        "male_nickname": "The Three Lions",
        "female_nickname": "The Lionesses"
    },
    {
        "name": "Estonia",
        "short_name": "EST",
        "continent": "Europe",
        "male_nickname": "The Blueshirts",
        "female_nickname": "The Blueshirts"
    },
    {
        "name": "Faroe Islands",
        "short_name": "FRO",
        "continent": "Europe",
        "male_nickname": "Landsliðið",
        "female_nickname": "Landsliðið"
    },
    {
        "name": "Finland",
        "short_name": "FIN",
        "continent": "Europe",
        "male_nickname": "Huuhkajat",
        "female_nickname": "Helmarit"
    },
    {
        "name": "France",
        "short_name": "FRA",
        "continent": "Europe",
        "male_nickname": "Les Bleus",
        "female_nickname": "Les Bleues"
    },
    {
        "name": "Georgia",
        "short_name": "GEO",
        "continent": "Europe",
        "male_nickname": "Jvarosnebi",
        "female_nickname": "Jvarosnebi"
    },
    {
        "name": "Germany",
        "short_name": "GER",
        "continent": "Europe",
        "male_nickname": "Die Mannschaft",
        "female_nickname": "Die Nationalelf"
    },
    {
        "name": "Gibraltar",
        "short_name": "GIB",
        "continent": "Europe",
        "male_nickname": "The Rock",
        "female_nickname": "The Rock"
    },
    {
        "name": "Greece",
        "short_name": "GRE",
        "continent": "Europe",
        "male_nickname": "The Pirate Ship",
        "female_nickname": "The Pirate Ship"
    },
    {
        "name": "Hungary",
        "short_name": "HUN",
        "continent": "Europe",
        "male_nickname": "The Magyars",
        "female_nickname": "The Magyars"
    },
    {
        "name": "Iceland",
        "short_name": "ISL",
        "continent": "Europe",
        "male_nickname": "Strákarnir okkar",
        "female_nickname": "Stelpurnar okkar"
    },
    {
        "name": "Israel",
        "short_name": "ISR",
        "continent": "Europe",
        "male_nickname": "The Blue and Whites",
        "female_nickname": "The Blue and Whites"
    },
    {
        "name": "Italy",
        "short_name": "ITA",
        "continent": "Europe",
        "male_nickname": "Azzurri",
        "female_nickname": "Azzurre"
    },
    {
        "name": "Kazakhstan",
        "short_name": "KAZ",
        "continent": "Europe",
        "male_nickname": "The Hawks",
        "female_nickname": "The Hawks"
    },
    {
        "name": "Kosovo",
        "short_name": "KVX",
        "continent": "Europe",
        "male_nickname": "Dardanët",
        "female_nickname": "Dardanët"
    },
    {
        "name": "Latvia",
        "short_name": "LVA",
        "continent": "Europe",
        "male_nickname": "The Red-Whites",
        "female_nickname": "The Red-Whites"
    },
    {
        "name": "Liechtenstein",
        "short_name": "LIE",
        "continent": "Europe",
        "male_nickname": "The Blues-Reds",
        "female_nickname": "The Blues-Reds"
    },
    {
        "name": "Lithuania",
        "short_name": "LTU",
        "continent": "Europe",
        "male_nickname": "The Yellow-Greens",
        "female_nickname": "The Yellow-Greens"
    },
    {
        "name": "Luxembourg",
        "short_name": "LUX",
        "continent": "Europe",
        "male_nickname": "The Red Lions",
        "female_nickname": "The Red Lions"
    },
    {
        "name": "Malta",
        "short_name": "MLT",
        "continent": "Europe",
        "male_nickname": "The Knights",
        "female_nickname": "The Knights"
    },
    {
        "name": "Moldova",
        "short_name": "MDA",
        "continent": "Europe",
        "male_nickname": "The Tricolours",
        "female_nickname": "The Tricolours"
    },
    {
        "name": "Montenegro",
        "short_name": "MNE",
        "continent": "Europe",
        "male_nickname": "The Brave Falcons",
        "female_nickname": "The Brave Falcons"
    },
    {
        "name": "Netherlands",
        "short_name": "NED",
        "continent": "Europe",
        "male_nickname": "Oranje",
        "female_nickname": "Oranje Leeuwinnen"
    },
    {
        "name": "North Macedonia",
        "short_name": "MKD",
        "continent": "Europe",
        "male_nickname": "The Red Lynxes",
        "female_nickname": "The Red Lynxes"
    },
    {
        "name": "Northern Ireland",
        "short_name": "NIR",
        "continent": "Europe",
        "male_nickname": "The Green and White Army",
        "female_nickname": "The Green and White Army"
    },
    {
        "name": "Norway",
        "short_name": "NOR",
        "continent": "Europe",
        "male_nickname": "Løvene",
        "female_nickname": "Gresshoppene"
    },
    {
        "name": "Poland",
        "short_name": "POL",
        "continent": "Europe",
        "male_nickname": "Biało-czerwoni",
        "female_nickname": "Biało-czerwone"
    },
    {
        "name": "Portugal",
        "short_name": "POR",
        "continent": "Europe",
        "male_nickname": "Seleção",
        "female_nickname": "A Seleção"
    },
    {
        "name": "Republic of Ireland",
        "short_name": "IRL",
        "continent": "Europe",
        "male_nickname": "The Boys in Green",
        "female_nickname": "The Girls in Green"
    },
    {
        "name": "Romania",
        "short_name": "ROU",
        "continent": "Europe",
        "male_nickname": "Tricolorii",
        "female_nickname": "Tricolorele"
    },
    {
        "name": "Russia",
        "short_name": "RUS",
        "continent": "Europe",
        "male_nickname": "Sbornaya",
        "female_nickname": "Sbornaya"
    },
    {
        "name": "San Marino",
        "short_name": "SMR",
        "continent": "Europe",
        "male_nickname": "La Serenissima",
        "female_nickname": "La Serenissima"
    },
    {
        "name": "Scotland",
        "short_name": "SCO",
        "continent": "Europe",
        "male_nickname": "The Tartan Army",
        "female_nickname": "The Tartan Army"
    },
    {
        "name": "Serbia",
        "short_name": "SRB",
        "continent": "Europe",
        "male_nickname": "The Eagles",
        "female_nickname": "The Eagles"
    },
    {
        "name": "Slovakia",
        "short_name": "SVK",
        "continent": "Europe",
        "male_nickname": "Repre",
        "female_nickname": "Repre"
    },
    {
        "name": "Slovenia",
        "short_name": "SVN",
        "continent": "Europe",
        "male_nickname": "The Boys",
        "female_nickname": "The Girls"
    },
    {
        "name": "Spain",
        "short_name": "ESP",
        "continent": "Europe",
        "male_nickname": "La Roja",
        "female_nickname": "La Roja"
    },
    {
        "name": "Sweden",
        "short_name": "SWE",
        "continent": "Europe",
        "male_nickname": "Blågult",
        "female_nickname": "Blågult"
    },
    {
        "name": "Switzerland",
        "short_name": "SUI",
        "continent": "Europe",
        "male_nickname": "Rossocrociati",
        "female_nickname": "Nati"
    },
    {
        "name": "Türkiye",
        "short_name": "TUR",
        "continent": "Europe",
        "male_nickname": "Ay-Yıldızlılar",
        "female_nickname": "Ay-Yıldızlılar"
    },
    {
        "name": "Ukraine",
        "short_name": "UKR",
        "continent": "Europe",
        "male_nickname": "The Blue and Yellows",
        "female_nickname": "The Blue and Yellows"
    },
    {
        "name": "Wales",
        "short_name": "WAL",
        "continent": "Europe",
        "male_nickname": "The Dragons",
        "female_nickname": "The Red Wall"
    },

    # ========================================================
    # NORTH AMERICA / CENTRAL AMERICA / CARIBBEAN - CONCACAF
    # 41
    # ========================================================

    {
        "name": "Anguilla",
        "short_name": "AIA",
        "continent": "North America",
        "male_nickname": "The Dolphins",
        "female_nickname": "The Dolphins"
    },
    {
        "name": "Antigua and Barbuda",
        "short_name": "ATG",
        "continent": "North America",
        "male_nickname": "Benna Boys",
        "female_nickname": "Benna Girls"
    },
    {
        "name": "Aruba",
        "short_name": "ARU",
        "continent": "North America",
        "male_nickname": "The Aruban National Team",
        "female_nickname": "The Aruban National Team"
    },
    {
        "name": "Bahamas",
        "short_name": "BAH",
        "continent": "North America",
        "male_nickname": "The Baha Boyz",
        "female_nickname": "The Baha Girlz"
    },
    {
        "name": "Barbados",
        "short_name": "BRB",
        "continent": "North America",
        "male_nickname": "The Tridents",
        "female_nickname": "The Tridents"
    },
    {
        "name": "Belize",
        "short_name": "BLZ",
        "continent": "North America",
        "male_nickname": "The Jaguars",
        "female_nickname": "The Jaguars"
    },
    {
        "name": "Bermuda",
        "short_name": "BER",
        "continent": "North America",
        "male_nickname": "The Gombey Warriors",
        "female_nickname": "The Gombey Warriors"
    },
    {
        "name": "British Virgin Islands",
        "short_name": "VGB",
        "continent": "North America",
        "male_nickname": "The Nature Boyz",
        "female_nickname": "The Nature Girlz"
    },
    {
        "name": "Canada",
        "short_name": "CAN",
        "continent": "North America",
        "male_nickname": "The Canucks",
        "female_nickname": "Les Rouges"
    },
    {
        "name": "Cayman Islands",
        "short_name": "CAY",
        "continent": "North America",
        "male_nickname": "The Stingrays",
        "female_nickname": "The Stingrays"
    },
    {
        "name": "Costa Rica",
        "short_name": "CRC",
        "continent": "North America",
        "male_nickname": "Los Ticos",
        "female_nickname": "Las Ticas"
    },
    {
        "name": "Cuba",
        "short_name": "CUB",
        "continent": "North America",
        "male_nickname": "Leones del Caribe",
        "female_nickname": "Leonas del Caribe"
    },
    {
        "name": "Curaçao",
        "short_name": "CUW",
        "continent": "North America",
        "male_nickname": "Blue Curacao",
        "female_nickname": "Blue Curacao"
    },
    {
        "name": "Dominica",
        "short_name": "DMA",
        "continent": "North America",
        "male_nickname": "The Nature Isle",
        "female_nickname": "The Nature Isle"
    },
    {
        "name": "Dominican Republic",
        "short_name": "DOM",
        "continent": "North America",
        "male_nickname": "Los Quisqueyanos",
        "female_nickname": "Las Quisqueyanas"
    },
    {
        "name": "El Salvador",
        "short_name": "SLV",
        "continent": "North America",
        "male_nickname": "La Selecta",
        "female_nickname": "La Selecta"
    },
    {
        "name": "Grenada",
        "short_name": "GRN",
        "continent": "North America",
        "male_nickname": "Spice Boyz",
        "female_nickname": "Spice Girlz"
    },
    {
        "name": "Guadeloupe",
        "short_name": "GLP",
        "continent": "North America",
        "male_nickname": "The Gwada Boys",
        "female_nickname": "The Gwada Girls"
    },
    {
        "name": "Guatemala",
        "short_name": "GUA",
        "continent": "North America",
        "male_nickname": "Los Chapines",
        "female_nickname": "Las Chapinas"
    },
    {
        "name": "Guyana",
        "short_name": "GUY",
        "continent": "North America",
        "male_nickname": "Golden Jaguars",
        "female_nickname": "Lady Jags"
    },
    {
        "name": "Haiti",
        "short_name": "HAI",
        "continent": "North America",
        "male_nickname": "Les Grenadiers",
        "female_nickname": "Les Grenadières"
    },
    {
        "name": "Honduras",
        "short_name": "HON",
        "continent": "North America",
        "male_nickname": "Los Catrachos",
        "female_nickname": "Las Catrachas"
    },
    {
        "name": "Jamaica",
        "short_name": "JAM",
        "continent": "North America",
        "male_nickname": "Reggae Boyz",
        "female_nickname": "Reggae Girlz"
    },
    {
        "name": "Martinique",
        "short_name": "MTQ",
        "continent": "North America",
        "male_nickname": "Les Matinino",
        "female_nickname": "Les Matinino"
    },
    {
        "name": "Mexico",
        "short_name": "MEX",
        "continent": "North America",
        "male_nickname": "El Tri",
        "female_nickname": "El Tri Femenil"
    },
    {
        "name": "Montserrat",
        "short_name": "MSR",
        "continent": "North America",
        "male_nickname": "The Emerald Boys",
        "female_nickname": "The Emerald Girls"
    },
    {
        "name": "Nicaragua",
        "short_name": "NCA",
        "continent": "North America",
        "male_nickname": "La Azul y Blanco",
        "female_nickname": "La Azul y Blanco"
    },
    {
        "name": "Panama",
        "short_name": "PAN",
        "continent": "North America",
        "male_nickname": "Los Canaleros",
        "female_nickname": "Las Canaleras"
    },
    {
        "name": "Puerto Rico",
        "short_name": "PUR",
        "continent": "North America",
        "male_nickname": "El Huracán Azul",
        "female_nickname": "Las Boricuas"
    },
    {
        "name": "Saint Kitts and Nevis",
        "short_name": "SKN",
        "continent": "North America",
        "male_nickname": "The Sugar Boyz",
        "female_nickname": "Sugar Girlz"
    },
    {
        "name": "Saint Lucia",
        "short_name": "LCA",
        "continent": "North America",
        "male_nickname": "The Pitons",
        "female_nickname": "The Pitons"
    },
    {
        "name": "Saint Vincent and the Grenadines",
        "short_name": "VIN",
        "continent": "North America",
        "male_nickname": "Vincy Heat",
        "female_nickname": "Vincy Heat"
    },
    {
        "name": "Sint Maarten",
        "short_name": "SXM",
        "continent": "North America",
        "male_nickname": "The Soualiga Boys",
        "female_nickname": "The Soualiga Girls"
    },
    {
        "name": "Suriname",
        "short_name": "SUR",
        "continent": "North America",
        "male_nickname": "Natio",
        "female_nickname": "Natio"
    },
    {
        "name": "Trinidad and Tobago",
        "short_name": "TRI",
        "continent": "North America",
        "male_nickname": "Soca Warriors",
        "female_nickname": "Women Soca Warriors"
    },
    {
        "name": "Turks and Caicos Islands",
        "short_name": "TCA",
        "continent": "North America",
        "male_nickname": "The Conch Crawler",
        "female_nickname": "The Conch Crawler"
    },
    {
        "name": "United States",
        "short_name": "USA",
        "continent": "North America",
        "male_nickname": "USMNT",
        "female_nickname": "USWNT"
    },
    {
        "name": "U.S. Virgin Islands",
        "short_name": "VIR",
        "continent": "North America",
        "male_nickname": "The Dashing Eagles",
        "female_nickname": "The Dashing Eagles"
    },

    # ========================================================
    # SOUTH AMERICA - CONMEBOL (10)
    # ========================================================

    {
        "name": "Argentina",
        "short_name": "ARG",
        "continent": "South America",
        "male_nickname": "La Albiceleste",
        "female_nickname": "Las Guerreras"
    },
    {
        "name": "Bolivia",
        "short_name": "BOL",
        "continent": "South America",
        "male_nickname": "La Verde",
        "female_nickname": "La Verde"
    },
    {
        "name": "Brazil",
        "short_name": "BRA",
        "continent": "South America",
        "male_nickname": "Canarinho",
        "female_nickname": "As Canarinhas"
    },
    {
        "name": "Chile",
        "short_name": "CHI",
        "continent": "South America",
        "male_nickname": "La Roja",
        "female_nickname": "La Roja"
    },
    {
        "name": "Colombia",
        "short_name": "COL",
        "continent": "South America",
        "male_nickname": "Los Cafeteros",
        "female_nickname": "Las Cafeteras"
    },
    {
        "name": "Ecuador",
        "short_name": "ECU",
        "continent": "South America",
        "male_nickname": "La Tri",
        "female_nickname": "La Tri"
    },
    {
        "name": "Paraguay",
        "short_name": "PAR",
        "continent": "South America",
        "male_nickname": "La Albirroja",
        "female_nickname": "La Albirroja"
    },
    {
        "name": "Peru",
        "short_name": "PER",
        "continent": "South America",
        "male_nickname": "La Bicolor",
        "female_nickname": "La Blanquirroja"
    },
    {
        "name": "Uruguay",
        "short_name": "URU",
        "continent": "South America",
        "male_nickname": "La Celeste",
        "female_nickname": "Las Celestes"
    },
    {
        "name": "Venezuela",
        "short_name": "VEN",
        "continent": "South America",
        "male_nickname": "La Vinotinto",
        "female_nickname": "La Vinotinto"
    },

    # ========================================================
    # OCEANIA - OFC (11)
    # ========================================================

    {
        "name": "American Samoa",
        "short_name": "ASA",
        "continent": "Oceania",
        "male_nickname": "The Boys from the Territory",
        "female_nickname": "The Girls from the Territory"
    },
    {
        "name": "Cook Islands",
        "short_name": "COK",
        "continent": "Oceania",
        "male_nickname": "The Toke",
        "female_nickname": "The Toke"
    },
    {
        "name": "Fiji",
        "short_name": "FIJ",
        "continent": "Oceania",
        "male_nickname": "Bula Boys",
        "female_nickname": "Bula Girls"
    },
    {
        "name": "New Caledonia",
        "short_name": "NCL",
        "continent": "Oceania",
        "male_nickname": "Les Cagous",
        "female_nickname": "Les Cagous"
    },
    {
        "name": "New Zealand",
        "short_name": "NZL",
        "continent": "Oceania",
        "male_nickname": "All Whites",
        "female_nickname": "Football Ferns"
    },
    {
        "name": "Papua New Guinea",
        "short_name": "PNG",
        "continent": "Oceania",
        "male_nickname": "The Kapuls",
        "female_nickname": "The Pepes"
    },
    {
        "name": "Samoa",
        "short_name": "SAM",
        "continent": "Oceania",
        "male_nickname": "Manumea",
        "female_nickname": "Manumea"
    },
    {
        "name": "Solomon Islands",
        "short_name": "SOL",
        "continent": "Oceania",
        "male_nickname": "Bonitos",
        "female_nickname": "Bonitas"
    },
    {
        "name": "Tahiti",
        "short_name": "TAH",
        "continent": "Oceania",
        "male_nickname": "Toa Aito",
        "female_nickname": "Toa Aito"
    },
    {
        "name": "Tonga",
        "short_name": "TGA",
        "continent": "Oceania",
        "male_nickname": "Ikale Tahi",
        "female_nickname": "Ikale Tahi"
    },
    {
        "name": "Vanuatu",
        "short_name": "VAN",
        "continent": "Oceania",
        "male_nickname": "The Men in Black",
        "female_nickname": "The Women in Black"
    },
]


# ============================================================
# COUNTRY NAME ALIASES
# ============================================================
#
# This helps when your countries seeder uses a slightly
# different country name from the FIFA association name.
#
# The seeder first searches short_name, then name, then aliases.
# ============================================================

COUNTRY_ALIASES = {
    "Czech Republic": [
        "Czechia"
    ],

    "Türkiye": [
        "Turkey"
    ],

    "Korea Republic": [
        "South Korea",
        "Republic of Korea"
    ],

    "Korea DPR": [
        "North Korea",
        "DPR Korea",
        "Democratic People's Republic of Korea"
    ],

    "Congo": [
        "Republic of the Congo",
        "Congo-Brazzaville"
    ],

    "Democratic Republic of the Congo": [
        "DR Congo",
        "DRC",
        "Congo-Kinshasa"
    ],

    "Ivory Coast": [
        "Côte d'Ivoire",
        "Cote d'Ivoire"
    ],

    "Eswatini": [
        "Swaziland"
    ],

    "Cape Verde": [
        "Cabo Verde"
    ],

    "Türkiye": [
        "Turkey"
    ],

    "United States": [
        "United States of America",
        "USA"
    ],

    "Iran": [
        "IR Iran",
        "Islamic Republic of Iran"
    ],

    "Laos": [
        "Lao People's Democratic Republic"
    ],

    "Vietnam": [
        "Viet Nam"
    ],

    "Tanzania": [
        "United Republic of Tanzania"
    ],

    "Bolivia": [
        "Bolivia (Plurinational State of)"
    ],

    "Venezuela": [
        "Venezuela (Bolivarian Republic of)"
    ],

    "Moldova": [
        "Republic of Moldova"
    ],

    "Brunei": [
        "Brunei Darussalam"
    ],

    "Palestine": [
        "Palestine, State of"
    ],

    "Russia": [
        "Russian Federation"
    ],

    "Sao Tome and Principe": [
        "São Tomé and Príncipe"
    ],

    "Micronesia": [
        "Federated States of Micronesia"
    ],
}


# ============================================================
# HELPER: FIND COUNTRY
# ============================================================

def find_country(data):
    """
    Find an existing Country record.

    Priority:
        1. FIFA short_name
        2. Exact country name
        3. Alias names
    """

    fifa_code = data["short_name"]
    name = data["name"]

    # --------------------------------------------------------
    # Search by short name
    # --------------------------------------------------------

    country = Country.query.filter(
        Country.short_name.ilike(fifa_code)
    ).first()

    if country:
        return country

    # --------------------------------------------------------
    # Search exact name
    # --------------------------------------------------------

    country = Country.query.filter(
        Country.name.ilike(name)
    ).first()

    if country:
        return country

    # --------------------------------------------------------
    # Search aliases
    # --------------------------------------------------------

    aliases = COUNTRY_ALIASES.get(name, [])

    for alias in aliases:
        country = Country.query.filter(
            Country.name.ilike(alias)
        ).first()

        if country:
            return country

    return None


# ============================================================
# CREATE / UPDATE NATIONAL TEAM
# ============================================================

def create_or_update_team(
    country,
    association,
    gender,
    nickname
):
    """
    Create a national team if it doesn't exist.

    If the team already exists, update its information.
    """

    fifa_code = association["short_name"]

    if gender == "Male":
        team_name = f"{country.name} Men's National Team"
        short_name = f"{country.name} Men"
        age_group = "Senior Men"

    else:
        team_name = f"{country.name} Women's National Team"
        short_name = f"{country.name} Women"
        age_group = "Senior Women"

    # --------------------------------------------------------
    # Find existing team
    # --------------------------------------------------------

    team = NationalTeam.query.filter_by(
        country_id=country.id,
        gender=gender,
        age="Senior"
    ).first()

    # --------------------------------------------------------
    # Create new team
    # --------------------------------------------------------

    if not team:
        team = NationalTeam(
            country_id=country.id,
            name=team_name,
            short_name=short_name,
            gender=gender,
            age="Senior",
            nickname=nickname,
            fifa_code=fifa_code,
            age_group=age_group
        )

        db.session.add(team)

        return "created"

    # --------------------------------------------------------
    # Update existing team
    # --------------------------------------------------------

    team.name = team_name
    team.short_name = short_name
    team.gender = gender
    team.age = "Senior"
    team.nickname = nickname
    team.fifa_code = fifa_code
    team.age_group = age_group

    return "updated"


# ============================================================
# MAIN SEEDER
# ============================================================

def seed_national_teams():

    print()
    print("=" * 70)
    print(" FIFA NATIONAL TEAMS SEEDER")
    print("=" * 70)
    print()

    print(
        f"FIFA associations in dataset: "
        f"{len(FIFA_ASSOCIATIONS)}"
    )

    print()

    created = 0
    updated = 0
    skipped = 0

    missing_countries = []

    # --------------------------------------------------------
    # Process each FIFA association
    # --------------------------------------------------------

    for association in FIFA_ASSOCIATIONS:

        country = find_country(association)

        # ----------------------------------------------------
        # Country not found
        # ----------------------------------------------------

        if not country:

            missing_countries.append(
                association["name"]
            )

            print(
                f"⚠️ Country not found: "
                f"{association['name']} "
                f"({association['short_name']})"
            )

            continue

        # ----------------------------------------------------
        # Male team
        # ----------------------------------------------------

        result = create_or_update_team(
            country=country,
            association=association,
            gender="Male",
            nickname=association["male_nickname"]
        )

        if result == "created":
            created += 1

            print(
                f"✅ Male:   "
                f"{country.name} "
                f"→ {association['male_nickname']}"
            )

        elif result == "updated":
            updated += 1

        # ----------------------------------------------------
        # Female team
        # ----------------------------------------------------

        result = create_or_update_team(
            country=country,
            association=association,
            gender="Female",
            nickname=association["female_nickname"]
        )

        if result == "created":
            created += 1

            print(
                f"✅ Female: "
                f"{country.name} "
                f"→ {association['female_nickname']}"
            )

        elif result == "updated":
            updated += 1

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    try:

        db.session.commit()

        print()
        print("=" * 70)
        print(" SEEDING COMPLETED")
        print("=" * 70)

        print()
        print(f"Associations processed : {len(FIFA_ASSOCIATIONS)}")
        print(f"Teams created          : {created}")
        print(f"Teams updated          : {updated}")
        print(f"Expected teams         : {len(FIFA_ASSOCIATIONS) * 2}")
        print()

        # ----------------------------------------------------
        # Missing countries
        # ----------------------------------------------------

        if missing_countries:

            print("=" * 70)
            print(" ⚠️ COUNTRIES NOT FOUND")
            print("=" * 70)

            for country_name in missing_countries:
                print(f" - {country_name}")

            print()
            print(
                "These countries were skipped because "
                "they were not found in the countries table."
            )

        else:

            print(
                "✅ All FIFA associations matched "
                "to the countries table."
            )

        print()

        # ----------------------------------------------------
        # Count database records
        # ----------------------------------------------------

        total_teams = NationalTeam.query.count()

        print(
            f"National teams currently in database: "
            f"{total_teams}"
        )

        print()

    except Exception as e:

        db.session.rollback()

        print()
        print("=" * 70)
        print("❌ SEEDING FAILED")
        print("=" * 70)
        print()
        print(str(e))
        print()

        raise


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if __name__ == "__main__":

    app = create_app()

    with app.app_context():

        seed_national_teams()