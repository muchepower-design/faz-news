from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models._base import Base, ToDictMixin
import uuid

class QualificationRule(Base, ToDictMixin):
    __tablename__ = "qualification_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    from_stage_id = Column(UUID(as_uuid=True), ForeignKey("stages.id"), nullable=False)
    to_stage_id = Column(UUID(as_uuid=True), ForeignKey("stages.id"), nullable=False)
    rank_condition = Column(String(50), nullable=False)
    number_of_teams = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    from_stage = relationship("Stage", foreign_keys=[from_stage_id], back_populates="qualification_rules_from")
    to_stage = relationship("Stage", foreign_keys=[to_stage_id], back_populates="qualification_rules_to")