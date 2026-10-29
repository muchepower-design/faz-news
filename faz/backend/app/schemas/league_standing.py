# app/schemas/league_standing.py
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from app.schemas.league import League
from app.schemas.team import Team

class LeagueStandingBase(BaseModel):
    league_id: UUID
    team_id: UUID
    season: str
    played: int = 0
    won: int = 0
    drawn: int = 0
    lost: int = 0
    goals_for: int = 0
    goals_against: int = 0
    points: int = 0

class LeagueStanding(LeagueStandingBase):
    id: UUID
    league: Optional[League] = None
    team: Optional[Team] = None

    class Config:
        from_attributes = True