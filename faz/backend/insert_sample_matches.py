# backend/insert_sample_matches.py
from app.database import SessionLocal
from app.models import Match, Team
from datetime import datetime, timedelta
import random

db = SessionLocal()

print("=" * 60)
print("Inserting Sample Match Data")
print("=" * 60)

# Get all teams
teams = db.query(Team).all()
team_names = [team.name for team in teams]

if len(team_names) < 2:
    print("Not enough teams found! Please run insert_league_data.py first.")
    exit()

# Sample matches data
matches_data = [
    # Upcoming matches (future dates)
    {"home_team": "ZESCO United FC", "away_team": "Nkana FC", "match_date": datetime.now() + timedelta(days=3), "venue": "Levy Mwanawasa Stadium", "competition": "Super League", "status": "upcoming"},
    {"home_team": "Power Dynamos FC", "away_team": "Red Arrows FC", "match_date": datetime.now() + timedelta(days=5), "venue": "Arthur Davies Stadium", "competition": "Super League", "status": "upcoming"},
    {"home_team": "Green Buffaloes FC", "away_team": "Kabwe Warriors FC", "match_date": datetime.now() + timedelta(days=7), "venue": "Independence Stadium", "competition": "Super League", "status": "upcoming"},
    {"home_team": "Mufulira Wanderers FC", "away_team": "NAPSA Stars FC", "match_date": datetime.now() + timedelta(days=10), "venue": "Shinde Stadium", "competition": "Super League", "status": "upcoming"},
    {"home_team": "ZANACO FC", "away_team": "FC MUZA", "match_date": datetime.now() + timedelta(days=12), "venue": "Sunset Stadium", "competition": "Super League", "status": "upcoming"},
    {"home_team": "Nchanga Rangers FC", "away_team": "Green Eagles FC", "match_date": datetime.now() + timedelta(days=14), "venue": "Nchanga Stadium", "competition": "Super League", "status": "upcoming"},
    {"home_team": "Mutondo Stars FC", "away_team": "Atletico Lusaka FC", "match_date": datetime.now() + timedelta(days=16), "venue": "Levy Mwanawasa Stadium", "competition": "Super League", "status": "upcoming"},
    {"home_team": "Forest Rangers FC", "away_team": "Lumwana Radiants FC", "match_date": datetime.now() + timedelta(days=18), "venue": "Levy Mwanawasa Stadium", "competition": "Super League", "status": "upcoming"},
    
    # Live matches (today)
    {"home_team": "ZESCO Ndola Girls FC", "away_team": "Green Buffaloes Women FC", "match_date": datetime.now(), "venue": "Levy Mwanawasa Stadium", "competition": "Women's Super League", "status": "live", "home_score": 1, "away_score": 0},
    {"home_team": "Indeni Roses FC", "away_team": "Red Arrows Women FC", "match_date": datetime.now(), "venue": "Indeni Stadium", "competition": "Women's Super League", "status": "live", "home_score": 0, "away_score": 1},
    
    # Finished matches (past dates)
    {"home_team": "ZESCO United FC", "away_team": "Power Dynamos FC", "match_date": datetime.now() - timedelta(days=7), "venue": "Levy Mwanawasa Stadium", "competition": "Super League", "status": "finished", "home_score": 2, "away_score": 1},
    {"home_team": "Nkana FC", "away_team": "Red Arrows FC", "match_date": datetime.now() - timedelta(days=5), "venue": "Nkana Stadium", "competition": "Super League", "status": "finished", "home_score": 1, "away_score": 1},
    {"home_team": "Kabwe Warriors FC", "away_team": "Green Buffaloes FC", "match_date": datetime.now() - timedelta(days=3), "venue": "Godfrey Chitalu Stadium", "competition": "Super League", "status": "finished", "home_score": 0, "away_score": 2},
    {"home_team": "NAPSA Stars FC", "away_team": "Mufulira Wanderers FC", "match_date": datetime.now() - timedelta(days=2), "venue": "NAPSA Stadium", "competition": "Super League", "status": "finished", "home_score": 3, "away_score": 0},
    {"home_team": "FC MUZA", "away_team": "ZANACO FC", "match_date": datetime.now() - timedelta(days=1), "venue": "MUZA Stadium", "competition": "Super League", "status": "finished", "home_score": 2, "away_score": 2},
    
    # Women's finished matches
    {"home_team": "ZESCO Ndola Girls FC", "away_team": "Indeni Roses FC", "match_date": datetime.now() - timedelta(days=4), "venue": "Levy Mwanawasa Stadium", "competition": "Women's Super League", "status": "finished", "home_score": 3, "away_score": 1},
    {"home_team": "Green Buffaloes Women FC", "away_team": "Red Arrows Women FC", "match_date": datetime.now() - timedelta(days=2), "venue": "Independence Stadium", "competition": "Women's Super League", "status": "finished", "home_score": 2, "away_score": 0},
]

print("\n📊 Inserting matches...")
count = 0
skipped = 0

for match_data in matches_data:
    # Check if teams exist
    home_team = db.query(Team).filter(Team.name == match_data["home_team"]).first()
    away_team = db.query(Team).filter(Team.name == match_data["away_team"]).first()
    
    if not home_team:
        print(f"  ⚠️ Home team not found: {match_data['home_team']}")
        skipped += 1
        continue
    if not away_team:
        print(f"  ⚠️ Away team not found: {match_data['away_team']}")
        skipped += 1
        continue
    
    # Check if match already exists (simple check by teams and date)
    existing = db.query(Match).filter(
        Match.home_team == match_data["home_team"],
        Match.away_team == match_data["away_team"],
        Match.match_date == match_data["match_date"]
    ).first()
    
    if existing:
        print(f"  Skipped (exists): {match_data['home_team']} vs {match_data['away_team']}")
        skipped += 1
        continue
    
    match = Match(
        home_team=match_data["home_team"],
        away_team=match_data["away_team"],
        home_score=match_data.get("home_score", 0),
        away_score=match_data.get("away_score", 0),
        match_date=match_data["match_date"],
        venue=match_data["venue"],
        competition=match_data["competition"],
        status=match_data["status"],
        is_home_match=True
    )
    db.add(match)
    count += 1
    print(f"  Added: {match_data['home_team']} vs {match_data['away_team']} ({match_data['status']})")

db.commit()

print("\n" + "=" * 60)
print("🎉 MATCHES INSERTION COMPLETE! 🎉")
print("=" * 60)
print(f"\nSummary:")
print(f"  - Matches added: {count}")
print(f"  - Skipped: {skipped}")
print(f"\nNow you can view matches at:")
print(f"  - /matches (all matches)")
print(f"  - /matches?status=upcoming (upcoming matches)")
print(f"  - /matches?status=live (live matches)")
print(f"  - /matches?status=finished (finished matches)")

db.close()