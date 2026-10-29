# app/schemas/national_team.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID
from app.schemas._base import Gender, MatchType

class NationalTeamBase(BaseModel):
    gender: Gender
    age_group: str
    name: str
    coach: Optional[str] = None

class NationalTeamCreate(NationalTeamBase):
    captain_id: Optional[UUID] = None

class NationalTeamOut(NationalTeamBase):
    id: UUID
    captain_id: Optional[UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True

class NationalTeamFixtureCreate(BaseModel):
    opponent: str
    match_date: datetime
    venue: str
    competition: str
    match_type: MatchType
    home_away: str
    is_qualifier: bool = False

class NationalTeamFixtureOut(NationalTeamFixtureCreate):
    id: UUID
    national_team_id: UUID
    goals_for: int
    goals_against: int
    result: Optional[str]
    is_played: bool
    created_at: datetime

    class Config:
        from_attributes = True