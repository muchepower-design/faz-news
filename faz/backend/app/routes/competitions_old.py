# backend/app/routes/competitions.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from uuid import UUID
from .. import database, models, schemas, auth

router = APIRouter()

@router.get("/")
async def get_competitions(
    gender: Optional[str] = None,
    season: Optional[str] = None,
    competition_type: Optional[str] = None,
    include_archived: bool = False,
    db: Session = Depends(database.get_db)
):
    """Get all competitions with optional filters"""
    query = db.query(models.Competition).options(
        joinedload(models.Competition.current_champion),
        joinedload(models.Competition.seasons)
    )
    
    if gender:
        query = query.filter(models.Competition.gender == gender)
    if competition_type:
        query = query.filter(models.Competition.competition_type == competition_type)
    if season:
        query = query.filter(models.Competition.season == season)
    if not include_archived:
        query = query.filter(models.Competition.is_archived == False)
    
    return query.all()

@router.get("/seasons")
async def get_available_seasons(db: Session = Depends(database.get_db)):
    """Get all unique seasons from competitions"""
    seasons = db.query(models.Competition.season).distinct().order_by(models.Competition.season.desc()).all()
    return [s[0] for s in seasons]

@router.get("/{competition_id}")
async def get_competition_detail(
    competition_id: str,
    season: Optional[str] = None,
    db: Session = Depends(database.get_db)
):
    """Get detailed competition info including standings for a specific season"""
    try:
        comp_uuid = UUID(competition_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid competition ID format")
    
    competition = db.query(models.Competition).filter(
        models.Competition.id == comp_uuid
    ).first()
    
    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")
    
    # Get standings for the specified season
    standings = []
    if season:
        # Find the league associated with this competition
        league = db.query(models.League).filter(
            models.League.name == competition.name,
            models.League.season == season
        ).first()
        
        if league:
            standings = db.query(models.LeagueStanding).options(
                joinedload(models.LeagueStanding.team)
            ).filter(
                models.LeagueStanding.league_id == league.id,
                models.LeagueStanding.season == season
            ).order_by(
                models.LeagueStanding.points.desc(),
                (models.LeagueStanding.goals_for - models.LeagueStanding.goals_against).desc(),
                models.LeagueStanding.goals_for.desc()
            ).all()
    
    # Get historical champions
    seasons_history = db.query(models.CompetitionSeason).filter(
        models.CompetitionSeason.competition_id == comp_uuid
    ).order_by(models.CompetitionSeason.season.desc()).all()
    
    return {
        "competition": competition,
        "standings": standings,
        "season": season,
        "history": seasons_history
    }

@router.get("/{competition_id}/history")
async def get_competition_history(
    competition_id: str,
    limit: int = 10,
    db: Session = Depends(database.get_db)
):
    """Get historical champions and runners-up for a competition"""
    try:
        comp_uuid = UUID(competition_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid competition ID format")
    
    history = db.query(models.CompetitionSeason).options(
        joinedload(models.CompetitionSeason.champion),
        joinedload(models.CompetitionSeason.runner_up)
    ).filter(
        models.CompetitionSeason.competition_id == comp_uuid
    ).order_by(
        models.CompetitionSeason.season.desc()
    ).limit(limit).all()
    
    return history

@router.post("/", response_model=schemas.CompetitionOut)
async def create_competition(
    competition: schemas.CompetitionCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    """Create a new competition (admin only)"""
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin only")
    
    db_competition = models.Competition(**competition.dict())
    db.add(db_competition)
    db.commit()
    db.refresh(db_competition)
    return db_competition