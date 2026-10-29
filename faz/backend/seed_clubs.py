# ============================================================
# seed_clubs.py
#
# Seeds the `clubs` table from:
#     ZPL TEAM LIST AND GROUPING coach.xlsx
#
# IMPORTANT:
# Only fields that exist in the Club model are inserted:
#     id
#     name
#     short_name
#     age
#     gender
#     logo_url
#     description
#     is_active
#     country_id
#
# The following Excel columns are intentionally NOT inserted:
#     Town/City
#     Province
#     League/Zone/Grouping
#
# Existing clubs are detected by normalized name, so names such as:
#     ZESCO United
#     ZESCO United FC
#     ZESCO United Football Club
# are treated as the same club.
#
# Country:
#     e5bca288-206e-45a9-9cc6-726f6a568082
#
# This file follows the same Flask application/database pattern as
# the working seed_fifa_211.py:
#
#     from app import create_app, db
#     ...
#     app = create_app()
#     with app.app_context():
#         seed_clubs()
#
# Run from the backend/project root:
#     python seed_clubs.py
# ============================================================


import sys
import os
import re
import uuid
import unicodedata

import pandas as pd


# ============================================================
# ADD BACKEND DIRECTORY TO PYTHON PATH
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


# ============================================================
# IMPORT FLASK APPLICATION
# ============================================================

from app import create_app, db
from app.models.club import Club


# ============================================================
# CONFIGURATION
# ============================================================

COUNTRY_ID = uuid.UUID(
    "e5bca288-206e-45a9-9cc6-726f6a568082"
)

EXCEL_FILE = os.path.join(
    BASE_DIR,
    "ZPL TEAM LIST AND GROUPING coach.xlsx"
)


# ============================================================
# TEXT HELPERS
# ============================================================

def clean_text(value):
    """Clean Excel/database text without changing its meaning."""

    if value is None or pd.isna(value):
        return None

    value = unicodedata.normalize("NFKC", str(value))
    value = value.replace("\xa0", " ")
    value = re.sub(r"\s+", " ", value).strip()

    return value or None


def normalize_club_name(name):
    """
    Normalize club names for duplicate detection.

    Examples considered the same:
        ZESCO United
        ZESCO United FC
        ZESCO United Football Club

        FC MUZA
        MUZA

        Nkana
        Nkana FC

        Mufurila Wonderers
        Mufulira Wanderers
    """

    name = clean_text(name) or ""
    name = name.lower()

    # Normalize apostrophes.
    name = name.replace("’", "'")

    # Remove common football suffixes.
    name = re.sub(
        r"\bfootball\s+club\b",
        "",
        name,
        flags=re.IGNORECASE,
    )

    name = re.sub(
        r"\bfc\b",
        "",
        name,
        flags=re.IGNORECASE,
    )

    # Normalize common spelling/name variations.
    name = re.sub(r"\s+", " ", name).strip()

    aliases = {
        "mufurila wonderers": "mufulira wanderers",
        "mufurila wanderers": "mufulira wanderers",

        "muza": "muza",
        "fc muza": "muza",

        "nkana qeens": "nkana queens",
        "nkana queen": "nkana queens",

        "leopards": "leopards",
        "fc leopards": "leopards",

        "napsa": "napsa stars",
        "napsa stars": "napsa stars",

        "zanaco": "zanaco",
        "zanaco ladies": "zanaco ladies",

        "green buffaloes women": "green buffaloes women",
        "green eagles women": "green eagles women",

        "red arrows women": "red arrows women",

        "power dynamos queens": "power dynamos queens",
        "mufulira wanderers queens": "mufulira wanderers queens",

        "fc muza queens": "muza queens",
        "muza queens": "muza queens",
    }

    return aliases.get(name, name)


# ============================================================
# SHORT NAMES
# ============================================================

# These are used where a commonly used club short name is known.
# For clubs not listed here, a safe short form is generated below.
SHORT_NAMES = {

    # Men's Super League
    "FC MUZA": "MUZA",
    "Kansanshi Dynamos": "Kansanshi",
    "Konkola Blades": "Konkola",
    "Makeni All Stars": "Makeni All Stars",
    "NAPSA Stars": "NAPSA",
    "Nchanga Rangers": "Nchanga Rangers",
    "Nkana FC": "Nkana",
    "Power Dynamos": "Power Dynamos",
    "Trident": "Trident",
    "ZANACO FC": "ZANACO",

    "Chirundu United FC": "Chirundu United",
    "Green Buffaloes": "Green Buffaloes",
    "Green Eagles": "Green Eagles",
    "Kabwe Warriors": "Kabwe Warriors",
    "Mufulira Wanderers": "Mufulira Wanderers",
    "Mutondo Stars": "Mutondo Stars",
    "Nkwazi FC": "Nkwazi",
    "Red Arrows": "Red Arrows",
    "Roan United": "Roan United",
    "ZESCO United": "ZESCO",

    # Men's National Division
    "Chambishi FC": "Chambishi",
    "Mines United": "Mines United",
    "FC Leopards": "Leopards",
    "Jumulo FC": "Jumulo",
    "Kitwe United": "Kitwe United",
    "Lumwana Radiants": "Lumwana Radiants",
    "Forest Rangers": "Forest Rangers",
    "Mathkat United": "Mathkat United",
    "Indeni FC": "Indeni",
    "Ndola United": "Ndola United",
    "Chipata City Council": "Chipata City",
    "Mikalile FC": "Mikalile",
    "Play It Forward": "Play It Forward",
    "Aguila Stars": "Aguila Stars",
    "Atletico Lusaka": "Atletico Lusaka",
    "Kafue Celtic": "Kafue Celtic",
    "River Plate": "River Plate",
    "Locus FC": "Locus",
    "Forest Myooye": "Forest Myooye",
    "Nampundwe FC": "Nampundwe",
    "Choma Warriors Academy": "Choma Warriors",

    # Women's teams
    "AmeZam Tamanga Queens": "AmeZam Queens",
    "ZANACO Ladies": "ZANACO Ladies",
    "ZISD FC": "ZISD",
    "Green Buffaloes Women": "GB Women",
    "Green Eagles Women": "GE Women",
    "Luyando Sporting FC": "Luyando",
    "National Assembly Women": "NA Women",
    "Red Arrows Women": "Red Arrows Women",
    "The Elite Ladies": "Elite Ladies",
    "YASA Queens": "YASA Queens",

    "Konkola Blades Queens": "Konkola Queens",
    "Nchanga Rangers Queens": "Nchanga Queens",
    "Leopards Queens": "Leopards Queens",
    "Amazing Grace FC": "Amazing Grace",
    "Trident Queens": "Trident Queens",
    "Kamfinsa Blue Eagles Queens": "Blue Eagles Queens",
    "Kansanshi Queens": "Kansanshi Queens",
    "Indeni Roses": "Indeni Roses",
    "ZESCO Ndola Girls": "ZESCO Girls",

    "Bwacha Pirates": "Bwacha Pirates",
    "Lunchu Queens": "Lunchu Queens",
    "Chitapankwa Girls": "Chitapankwa Girls",
    "Clemsons Queens": "Clemsons Queens",
    "Sporting Doves": "Sporting Doves",
    "Ntindi Shining Stars": "Ntindi Stars",
    "Mwenzo Queens": "Mwenzo Queens",

    "Mimbula Minerals Amazons FC": "Mimbula Amazons",
    "Kalumbila Queens": "Kalumbila Queens",
    "Chalube Angels": "Chalube Angels",
    "Power Dynamos Queens": "Power Dynamos Women",
    "Manyama Queens": "Manyama Queens",
    "Mufulira Wanderers Queens": "Mufulira Queens",
    "Fibunde Stars": "Fibunde Stars",
    "Dove Queens": "Dove Queens",
    "Nkana Qeens": "Nkana Queens",
    "Driven Queens": "Driven Queens",

    "Kabwe Warriors Ladies": "Kabwe Warriors Women",
    "Pataaki Girls": "Pataaki Girls",
    "Locus Women FC": "Locus Women",
    "Young Green Buffaloes Women": "Young GB Women",
    "Barts Queens": "Barts Queens",
    "Play It Forward Queens": "Play It Forward Women",
    "FC MUZA Queens": "MUZA Women",
    "Nampundwe Queens": "Nampundwe Queens",
    "Pemba Queens": "Pemba Queens",

    "ZedPro Sports Foundation": "ZedPro",
    "Young Elite Ladies": "Young Elite",
    "Valley Queens": "Valley Queens",
    "Chipata Girls": "Chipata Girls",
    "Kum'mawa Stars Queens": "Kum'mawa Stars",
    "Panzer Queens": "Panzer Queens",
    "BUSA Queens": "BUSA Queens",
    "Chainda Bombers Ladies": "Chainda Bombers",
    "Nkwazi Queens": "Nkwazi Queens",
}


def get_short_name(name):
    """Return a known short name or generate a safe fallback."""

    if name in SHORT_NAMES:
        return SHORT_NAMES[name]

    short = name

    short = re.sub(
        r"\bFootball Club\b",
        "",
        short,
        flags=re.IGNORECASE,
    )

    short = re.sub(
        r"\bFC\b",
        "",
        short,
        flags=re.IGNORECASE,
    )

    short = re.sub(
        r"\bLadies\b",
        "",
        short,
        flags=re.IGNORECASE,
    )

    short = re.sub(
        r"\s+",
        " ",
        short,
    ).strip()

    return short[:50]


# ============================================================
# DESCRIPTIONS
# ============================================================

# Specific descriptions where the club's identity is reasonably
# established. For other clubs we deliberately use a neutral
# description rather than inventing sponsorship/history.

DESCRIPTION_OVERRIDES = {
    "ZESCO United": (
        "Zambian football club based in Ndola and associated with ZESCO."
    ),

    "Red Arrows": (
        "Zambian football club based in Lusaka and associated with the "
        "Zambia Air Force."
    ),

    "ZANACO FC": (
        "Zambian football club based in Lusaka and associated with "
        "Zambia National Commercial Bank."
    ),

    "Green Buffaloes": (
        "Zambian football club based in Lusaka and associated with the "
        "Zambia Army."
    ),

    "Green Eagles": (
        "Zambian football club based in Choma and associated with the "
        "Zambia National Service."
    ),

    "Kabwe Warriors": (
        "Historic Zambian football club based in Kabwe."
    ),

    "Power Dynamos": (
        "Zambian football club based in Kitwe."
    ),

    "Nkana FC": (
        "Historic Zambian football club based in Kitwe."
    ),

    "Mufulira Wanderers": (
        "Historic Zambian football club based in Mufulira."
    ),

    "NAPSA Stars": (
        "Zambian football club based in Lusaka and associated with "
        "the National Pension Scheme Authority."
    ),

    "Nkwazi FC": (
        "Zambian football club based in Lusaka and associated with "
        "the Zambia Police Service."
    ),

    "Kansanshi Dynamos": (
        "Zambian football club based in Solwezi."
    ),

    "Konkola Blades": (
        "Zambian football club based in Chililabombwe."
    ),

    "Nchanga Rangers": (
        "Zambian football club based in Chingola."
    ),

    "FC MUZA": (
        "Zambian football club based in Mazabuka."
    ),

    "Trident": (
        "Zambian football club based in Kalumbila."
    ),
}


def make_description(name, city, gender):
    """
    Create a neutral description.

    For known clubs, use the researched description above.
    Otherwise use the club's name and supplied town/city without
    adding information that is not supported by the workbook.
    """

    if name in DESCRIPTION_OVERRIDES:
        return DESCRIPTION_OVERRIDES[name]

    if gender == "female":
        if city:
            return f"Zambian women's football club based in {city}."
        return "Zambian women's football club."

    if city:
        return f"Zambian football club based in {city}."

    return "Zambian football club."


# ============================================================
# READ EXCEL
# ============================================================

def read_clubs():
    """
    Read clubs from the supplied workbook.

    Only the club name is ultimately inserted into the Club model.
    Town/City and section are used only to determine a neutral
    description and gender.
    """

    if not os.path.exists(EXCEL_FILE):
        raise FileNotFoundError(
            f"Could not find Excel file:\n{EXCEL_FILE}"
        )

    workbook = pd.read_excel(
        EXCEL_FILE,
        sheet_name=0,
        header=None,
    )

    # --------------------------------------------------------
    # Find the actual header row
    # --------------------------------------------------------

    header_row = None

    for row_number, row in workbook.iterrows():

        values = [
            clean_text(value)
            for value in row.tolist()
        ]

        if (
            "Club" in values
            and "Town/City" in values
            and "Province" in values
        ):
            header_row = row_number
            break

    if header_row is None:
        raise ValueError(
            "Could not find the Club / Town/City / Province headers."
        )

    clubs = []
    current_section = ""

    # --------------------------------------------------------
    # Read club rows
    # --------------------------------------------------------

    for _, row in workbook.iloc[header_row + 1:].iterrows():

        number = (
            clean_text(row.iloc[1])
            if len(row) > 1
            else None
        )

        name = (
            clean_text(row.iloc[2])
            if len(row) > 2
            else None
        )

        city = (
            clean_text(row.iloc[3])
            if len(row) > 3
            else None
        )

        province = (
            clean_text(row.iloc[4])
            if len(row) > 4
            else None
        )

        if not name:
            continue

        # Section heading.
        if (
            number is None
            and city is None
            and province is None
        ):
            current_section = name
            continue

        # Only numbered rows are clubs.
        if number is None:
            continue

        section_lower = current_section.lower()

        if (
            "women" in section_lower
            or "wsd" in section_lower
            or "wnd" in section_lower
        ):
            gender = "Female"
        else:
            gender = "Male"

        clubs.append({
            "name": name,
            "city": city,
            "gender": gender,
        })

    return clubs


# ============================================================
# CREATE CLUB
# ============================================================

def create_club(name, city, gender):
    """
    Create one Club model instance.

    IMPORTANT:
    Only fields that exist in the supplied Club model are used.
    """

    return Club(
        id=uuid.uuid4(),
        name=name,
        short_name=get_short_name(name),
        age="Senior",
        gender=gender,
        logo_url=None,
        description=make_description(
            name=name,
            city=city,
            gender=gender,
        ),
        is_active=True,
        country_id=COUNTRY_ID,
    )


# ============================================================
# DATABASE SEEDING
# ============================================================

def seed_clubs():

    print()
    print("=" * 70)
    print(" ZPL CLUBS SEEDER")
    print("=" * 70)
    print()

    clubs_from_excel = read_clubs()

    print(
        f"Clubs found in Excel: {len(clubs_from_excel)}"
    )

    print()

    created = 0
    skipped = 0

    skipped_clubs = []
    inserted_clubs = []

    # --------------------------------------------------------
    # Load existing clubs
    # --------------------------------------------------------

    existing_clubs = Club.query.all()

    existing_normalized = {
        normalize_club_name(club.name)
        for club in existing_clubs
        if club.name
    }

    # Prevent duplicate entries inside the Excel file.
    processed = set()

    # --------------------------------------------------------
    # Insert clubs
    # --------------------------------------------------------

    for item in clubs_from_excel:

        name = clean_text(item["name"])

        if not name:
            continue

        normalized = normalize_club_name(name)

        # Duplicate inside Excel.
        if normalized in processed:

            skipped += 1

            skipped_clubs.append(
                (name, "duplicate in Excel")
            )

            continue

        processed.add(normalized)

        # Already exists in database.
        if normalized in existing_normalized:

            skipped += 1

            skipped_clubs.append(
                (name, "already exists")
            )

            continue

        club = create_club(
            name=name,
            city=item["city"],
            gender=item["gender"],
        )

        db.session.add(club)

        existing_normalized.add(normalized)

        inserted_clubs.append(name)
        created += 1

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
        print(
            f"Clubs found in Excel : {len(clubs_from_excel)}"
        )

        print(
            f"Clubs created        : {created}"
        )

        print(
            f"Clubs skipped         : {skipped}"
        )

        print()

        # ----------------------------------------------------
        # Inserted clubs
        # ----------------------------------------------------

        if inserted_clubs:

            print("=" * 70)
            print(" INSERTED CLUBS")
            print("=" * 70)

            for name in inserted_clubs:
                print(f"✅ {name}")

            print()

        # ----------------------------------------------------
        # Skipped clubs
        # ----------------------------------------------------

        if skipped_clubs:

            print("=" * 70)
            print(" SKIPPED CLUBS")
            print("=" * 70)

            for name, reason in skipped_clubs:
                print(f"⚠️ {name} → {reason}")

            print()

        # ----------------------------------------------------
        # Current database count
        # ----------------------------------------------------

        total_clubs = Club.query.count()

        print(
            f"Clubs currently in database: {total_clubs}"
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

        seed_clubs()
