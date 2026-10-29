from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from typing import List
from datetime import datetime
from .. import database, models, schemas

router = APIRouter()

@router.get("/", response_model=List[schemas.LeagueTable])
async def get_league_table(
    season: str = Query(str(datetime.now().year), description="Season year"),
    db: Session = Depends(database.get_db)
):
    # Ensure we have team data loaded
    table = db.query(models.LeagueTable)\
        .filter(models.LeagueTable.season == season)\
        .options(joinedload(models.LeagueTable.team))\
        .order_by(
            models.LeagueTable.points.desc(),
            (models.LeagueTable.goals_for - models.LeagueTable.goals_against).desc(),
            models.LeagueTable.goals_for.desc()
        ).all()
    return table

@router.get("/seasons")
async def get_seasons(db: Session = Depends(database.get_db)):
    # Get distinct seasons from database, ordered descending
    seasons = db.query(models.LeagueTable.season).distinct().order_by(models.LeagueTable.season.desc()).all()
    seasons_list = [s[0] for s in seasons]
    current_year = str(datetime.now().year)
    # Always include current year at the top
    if current_year not in seasons_list:
        seasons_list.insert(0, current_year)
    return seasons_list