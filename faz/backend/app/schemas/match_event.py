# app/schemas/match_event.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID
from app.schemas._base import MatchEventType

class MatchEventBase(BaseModel):
    event_type: MatchEventType
    player_id: UUID
    related_player_id: Optional[UUID] = None
    minute: int
    minute_added: int = 0
    description: Optional[str] = None

class MatchEventCreate(MatchEventBase):
    match_id: UUID

class MatchEventOut(MatchEventBase):
    id: UUID
    match_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True