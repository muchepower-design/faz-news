from sqlalchemy import Column, Text, JSON, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models._base import Base
import uuid

class MatchReport(Base):
    __tablename__ = "match_reports"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_id = Column(UUID(as_uuid=True), ForeignKey("matches.id"), unique=True)
    referee_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    content = Column(Text)
    yellow_cards = Column(JSON, default=[])
    red_cards = Column(JSON, default=[])
    incidents = Column(JSON, default=[])
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())

    match = relationship("Match", back_populates="report")
    referee = relationship("User", foreign_keys=[referee_id])