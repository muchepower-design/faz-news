# app/models/group_club.py
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.models._base import Base

class GroupClub(Base):
    __tablename__ = "group_clubs"
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id"), primary_key=True)
    club_id = Column(UUID(as_uuid=True), ForeignKey("clubs.id"), primary_key=True)