# backend/insert_tournament_data.py
from app.database import SessionLocal
from app.models import Tournament, TournamentCategory, Gender, NationalTeam, TournamentParticipation
import sys

db = SessionLocal()

# ============ MEN'S TOURNAMENTS ============
men_tournaments = [
    {"name": "International Friendly", "category": TournamentCategory.FRIENDLY, "gender": Gender.MALE, "age_group": "senior", "has_qualifiers": False, "is_major_tournament": False},
    {"name": "COSAFA Cup", "category": TournamentCategory.COSAFA, "gender": Gender.MALE, "age_group": "senior", "has_qualifiers": False, "is_major_tournament": True, "continent": "CAF"},
    {"name": "AFCON", "category": TournamentCategory.AFCON, "gender": Gender.MALE, "age_group": "senior", "has_qualifiers": True, "is_major_tournament": True, "continent": "CAF"},
    {"name": "Four Nations Tournament", "category": TournamentCategory.FOUR_NATIONS, "gender": Gender.MALE, "age_group": "senior", "has_qualifiers": False, "is_major_tournament": False},
    {"name": "CHAN", "category": TournamentCategory.CHAN, "gender": Gender.MALE, "age_group": "u23", "has_qualifiers": True, "is_major_tournament": True, "continent": "CAF"},
    {"name": "FIFA World Cup", "category": TournamentCategory.FIFA_WORLD_CUP, "gender": Gender.MALE, "age_group": "senior", "has_qualifiers": True, "is_major_tournament": True, "continent": "FIFA"},
    {"name": "Olympics", "category": TournamentCategory.OLYMPICS, "gender": Gender.MALE, "age_group": "senior", "has_qualifiers": True, "is_major_tournament": True, "continent": "Olympic"},
]

# ============ WOMEN'S TOURNAMENTS ============
women_tournaments = [
    {"name": "International Friendly", "category": TournamentCategory.FRIENDLY, "gender": Gender.FEMALE, "age_group": "senior", "has_qualifiers": False, "is_major_tournament": False},
    {"name": "COSAFA Women's Cup", "category": TournamentCategory.COSAFA, "gender": Gender.FEMALE, "age_group": "senior", "has_qualifiers": False, "is_major_tournament": True, "continent": "CAF"},
    {"name": "WAFCON", "category": TournamentCategory.WAFCON, "gender": Gender.FEMALE, "age_group": "senior", "has_qualifiers": True, "is_major_tournament": True, "continent": "CAF"},
    {"name": "Four Nations Tournament", "category": TournamentCategory.FOUR_NATIONS, "gender": Gender.FEMALE, "age_group": "senior", "has_qualifiers": False, "is_major_tournament": False},
    {"name": "FIFA Women's World Cup", "category": TournamentCategory.FIFA_WORLD_CUP, "gender": Gender.FEMALE, "age_group": "senior", "has_qualifiers": True, "is_major_tournament": True, "continent": "FIFA"},
    {"name": "Olympics", "category": TournamentCategory.OLYMPICS, "gender": Gender.FEMALE, "age_group": "senior", "has_qualifiers": True, "is_major_tournament": True, "continent": "Olympic"},
]

print("=" * 50)
print("Inserting Tournaments (skipping existing)...")
print("=" * 50)

# Insert Men's Tournaments (commit after each)
for tour in men_tournaments:
    exists = db.query(Tournament).filter(Tournament.name == tour["name"]).first()
    if not exists:
        db.add(Tournament(**tour))
        db.commit()  # Commit immediately to avoid duplicate issues
        print(f"  Added: {tour['name']} (Men)")
    else:
        print(f"  Skipped (already exists): {tour['name']} (Men)")

# Insert Women's Tournaments (commit after each)
for tour in women_tournaments:
    exists = db.query(Tournament).filter(Tournament.name == tour["name"]).first()
    if not exists:
        db.add(Tournament(**tour))
        db.commit()  # Commit immediately
        print(f"  Added: {tour['name']} (Women)")
    else:
        print(f"  Skipped (already exists): {tour['name']} (Women)")

print("\n✅ Tournaments processed successfully!")

# ============ ADD SAMPLE TOURNAMENT PARTICIPATIONS (skip if exist) ============
print("\n" + "=" * 50)
print("Adding Sample Tournament Participations...")
print("=" * 50)

sample_participations = [
    # Chipolopolo (Men's Senior)
    {"national_team_name": "Chipolopolo", "tournament_name": "AFCON", "year": "2023", "round_reached": "Group Stage"},
    {"national_team_name": "Chipolopolo", "tournament_name": "COSAFA Cup", "year": "2024", "round_reached": "Winner"},
    {"national_team_name": "Chipolopolo", "tournament_name": "FIFA World Cup", "year": "2022", "round_reached": "Did Not Qualify"},
    {"national_team_name": "Chipolopolo", "tournament_name": "Four Nations Tournament", "year": "2024", "round_reached": "Runner-up"},
    {"national_team_name": "Chipolopolo", "tournament_name": "CHAN", "year": "2024", "round_reached": "Group Stage"},
    
    # Copper Queens (Women's Senior)
    {"national_team_name": "Copper Queens", "tournament_name": "WAFCON", "year": "2023", "round_reached": "Quarterfinal"},
    {"national_team_name": "Copper Queens", "tournament_name": "COSAFA Women's Cup", "year": "2024", "round_reached": "Winner"},
    {"national_team_name": "Copper Queens", "tournament_name": "FIFA Women's World Cup", "year": "2023", "round_reached": "Group Stage"},
    {"national_team_name": "Copper Queens", "tournament_name": "Olympics", "year": "2024", "round_reached": "Quarterfinal"},
    {"national_team_name": "Copper Queens", "tournament_name": "Four Nations Tournament", "year": "2024", "round_reached": "Winner"},
]

participation_count = 0
for part in sample_participations:
    team = db.query(NationalTeam).filter(NationalTeam.name == part["national_team_name"]).first()
    tournament = db.query(Tournament).filter(Tournament.name == part["tournament_name"]).first()
    if team and tournament:
        exists = db.query(TournamentParticipation).filter(
            TournamentParticipation.national_team_id == team.id,
            TournamentParticipation.tournament_name == part["tournament_name"],
            TournamentParticipation.year == part["year"]
        ).first()
        if not exists:
            db.add(TournamentParticipation(
                national_team_id=team.id,
                tournament_name=part["tournament_name"],
                year=part["year"],
                round_reached=part["round_reached"]
            ))
            db.commit()  # Commit after each participation
            participation_count += 1
            print(f"  Added: {team.name} - {part['tournament_name']} ({part['year']})")
        else:
            print(f"  Skipped (exists): {team.name} - {part['tournament_name']} ({part['year']})")
    else:
        if not team:
            print(f"  Warning: Team '{part['national_team_name']}' not found")
        if not tournament:
            print(f"  Warning: Tournament '{part['tournament_name']}' not found")

print(f"\n✅ Added {participation_count} new tournament participations (skipped existing)")

print("\n" + "=" * 50)
print("🎉 ALL TOURNAMENT DATA INSERTED SUCCESSFULLY! 🎉")
print("=" * 50)
db.close()