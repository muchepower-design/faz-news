from sqlalchemy import Column, String, Boolean, DateTime, UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models._base import Base, ToDictMixin
import uuid

class Competition(Base, ToDictMixin):
    __tablename__ = "competitions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    competition_type = Column(String, nullable=False)   # e.g., 'league', 'cup'
    gender = Column(String)
    age_group = Column(String, nullable=True)
    scope = Column(String)  # 'national', 'international'
    description = Column(String, nullable=True)
    logo_url = Column(String, nullable=True)
    participant_type = Column(String, nullable=True)  # 'countries' or 'clubs'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    season = Column(String(50))                            # e.g., "2025-2026"
    is_archived = Column(Boolean, default=False)
    level = Column(String(50))                             # e.g., 'tier1', 'tier2'
    icon = Column(String(50))
    
    seasons = relationship("CompetitionSeason", back_populates="competition")

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "competition_type": self.competition_type,
            "gender": self.gender,
            "age_group": self.age_group,
            "scope": self.scope,
            "description": self.description,
            "logo_url": self.logo_url,
            "participant_type": self.participant_type,
            "is_active": self.is_active,
        }

    