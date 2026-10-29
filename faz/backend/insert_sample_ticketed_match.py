import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app import create_app
from app.database import db
from app.models import Match, TicketType, Club
from datetime import datetime, timedelta

app = create_app()

# Helper to create a club if it doesn't exist
def get_or_create_club(name, short_name):
    club = Club.query.filter_by(name=name).first()
    if not club:
        club = Club(name=name, short_name=short_name, is_active=True)
        db.session.add(club)
        db.session.commit()
    return club

# Helper to create a match if it doesn't exist (by checking home/away/date)
def create_match_if_not_exists(home_team, away_team, venue, match_date, competition,
                              status='upcoming', is_ticketed=True, club_id=None):
    # Check if match already exists (within 1 minute tolerance)
    existing = Match.query.filter(
        Match.home_team == home_team,
        Match.away_team == away_team,
        Match.match_date >= match_date - timedelta(minutes=1),
        Match.match_date <= match_date + timedelta(minutes=1)
    ).first()
    if existing:
        print(f"Match already exists: {home_team} vs {away_team}")
        return existing

    match = Match(
        home_team=home_team,
        away_team=away_team,
        venue=venue,
        match_date=match_date,
        competition=competition,
        status=status,
        is_ticketed=is_ticketed,
        club_id=club_id
    )
    db.session.add(match)
    db.session.flush()

    # Add ticket types only if ticketed
    if is_ticketed:
        ticket_types = [
            {"name": "Standard", "price": 50.00, "capacity": 100},
            {"name": "VIP", "price": 150.00, "capacity": 20},
            {"name": "VVIP", "price": 300.00, "capacity": 5},
        ]
        for tt_data in ticket_types:
            tt = TicketType(
                match_id=match.id,
                name=tt_data['name'],
                price=tt_data['price'],
                capacity=tt_data['capacity']
            )
            db.session.add(tt)
    db.session.commit()
    print(f"Created: {home_team} vs {away_team} ({competition})")
    return match

def main():
    with app.app_context():
        # ---- Create clubs ----
        clubs = {
            "zesco": get_or_create_club("ZESCO United", "ZESCO"),
            "nkana": get_or_create_club("Nkana FC", "Nkana"),
            "power": get_or_create_club("Power Dynamos", "Power"),
            "arrows": get_or_create_club("Red Arrows FC", "Arrows"),
            "buffaloes": get_or_create_club("Green Buffaloes", "Buffaloes"),
            "kabwe": get_or_create_club("Kabwe Warriors", "Warriors"),
        }

        now = datetime.now()

        # ---- NATIONAL TEAM MATCHES (club_id = NULL) ----
        national_matches = [
            # World Cup Qualifiers (Africa)
            {"home": "Chipolopolo", "away": "Morocco", "date": now + timedelta(days=5), "comp": "World Cup Qualifier"},
            {"home": "Chipolopolo", "away": "Nigeria", "date": now + timedelta(days=12), "comp": "World Cup Qualifier"},
            {"home": "Chipolopolo", "away": "Cameroon", "date": now + timedelta(days=19), "comp": "World Cup Qualifier"},
            {"home": "Chipolopolo", "away": "Egypt", "date": now + timedelta(days=26), "comp": "World Cup Qualifier"},
            {"home": "Chipolopolo", "away": "Senegal", "date": now + timedelta(days=33), "comp": "World Cup Qualifier"},
            {"home": "Chipolopolo", "away": "Algeria", "date": now + timedelta(days=40), "comp": "World Cup Qualifier"},
            {"home": "Chipolopolo", "away": "Ghana", "date": now + timedelta(days=47), "comp": "World Cup Qualifier"},
            {"home": "Chipolopolo", "away": "DRC", "date": now + timedelta(days=54), "comp": "World Cup Qualifier"},
            {"home": "Chipolopolo", "away": "Tunisia", "date": now + timedelta(days=61), "comp": "World Cup Qualifier"},
            # Friendly against non-African
            {"home": "Chipolopolo", "away": "Brazil", "date": now + timedelta(days=80), "comp": "International Friendly"},
            {"home": "Chipolopolo", "away": "Germany", "date": now + timedelta(days=90), "comp": "International Friendly"},
            {"home": "Chipolopolo", "away": "England", "date": now + timedelta(days=100), "comp": "International Friendly"},
            # Past matches (finished)
            {"home": "Chipolopolo", "away": "South Africa", "date": now - timedelta(days=2), "comp": "COSAFA Cup", "status": "finished"},
            {"home": "Chipolopolo", "away": "Zimbabwe", "date": now - timedelta(days=10), "comp": "COSAFA Cup", "status": "finished"},
        ]

        for m in national_matches:
            create_match_if_not_exists(
                home_team=m["home"],
                away_team=m["away"],
                venue="National Heroes Stadium, Lusaka",
                match_date=m["date"],
                competition=m["comp"],
                status=m.get("status", "upcoming"),
                is_ticketed=True,
                club_id=None  # national matches have no club
            )

        # ---- CLUB MATCHES (domestic) ----
        club_matches = [
            # Super League
            {"home": "ZESCO United", "away": "Nkana FC", "date": now + timedelta(days=3), "comp": "Super League"},
            {"home": "Power Dynamos", "away": "Red Arrows FC", "date": now + timedelta(days=6), "comp": "Super League"},
            {"home": "Green Buffaloes", "away": "Kabwe Warriors", "date": now + timedelta(days=8), "comp": "Super League"},
            {"home": "Nkana FC", "away": "Power Dynamos", "date": now + timedelta(days=14), "comp": "Super League"},
            {"home": "ZESCO United", "away": "Red Arrows FC", "date": now + timedelta(days=18), "comp": "Super League"},
            {"home": "Kabwe Warriors", "away": "Green Buffaloes", "date": now + timedelta(days=22), "comp": "Super League"},
            # Past matches
            {"home": "ZESCO United", "away": "Power Dynamos", "date": now - timedelta(days=5), "comp": "Super League", "status": "finished"},
            {"home": "Nkana FC", "away": "Green Buffaloes", "date": now - timedelta(days=12), "comp": "Super League", "status": "finished"},
        ]

        for m in club_matches:
            # Determine club_id based on home team name (assuming we have all clubs in dict)
            club_id = None
            # Map home team name to club id
            if m["home"] == "ZESCO United":
                club_id = clubs["zesco"].id
            elif m["home"] == "Nkana FC":
                club_id = clubs["nkana"].id
            elif m["home"] == "Power Dynamos":
                club_id = clubs["power"].id
            elif m["home"] == "Red Arrows FC":
                club_id = clubs["arrows"].id
            elif m["home"] == "Green Buffaloes":
                club_id = clubs["buffaloes"].id
            elif m["home"] == "Kabwe Warriors":
                club_id = clubs["kabwe"].id
            # For away teams, we still use the home club's id – we could also use away club id, but we'll use home club
            # In ticketing, the match is associated with the home club's tickets
            create_match_if_not_exists(
                home_team=m["home"],
                away_team=m["away"],
                venue="Various Stadiums",  # you can specify actual venues if you want
                match_date=m["date"],
                competition=m["comp"],
                status=m.get("status", "upcoming"),
                is_ticketed=True,
                club_id=club_id
            )

        # ---- CONTINENTAL CLUB MATCHES ----
        continental_matches = [
            {"home": "ZESCO United", "away": "Al Ahly (Egypt)", "date": now + timedelta(days=20), "comp": "CAF Champions League"},
            {"home": "ZESCO United", "away": "TP Mazembe (DRC)", "date": now + timedelta(days=35), "comp": "CAF Champions League"},
            {"home": "Power Dynamos", "away": "Mamelodi Sundowns (RSA)", "date": now + timedelta(days=28), "comp": "CAF Confederation Cup"},
            {"home": "Nkana FC", "away": "AS Vita Club (DRC)", "date": now + timedelta(days=45), "comp": "CAF Confederation Cup"},
            # Past
            {"home": "ZESCO United", "away": "ES Tunis (Tunisia)", "date": now - timedelta(days=8), "comp": "CAF Champions League", "status": "finished"},
        ]

        for m in continental_matches:
            club_id = None
            if m["home"] == "ZESCO United":
                club_id = clubs["zesco"].id
            elif m["home"] == "Power Dynamos":
                club_id = clubs["power"].id
            elif m["home"] == "Nkana FC":
                club_id = clubs["nkana"].id
            create_match_if_not_exists(
                home_team=m["home"],
                away_team=m["away"],
                venue="Levy Mwanawasa Stadium, Ndola" if "ZESCO" in m["home"] else "Arthur Davies Stadium, Kitwe",
                match_date=m["date"],
                competition=m["comp"],
                status=m.get("status", "upcoming"),
                is_ticketed=True,
                club_id=club_id
            )

        print("✅ All matches inserted successfully.")

if __name__ == "__main__":
    main()