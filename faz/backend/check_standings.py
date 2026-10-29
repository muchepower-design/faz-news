# backend/check_standings.py
from app.database import SessionLocal
from app.models import LeagueStanding, League

db = SessionLocal()

# Check if there are any standings
count = db.query(LeagueStanding).count()
print(f"Total standings records: {count}")

# Check leagues
leagues = db.query(League).all()
print(f"Leagues in database: {[l.name for l in leagues]}")

if count == 0:
    print("\n⚠️ No standings data found! You need to add league standings.")
    print("You can insert sample standings via admin panel or SQL.")
else:
    # Show sample
    sample = db.query(LeagueStanding).first()
    print(f"\nSample standing: League ID {sample.league_id}, Team ID {sample.team_id}, Points {sample.points}")

db.close()