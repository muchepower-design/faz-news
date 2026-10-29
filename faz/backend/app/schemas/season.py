# app/schemas/season.py
from pydantic import BaseModel
from datetime import date
from uuid import UUID

class SeasonBase(BaseModel):
    name: str
    start_date: date
    end_date: date
    is_current: bool = False

class SeasonCreate(SeasonBase):
    pass

class SeasonOut(SeasonBase):
    id: UUID

    class Config:
        from_attributes = True