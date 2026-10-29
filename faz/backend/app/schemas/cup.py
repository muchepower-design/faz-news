# app/schemas/cup.py
from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional
from uuid import UUID
from app.schemas._base import Gender

class CupCompetitionBase(BaseModel):
    name: str
    gender: Gender
    competition_type: str
    season: str

class CupCompetitionCreate(CupCompetitionBase):
    pass

class CupCompetitionOut(CupCompetitionBase):
    id: UUID
    current_champion_id: Optional[UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True

class CupSeasonBase(BaseModel):
    season: str
    started_at: date
    ended_at: Optional[date] = None

class CupSeasonCreate(CupSeasonBase):
    cup_competition_id: UUID

class CupSeasonOut(CupSeasonBase):
    id: UUID
    winner_id: Optional[UUID]
    runner_up_id: Optional[UUID]
    cup_competition_id: UUID

    class Config:
        from_attributes = True

class CupMatchCreate(BaseModel):
    round_name: str
    home_team_id: UUID
    away_team_id: UUID
    match_date: datetime
    venue: str

class CupMatchOut(CupMatchCreate):
    id: UUID
    home_score: int
    away_score: int
    is_played: bool
    winner_id: Optional[UUID]
    cup_season_id: UUID

    class Config:
        from_attributes = True