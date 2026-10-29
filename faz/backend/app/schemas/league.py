# app/schemas/league.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID
from app.schemas._base import Gender, LeagueLevel

class LeagueBase(BaseModel):
    name: str
    gender: Gender
    level: LeagueLevel
    tier: int
    season: str

class LeagueCreate(LeagueBase):
    pass

class League(LeagueBase):
    id: UUID
    current_champion_id: Optional[UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True