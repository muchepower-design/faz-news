from sqlalchemy import Column, String, Integer, Date, ForeignKey, DateTime, UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models._base import Base, ToDictMixin
import uuid

class Player(Base, ToDictMixin):
    __tablename__ = "players"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    position = Column(String)
    jersey_number = Column(Integer)
    date_of_birth = Column(Date)
    nationality = Column(String)
    # Instead of a single team_id, use two separate nullable FKs
    national_team_id = Column(UUID(as_uuid=True), ForeignKey("national_teams.id"), nullable=True)
    club_id = Column(UUID(as_uuid=True), ForeignKey("clubs.id"), nullable=True)
    goals = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    appearances = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationships
    national_team = relationship("NationalTeam", foreign_keys=[national_team_id], backref="players")
    club = relationship("Club", foreign_keys=[club_id], backref="players")

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "position": self.position,
            "jersey_number": self.jersey_number,
            "date_of_birth": self.date_of_birth.isoformat() if self.date_of_birth else None,
            "nationality": self.nationality,
            "national_team_id": str(self.national_team_id) if self.national_team_id else None,
            "club_id": str(self.club_id) if self.club_id else None,
            "goals": self.goals,
            "assists": self.assists,
            "appearances": self.appearances,
        }