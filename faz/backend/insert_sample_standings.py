# backend/insert_sample_standings.py
from app.database import SessionLocal
from app.models import LeagueStanding, League, Team
from sqlalchemy.orm import joinedload

db = SessionLocal()

print("=" * 60)
print("Inserting Sample League Standings")
print("=" * 60)

# Helper function to create standings
def create_standings(league_name, team_filter, season, standings_data):
    league = db.query(League).filter(League.name == league_name).first()
    if not league:
        print(f"  League '{league_name}' not found!")
        return 0
    
    # Get teams for this league
    teams = db.query(Team).filter(team_filter).all()
    if not teams:
        print(f"  No teams found for league '{league_name}'!")
        return 0
    
    count = 0
    for idx, team in enumerate(teams[:len(standings_data)]):
        if idx >= len(standings_data):
            break
        data = standings_data[idx]
        
        existing = db.query(LeagueStanding).filter(
            LeagueStanding.league_id == league.id,
            LeagueStanding.team_id == team.id,
            LeagueStanding.season == season
        ).first()
        
        if not existing:
            standing = LeagueStanding(
                league_id=league.id,
                team_id=team.id,
                season=season,
                played=data['played'],
                won=data['won'],
                drawn=data['drawn'],
                lost=data['lost'],
                goals_for=data['goals_for'],
                goals_against=data['goals_against'],
                points=data['points']
            )
            db.add(standing)
            count += 1
            print(f"  Added: {team.name} - P{data['points']}")
        else:
            print(f"  Already exists: {team.name}")
    
    return count

# ============ MEN'S SUPER LEAGUE STANDINGS ============
print("\n📊 Men's Super League Standings:")
men_super_standings = [
    {"played": 18, "won": 14, "drawn": 3, "lost": 1, "goals_for": 42, "goals_against": 12, "points": 45},
    {"played": 18, "won": 12, "drawn": 4, "lost": 2, "goals_for": 38, "goals_against": 15, "points": 40},
    {"played": 18, "won": 11, "drawn": 3, "lost": 4, "goals_for": 35, "goals_against": 18, "points": 36},
    {"played": 18, "won": 10, "drawn": 4, "lost": 4, "goals_for": 30, "goals_against": 20, "points": 34},
    {"played": 18, "won": 9, "drawn": 5, "lost": 4, "goals_for": 28, "goals_against": 22, "points": 32},
    {"played": 18, "won": 8, "drawn": 5, "lost": 5, "goals_for": 25, "goals_against": 24, "points": 29},
    {"played": 18, "won": 7, "drawn": 4, "lost": 7, "goals_for": 24, "goals_against": 25, "points": 25},
    {"played": 18, "won": 6, "drawn": 5, "lost": 7, "goals_for": 22, "goals_against": 26, "points": 23},
    {"played": 18, "won": 5, "drawn": 5, "lost": 8, "goals_for": 20, "goals_against": 28, "points": 20},
    {"played": 18, "won": 4, "drawn": 6, "lost": 8, "goals_for": 18, "goals_against": 30, "points": 18},
    {"played": 18, "won": 4, "drawn": 3, "lost": 11, "goals_for": 16, "goals_against": 34, "points": 15},
    {"played": 18, "won": 3, "drawn": 5, "lost": 10, "goals_for": 14, "goals_against": 32, "points": 14},
    {"played": 18, "won": 3, "drawn": 4, "lost": 11, "goals_for": 12, "goals_against": 35, "points": 13},
    {"played": 18, "won": 2, "drawn": 5, "lost": 11, "goals_for": 10, "goals_against": 38, "points": 11},
    {"played": 18, "won": 2, "drawn": 4, "lost": 12, "goals_for": 9, "goals_against": 40, "points": 10},
    {"played": 18, "won": 1, "drawn": 5, "lost": 12, "goals_for": 8, "goals_against": 42, "points": 8},
    {"played": 18, "won": 1, "drawn": 4, "lost": 13, "goals_for": 7, "goals_against": 44, "points": 7},
    {"played": 18, "won": 0, "drawn": 4, "lost": 14, "goals_for": 5, "goals_against": 48, "points": 4},
]

men_super_count = create_standings(
    "MTN Super League", 
    Team.current_league_level == "super_league", 
    "2025-2026", 
    men_super_standings
)
print(f"  ✅ Added {men_super_count} standings for Men's Super League")

# ============ WOMEN'S SUPER LEAGUE STANDINGS ============
print("\n📊 Women's Super League Standings:")
women_super_standings = [
    {"played": 16, "won": 14, "drawn": 1, "lost": 1, "goals_for": 48, "goals_against": 8, "points": 43},
    {"played": 16, "won": 12, "drawn": 2, "lost": 2, "goals_for": 42, "goals_against": 10, "points": 38},
    {"played": 16, "won": 11, "drawn": 3, "lost": 2, "goals_for": 38, "goals_against": 12, "points": 36},
    {"played": 16, "won": 10, "drawn": 4, "lost": 2, "goals_for": 35, "goals_against": 14, "points": 34},
    {"played": 16, "won": 9, "drawn": 3, "lost": 4, "goals_for": 30, "goals_against": 18, "points": 30},
    {"played": 16, "won": 8, "drawn": 4, "lost": 4, "goals_for": 28, "goals_against": 20, "points": 28},
    {"played": 16, "won": 7, "drawn": 3, "lost": 6, "goals_for": 24, "goals_against": 22, "points": 24},
    {"played": 16, "won": 6, "drawn": 4, "lost": 6, "goals_for": 22, "goals_against": 24, "points": 22},
    {"played": 16, "won": 5, "drawn": 3, "lost": 8, "goals_for": 20, "goals_against": 28, "points": 18},
    {"played": 16, "won": 4, "drawn": 4, "lost": 8, "goals_for": 18, "goals_against": 32, "points": 16},
    {"played": 16, "won": 4, "drawn": 2, "lost": 10, "goals_for": 16, "goals_against": 36, "points": 14},
    {"played": 16, "won": 3, "drawn": 3, "lost": 10, "goals_for": 14, "goals_against": 38, "points": 12},
    {"played": 16, "won": 2, "drawn": 4, "lost": 10, "goals_for": 12, "goals_against": 40, "points": 10},
    {"played": 16, "won": 2, "drawn": 2, "lost": 12, "goals_for": 10, "goals_against": 44, "points": 8},
    {"played": 16, "won": 1, "drawn": 3, "lost": 12, "goals_for": 8, "goals_against": 46, "points": 6},
    {"played": 16, "won": 0, "drawn": 3, "lost": 13, "goals_for": 5, "goals_against": 48, "points": 3},
]

women_super_count = create_standings(
    "Women's Super League", 
    Team.current_league_level == "super_league", 
    "2025-2026", 
    women_super_standings
)
print(f"  ✅ Added {women_super_count} standings for Women's Super League")

# ============ MEN'S DIVISION 1 STANDINGS ============
print("\n📊 Men's National Division 1 Standings:")
men_div1_standings = [
    {"played": 16, "won": 12, "drawn": 3, "lost": 1, "goals_for": 38, "goals_against": 10, "points": 39},
    {"played": 16, "won": 11, "drawn": 3, "lost": 2, "goals_for": 35, "goals_against": 12, "points": 36},
    {"played": 16, "won": 10, "drawn": 4, "lost": 2, "goals_for": 32, "goals_against": 14, "points": 34},
    {"played": 16, "won": 9, "drawn": 4, "lost": 3, "goals_for": 30, "goals_against": 16, "points": 31},
    {"played": 16, "won": 8, "drawn": 3, "lost": 5, "goals_for": 26, "goals_against": 20, "points": 27},
    {"played": 16, "won": 7, "drawn": 4, "lost": 5, "goals_for": 24, "goals_against": 22, "points": 25},
    {"played": 16, "won": 6, "drawn": 4, "lost": 6, "goals_for": 22, "goals_against": 24, "points": 22},
    {"played": 16, "won": 5, "drawn": 5, "lost": 6, "goals_for": 20, "goals_against": 26, "points": 20},
]

men_div1_count = create_standings(
    "National Division 1", 
    Team.current_league_level == "division_one", 
    "2025-2026", 
    men_div1_standings
)
print(f"  ✅ Added {men_div1_count} standings for Men's Division 1")

# ============ WOMEN'S NATIONAL LEAGUE - SOUTHERN ============
print("\n📊 Women's National League - Southern Standings:")
women_south_standings = [
    {"played": 14, "won": 12, "drawn": 2, "lost": 0, "goals_for": 45, "goals_against": 5, "points": 38},
    {"played": 14, "won": 11, "drawn": 1, "lost": 2, "goals_for": 40, "goals_against": 8, "points": 34},
    {"played": 14, "won": 10, "drawn": 2, "lost": 2, "goals_for": 36, "goals_against": 10, "points": 32},
    {"played": 14, "won": 9, "drawn": 2, "lost": 3, "goals_for": 32, "goals_against": 12, "points": 29},
    {"played": 14, "won": 8, "drawn": 1, "lost": 5, "goals_for": 28, "goals_against": 18, "points": 25},
    {"played": 14, "won": 6, "drawn": 3, "lost": 5, "goals_for": 24, "goals_against": 20, "points": 21},
    {"played": 14, "won": 5, "drawn": 2, "lost": 7, "goals_for": 20, "goals_against": 26, "points": 17},
    {"played": 14, "won": 4, "drawn": 3, "lost": 7, "goals_for": 18, "goals_against": 28, "points": 15},
]

women_south_count = create_standings(
    "National Women's League - Southern", 
    Team.current_league_level == "national_league_south", 
    "2025-2026", 
    women_south_standings
)
print(f"  ✅ Added {women_south_count} standings for Women's National League - Southern")

# ============ WOMEN'S NATIONAL LEAGUE - NORTHERN ============
print("\n📊 Women's National League - Northern Standings:")
women_north_standings = [
    {"played": 14, "won": 11, "drawn": 2, "lost": 1, "goals_for": 42, "goals_against": 7, "points": 35},
    {"played": 14, "won": 10, "drawn": 3, "lost": 1, "goals_for": 38, "goals_against": 8, "points": 33},
    {"played": 14, "won": 9, "drawn": 3, "lost": 2, "goals_for": 35, "goals_against": 10, "points": 30},
    {"played": 14, "won": 8, "drawn": 2, "lost": 4, "goals_for": 30, "goals_against": 15, "points": 26},
    {"played": 14, "won": 7, "drawn": 2, "lost": 5, "goals_for": 26, "goals_against": 20, "points": 23},
    {"played": 14, "won": 5, "drawn": 3, "lost": 6, "goals_for": 22, "goals_against": 24, "points": 18},
    {"played": 14, "won": 4, "drawn": 2, "lost": 8, "goals_for": 18, "goals_against": 30, "points": 14},
    {"played": 14, "won": 3, "drawn": 1, "lost": 10, "goals_for": 14, "goals_against": 36, "points": 10},
]

women_north_count = create_standings(
    "National Women's League - Northern", 
    Team.current_league_level == "national_league_north", 
    "2025-2026", 
    women_north_standings
)
print(f"  ✅ Added {women_north_count} standings for Women's National League - Northern")

db.commit()

print("\n" + "=" * 60)
print("🎉 STANDINGS INSERTION COMPLETE! 🎉")
print("=" * 60)
print(f"\nSummary:")
print(f"  - Men's Super League: {men_super_count} teams")
print(f"  - Women's Super League: {women_super_count} teams")
print(f"  - Men's Division 1: {men_div1_count} teams")
print(f"  - Women's Southern: {women_south_count} teams")
print(f"  - Women's Northern: {women_north_count} teams")
print(f"\nTotal: {men_super_count + women_super_count + men_div1_count + women_south_count + women_north_count} standings added")
print("\nRun 'python check_standings.py' again to verify.")
db.close()