# app/models/group_national_team.py
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.models._base import Base

class GroupNationalTeam(Base):
    __tablename__ = "group_national_teams"
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id"), primary_key=True)
    national_team_id = Column(UUID(as_uuid=True), ForeignKey("national_teams.id"), primary_key=True)