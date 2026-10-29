# app/schemas/match.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from app.schemas.match_event import MatchEventOut

class MatchBase(BaseModel):
    home_team: str
    away_team: str
    home_score: int = 0
    away_score: int = 0
    match_date: datetime
    venue: str
    competition: str
    status: str = "upcoming"
    is_home_match: bool = True

class MatchCreate(MatchBase):
    pass

class Match(MatchBase):
    id: UUID
    referee_id: Optional[UUID] = None

    class Config:
        from_attributes = True

class MatchDetail(Match):
    events: List[MatchEventOut] = []