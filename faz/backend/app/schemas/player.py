# app/schemas/player.py
from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional
from uuid import UUID

class PlayerBase(BaseModel):
    name: str
    position: str
    jersey_number: int
    date_of_birth: date
    nationality: str
    photo: Optional[str] = None
    team_id: UUID

class PlayerCreate(PlayerBase):
    pass

class Player(PlayerBase):
    id: UUID
    goals: int
    assists: int
    appearances: int

    class Config:
        from_attributes = True