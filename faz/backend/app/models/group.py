# app/models/group.py
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models._base import Base, ToDictMixin
import uuid

class Group(Base, ToDictMixin):
    __tablename__ = "groups"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    stage_id = Column(UUID(as_uuid=True), ForeignKey("stages.id"), nullable=False)
    name = Column(String(50), nullable=False)
    group_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    stage = relationship("Stage", back_populates="groups")
    standings = relationship("Standing", back_populates="group", cascade="all, delete-orphan")
    matches = relationship("CompetitionMatch", back_populates="group")

    # New relationships
    national_teams = relationship("NationalTeam", secondary="group_national_teams", back_populates="groups")
    clubs = relationship("Club", secondary="group_clubs", back_populates="groups")