# app/schemas/tournament.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID
from app.schemas._base import Gender, TournamentCategory

class TournamentBase(BaseModel):
    name: str
    category: TournamentCategory
    gender: Gender
    age_group: Optional[str] = None
    has_qualifiers: bool = False
    is_major_tournament: bool = True
    continent: Optional[str] = None

class TournamentCreate(TournamentBase):
    pass

class TournamentOut(TournamentBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class TournamentParticipationBase(BaseModel):
    tournament_name: str
    year: str
    round_reached: Optional[str] = None

class TournamentParticipationCreate(TournamentParticipationBase):
    national_team_id: UUID

class TournamentParticipationOut(TournamentParticipationBase):
    id: UUID
    national_team_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True