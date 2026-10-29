from sqlalchemy import Column, String, Date, ForeignKey, UUID, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models._base import Base, ToDictMixin
import uuid

class CupSeason(Base, ToDictMixin):
    __tablename__ = "cup_seasons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cup_competition_id = Column(UUID(as_uuid=True), ForeignKey("cup_competitions.id"), nullable=False)
    season = Column(String, nullable=False)
    started_at = Column(Date)
    ended_at = Column(Date, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    competition = relationship("CupCompetition", back_populates="seasons")
    matches = relationship("CupMatch", back_populates="season")

    def to_dict(self):
        return {
            "id": str(self.id),
            "cup_competition_id": str(self.cup_competition_id),
            "season": self.season,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
        }