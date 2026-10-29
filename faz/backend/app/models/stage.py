from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models._base import Base, ToDictMixin
import uuid

class Stage(Base, ToDictMixin):
    __tablename__ = "stages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    season_id = Column(UUID(as_uuid=True), ForeignKey("competition_seasons.id"), nullable=False)
    name = Column(String(100), nullable=False)
    stage_order = Column(Integer, default=0)
    is_knockout = Column(Boolean, default=False)
    is_group_stage = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    season = relationship("CompetitionSeason", back_populates="stages")
    groups = relationship("Group", back_populates="stage", cascade="all, delete-orphan")
    matches = relationship("CompetitionMatch", back_populates="stage")

    # Qualification rules - use back_populates to avoid conflict
    qualification_rules_from = relationship(
        "QualificationRule",
        foreign_keys="QualificationRule.from_stage_id",
        back_populates="from_stage"
    )
    qualification_rules_to = relationship(
        "QualificationRule",
        foreign_keys="QualificationRule.to_stage_id",
        back_populates="to_stage"
    )