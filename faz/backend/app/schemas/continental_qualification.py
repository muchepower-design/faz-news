# app/schemas/continental_qualification.py
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from app.schemas._base import Gender

class ContinentalQualificationBase(BaseModel):
    season: str
    competition_name: str
    gender: Gender
    qualifying_team_id: UUID
    qualification_reason: str

class ContinentalQualificationCreate(ContinentalQualificationBase):
    pass

class ContinentalQualificationOut(ContinentalQualificationBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True