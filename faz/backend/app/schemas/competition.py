# app/schemas/competition.py
from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional
from uuid import UUID
from app.schemas.team import Team

class CompetitionBase(BaseModel):
    name: str
    gender: str
    competition_type: str
    level: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None
    season: str
    is_archived: bool = False
    started_at: Optional[date] = None
    ended_at: Optional[date] = None

class CompetitionCreate(CompetitionBase):
    current_champion_id: Optional[UUID] = None

class CompetitionOut(CompetitionBase):
    id: UUID
    current_champion_id: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CompetitionSeasonBase(BaseModel):
    season: str
    started_at: Optional[date] = None
    ended_at: Optional[date] = None
    is_archived: bool = False

class CompetitionSeasonCreate(CompetitionSeasonBase):
    competition_id: UUID
    champion_id: Optional[UUID] = None
    runner_up_id: Optional[UUID] = None

class CompetitionSeasonOut(CompetitionSeasonBase):
    id: UUID
    competition_id: UUID
    champion_id: Optional[UUID] = None
    runner_up_id: Optional[UUID] = None
    champion: Optional[Team] = None
    runner_up: Optional[Team] = None

    class Config:
        from_attributes = True