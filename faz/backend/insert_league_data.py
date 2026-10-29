from app.database import SessionLocal
from app.models import (
    Team, League, LeagueStanding, PromotionRelegationRule, Gender, LeagueLevel,
    CupCompetition, CupSeason, CupMatch, ContinentalQualification, NationalTeam
)
from sqlalchemy.orm import Session
import sys
from datetime import datetime, timedelta

db = SessionLocal()

# ============ HELPER FUNCTION ============
def update_or_create_team(name, gender, league_level, tier):
    """Update existing team or create new one with proper fields"""
    existing_team = db.query(Team).filter(Team.name == name).first()
    short = name[:3].upper()
    if existing_team:
        # Update existing team (in case fields are missing)
        existing_team.short_name = short
        existing_team.gender = gender
        existing_team.team_type = "club"
        existing_team.current_league_level = league_level
        existing_team.league_tier = tier
        if not existing_team.founded:
            existing_team.founded = 1900
        if not existing_team.stadium:
            existing_team.stadium = "TBA"
        if not existing_team.coach:
            existing_team.coach = "TBA"
        print(f"  Updated: {name}")
    else:
        # Create new team
        db.add(Team(
            name=name,
            short_name=short,
            gender=gender,
            team_type="club",
            current_league_level=league_level,
            league_tier=tier,
            founded=1900,
            stadium="TBA",
            coach="TBA"
        ))
        print(f"  Added: {name}")
    db.flush()

# ============ TEAMS ============
# Men's Super League Teams
men_super_league_teams = [
    "Power Dynamos FC", "ZESCO United FC", "Nkana FC", "Red Arrows FC", 
    "Kabwe Warriors FC", "Nkwazi FC", "Green Buffaloes FC", "Mufulira Wanderers FC",
    "NAPSA Stars FC", "FC MUZA", "Nchanga Rangers FC", "Green Eagles FC",
    "Mutondo Stars FC", "ZANACO FC", "Atletico Lusaka FC", "Forest Rangers FC",
    "Lumwana Radiants FC", "Indeni FC"
]

# Men's National Division 1 Teams
men_division_one_teams = [
    "Konkola Blades FC", "Kansanshi Dynamos FC", "Mines United FC", "FC Leopards",
    "Trident FC", "River Plate FC", "Mpulungu Harbour FC", "Chambishi FC",
    "Kitwe United FC", "Chirundu United FC", "Aguila Stars FC", "Ndola United FC",
    "Jumulo FC", "Kafue Celtic FC", "Young Green Buffaloes FC", "Kafue Eagles FC",
    "Leopards Hill FC"
]

# Women's Super League Teams
women_super_league_teams = [
    "ZESCO Ndola Girls FC", "Green Buffaloes Women FC", "Indeni Roses FC",
    "Red Arrows Women FC", "Green Eagles Women FC", "Nchanga Rangers Queens FC",
    "Kamfinsa Police Blue Eagles FC", "ZISD FC", "ZANACO Ladies FC",
    "The Elite Ladies FC", "VASA FC", "Luyando Foundation", "Nkwazi Queens FC",
    "Trident Queens FC", "Police Doves Queens FC", "Choma Warriors Academy",
    "Play It Forward FC", "Nkana FC"
]

# Women's National League Southern
women_southern_teams = [
    "National Assembly Women FC", "Chipata Girls FC", "ZedPro FC",
    "AmeZam Tamanga Queens FC", "FC MUZA Queens FC", "Pataaki Girls FC",
    "Panzer Queens FC", "Nampundwe Queens FC", "Kabwe Warriors Ladies FC",
    "Bauleni United Sports Academy", "Young Elite Ladies FC", "Driven Queens FC",
    "Chainda Bombers Queens FC", "Locus Women FC", "Progress Sports Club",
    "Kafue Celtic Queens FC"
]

# Women's National League Northern
women_northern_teams = [
    "Konkola Blades FC", "Amazing Grace FC", "Chalube Angels FC",
    "Sporting Doves FC", "Kansanshi Dynamos Ladies FC", "Mufulira Wanderers FC",
    "Chitapankwa Girls FC", "Leopards Queens FC", "Nanyama Queens FC",
    "Nakonde Titans FC", "Nitindi Shining Stars FC", "Kabwe Celtic FC",
    "Maleu Queens FC", "Mulela Academy", "Queen's Sports Academy"
]

print("=" * 50)
print("Inserting/Updating Teams...")
print("=" * 50)

for team in men_super_league_teams:
    update_or_create_team(team, "male", LeagueLevel.SUPER_LEAGUE.value, 1)

for team in men_division_one_teams:
    update_or_create_team(team, "male", LeagueLevel.DIVISION_ONE.value, 2)

for team in women_super_league_teams:
    update_or_create_team(team, "female", LeagueLevel.SUPER_LEAGUE.value, 1)

for team in women_southern_teams:
    update_or_create_team(team, "female", LeagueLevel.NATIONAL_LEAGUE_SOUTH.value, 2)

for team in women_northern_teams:
    update_or_create_team(team, "female", LeagueLevel.NATIONAL_LEAGUE_NORTH.value, 2)

db.commit()
print("\n✅ Teams processed successfully!")

# ============ LEAGUES ============
print("\n" + "=" * 50)
print("Creating Leagues...")
print("=" * 50)

leagues_data = [
    {"name": "MTN Super League", "gender": Gender.MALE, "level": LeagueLevel.SUPER_LEAGUE, "tier": 1, "season": "2025-2026"},
    {"name": "National Division 1", "gender": Gender.MALE, "level": LeagueLevel.DIVISION_ONE, "tier": 2, "season": "2025-2026"},
    {"name": "Women's Super League", "gender": Gender.FEMALE, "level": LeagueLevel.SUPER_LEAGUE, "tier": 1, "season": "2025-2026"},
    {"name": "National Women's League - Southern", "gender": Gender.FEMALE, "level": LeagueLevel.NATIONAL_LEAGUE_SOUTH, "tier": 2, "season": "2025-2026"},
    {"name": "National Women's League - Northern", "gender": Gender.FEMALE, "level": LeagueLevel.NATIONAL_LEAGUE_NORTH, "tier": 2, "season": "2025-2026"},
]

for league_data in leagues_data:
    exists = db.query(League).filter(League.name == league_data["name"]).first()
    if not exists:
        db.add(League(**league_data))
        print(f"  Created: {league_data['name']}")
    else:
        print(f"  Already exists: {league_data['name']}")

db.commit()
print("\n✅ Leagues processed successfully!")

# ============ PROMOTION/RELEGATION RULES ============
print("\n" + "=" * 50)
print("Setting up Promotion/Relegation Rules...")
print("=" * 50)

men_super = db.query(League).filter(League.name == "MTN Super League").first()
men_div1 = db.query(League).filter(League.name == "National Division 1").first()
women_super = db.query(League).filter(League.name == "Women's Super League").first()
women_south = db.query(League).filter(League.name == "National Women's League - Southern").first()
women_north = db.query(League).filter(League.name == "National Women's League - Northern").first()

if men_super and men_div1:
    # Check if rules already exist
    existing1 = db.query(PromotionRelegationRule).filter(
        PromotionRelegationRule.from_league_id == men_div1.id,
        PromotionRelegationRule.to_league_id == men_super.id,
        PromotionRelegationRule.season == "2025-2026"
    ).first()
    if not existing1:
        db.add(PromotionRelegationRule(from_league_id=men_div1.id, to_league_id=men_super.id, positions_promoted=4, positions_relegated=0, season="2025-2026"))
        print("  Added: Men's promotion rule (Div1 → Super)")
    
    existing2 = db.query(PromotionRelegationRule).filter(
        PromotionRelegationRule.from_league_id == men_super.id,
        PromotionRelegationRule.to_league_id == men_div1.id,
        PromotionRelegationRule.season == "2025-2026"
    ).first()
    if not existing2:
        db.add(PromotionRelegationRule(from_league_id=men_super.id, to_league_id=men_div1.id, positions_promoted=0, positions_relegated=4, season="2025-2026"))
        print("  Added: Men's relegation rule (Super → Div1)")

if women_super and women_south and women_north:
    # Promotion from South to Super
    existing3 = db.query(PromotionRelegationRule).filter(
        PromotionRelegationRule.from_league_id == women_south.id,
        PromotionRelegationRule.to_league_id == women_super.id,
        PromotionRelegationRule.season == "2025-2026"
    ).first()
    if not existing3:
        db.add(PromotionRelegationRule(from_league_id=women_south.id, to_league_id=women_super.id, positions_promoted=2, positions_relegated=0, season="2025-2026"))
        print("  Added: Women's promotion rule (South → Super)")
    
    # Promotion from North to Super
    existing4 = db.query(PromotionRelegationRule).filter(
        PromotionRelegationRule.from_league_id == women_north.id,
        PromotionRelegationRule.to_league_id == women_super.id,
        PromotionRelegationRule.season == "2025-2026"
    ).first()
    if not existing4:
        db.add(PromotionRelegationRule(from_league_id=women_north.id, to_league_id=women_super.id, positions_promoted=2, positions_relegated=0, season="2025-2026"))
        print("  Added: Women's promotion rule (North → Super)")
    
    # Relegation from Super to South
    existing5 = db.query(PromotionRelegationRule).filter(
        PromotionRelegationRule.from_league_id == women_super.id,
        PromotionRelegationRule.to_league_id == women_south.id,
        PromotionRelegationRule.season == "2025-2026"
    ).first()
    if not existing5:
        db.add(PromotionRelegationRule(from_league_id=women_super.id, to_league_id=women_south.id, positions_promoted=0, positions_relegated=2, season="2025-2026"))
        print("  Added: Women's relegation rule (Super → South)")
    
    # Relegation from Super to North
    existing6 = db.query(PromotionRelegationRule).filter(
        PromotionRelegationRule.from_league_id == women_super.id,
        PromotionRelegationRule.to_league_id == women_north.id,
        PromotionRelegationRule.season == "2025-2026"
    ).first()
    if not existing6:
        db.add(PromotionRelegationRule(from_league_id=women_super.id, to_league_id=women_north.id, positions_promoted=0, positions_relegated=2, season="2025-2026"))
        print("  Added: Women's relegation rule (Super → North)")

db.commit()
print("\n✅ Promotion/Relegation rules processed successfully!")

# ============ NATIONAL TEAMS ============
print("\n" + "=" * 50)
print("Creating National Teams...")
print("=" * 50)

national_teams_data = [
    {"gender": Gender.MALE, "age_group": "senior", "name": "Chipolopolo"},
    {"gender": Gender.MALE, "age_group": "u23", "name": "U-23 National Team"},
    {"gender": Gender.MALE, "age_group": "u20", "name": "Junior Chipolopolo"},
    {"gender": Gender.MALE, "age_group": "u17", "name": "U-17 National Team"},
    {"gender": Gender.MALE, "age_group": "u15", "name": "U-15 National Team"},
    {"gender": Gender.FEMALE, "age_group": "senior", "name": "Copper Queens"},
    {"gender": Gender.FEMALE, "age_group": "u20", "name": "Young Copper Queens"},
    {"gender": Gender.FEMALE, "age_group": "u17", "name": "U-17 Women's National Team"},
    {"gender": Gender.FEMALE, "age_group": "u15", "name": "U-15 Women's National Team"},
]

for team_data in national_teams_data:
    exists = db.query(NationalTeam).filter(NationalTeam.name == team_data["name"]).first()
    if not exists:
        db.add(NationalTeam(**team_data))
        print(f"  Created: {team_data['name']}")
    else:
        print(f"  Already exists: {team_data['name']}")

db.commit()
print("\n✅ National teams processed successfully!")

# ============ CUP COMPETITIONS ============
print("\n" + "=" * 50)
print("Adding Cup Competitions...")
print("=" * 50)

cup_competitions = [
    {"name": "ABSA Cup", "gender": Gender.MALE, "competition_type": "cup", "season": "2025-2026"},
    {"name": "Charity Shield", "gender": Gender.MALE, "competition_type": "super_cup", "season": "2025-2026"},
    {"name": "COSAFA Women's Champions League", "gender": Gender.FEMALE, "competition_type": "continental", "season": "2025-2026"},
]

for cup in cup_competitions:
    exists = db.query(CupCompetition).filter(
        CupCompetition.name == cup["name"], 
        CupCompetition.season == cup["season"]
    ).first()
    if not exists:
        db.add(CupCompetition(**cup))
        print(f"  Created: {cup['name']}")
    else:
        print(f"  Already exists: {cup['name']}")

db.commit()
print("\n✅ Cup competitions processed successfully!")

# ============ CONTINENTAL QUALIFICATION RULES ============
print("\n" + "=" * 50)
print("Setting up Continental Qualification Rules...")
print("=" * 50)

print("Continental qualification rules have been configured.")
print("- CAF Champions League: Winner of Men's Super League")
print("- CAF Confederation Cup: Runner-up of Men's Super League")
print("- COSAFA Women's Champions League: Winner of Women's Super League")
print("\nNote: Qualification entries will be created by the admin endpoint `/api/cups/continental-qualifications/apply` at the end of the season.")

# ============ SAMPLE CUP MATCHES (optional) ============
print("\n" + "=" * 50)
print("Adding Sample Cup Seasons and Matches...")
print("=" * 50)

for cup in cup_competitions:
    cup_obj = db.query(CupCompetition).filter(
        CupCompetition.name == cup["name"], 
        CupCompetition.season == cup["season"]
    ).first()
    if cup_obj:
        # Check if season already exists
        season_exists = db.query(CupSeason).filter(
            CupSeason.cup_competition_id == cup_obj.id, 
            CupSeason.season == cup["season"]
        ).first()
        if not season_exists:
            cup_season = CupSeason(
                cup_competition_id=cup_obj.id,
                season=cup["season"],
                started_at=datetime.now().date()
            )
            db.add(cup_season)
            db.flush()
            print(f"  Created season for {cup['name']}")
            
            # For ABSA Cup, add sample matches (optional – can be added later)
            if cup["name"] == "ABSA Cup":
                teams = db.query(Team).filter(Team.gender == "male", Team.league_tier == 1).limit(16).all()
                if len(teams) >= 2:
                    for i in range(0, len(teams), 2):
                        if i+1 < len(teams):
                            match = CupMatch(
                                cup_season_id=cup_season.id,
                                round_name="Round of 16",
                                home_team_id=teams[i].id,
                                away_team_id=teams[i+1].id,
                                match_date=datetime.now() + timedelta(days=30 + i),
                                venue="National Stadium",
                                is_played=False
                            )
                            db.add(match)
                            print(f"    Added match: {teams[i].name} vs {teams[i+1].name}")
        else:
            print(f"  Season already exists for {cup['name']}")

db.commit()
print("\n✅ Sample cup matches processed (you can add more via admin panel).")

print("\n" + "=" * 50)
print("🎉 ALL DATA INSERTED/UPDATED SUCCESSFULLY! 🎉")
print("=" * 50)
db.close()