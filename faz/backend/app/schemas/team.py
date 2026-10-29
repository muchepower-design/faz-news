# app/schemas/team.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID

class TeamBase(BaseModel):
    name: str
    short_name: str
    logo: Optional[str] = None
    founded: int
    stadium: str
    coach: str
    description: Optional[str] = None

class TeamCreate(TeamBase):
    gender: str = "male"
    team_type: str = "club"
    current_league_level: Optional[str] = None
    league_tier: int = 3

class Team(TeamBase):
    id: UUID
    gender: str
    team_type: str
    current_league_level: Optional[str]
    league_tier: int
    created_at: datetime

    class Config:
        from_attributes = True