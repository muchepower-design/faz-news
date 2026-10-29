from sqlalchemy import Column, String, Integer, Date, ForeignKey, UUID, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models._base import Base, ToDictMixin
import uuid

class CupCompetition(Base, ToDictMixin):
    __tablename__ = "cup_competitions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    gender = Column(String)          # male/female
    season = Column(String)          # can be a default or derived
    description = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationship to seasons
    seasons = relationship("CupSeason", back_populates="competition")

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "gender": self.gender,
            "season": self.season,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }