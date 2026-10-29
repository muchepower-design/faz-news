from sqlalchemy import Column, String, Date, Boolean, DateTime, UUID, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models._base import Base, ToDictMixin
import uuid

class CompetitionSeason(Base, ToDictMixin):
    __tablename__ = "competition_seasons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competition_id = Column(UUID(as_uuid=True), ForeignKey("competitions.id"), nullable=False)
    season = Column(String, nullable=False)          # e.g., "2024"
    started_at = Column(Date)
    ended_at = Column(Date, nullable=True)
    is_archived = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    # Remove winner/runner_up FKs to teams. Use plain UUIDs + type if needed
    # winner_id, runner_up_id – remove them entirely or keep as generic UUID + type

    competition = relationship("Competition", back_populates="seasons")
    stages = relationship("Stage", back_populates="season")
    matches = relationship("CompetitionMatch", back_populates="season")
    standings = relationship("Standing", back_populates="season")

    def to_dict(self):
        return {
            "id": str(self.id),
            "competition_id": str(self.competition_id),
            "season": self.season,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "is_archived": self.is_archived,
        }