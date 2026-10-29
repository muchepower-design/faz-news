from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models._base import Base, MatchEventType
import uuid

class MatchEvent(Base):
    __tablename__ = "match_events"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_id = Column(UUID(as_uuid=True), ForeignKey("matches.id"))
    event_type = Column(String)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id"))
    related_player_id = Column(UUID(as_uuid=True), ForeignKey("players.id"), nullable=True)
    minute = Column(Integer)
    minute_added = Column(Integer, default=0)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    match = relationship("Match", back_populates="events")
    player = relationship("Player", foreign_keys=[player_id])
    related_player = relationship("Player", foreign_keys=[related_player_id])