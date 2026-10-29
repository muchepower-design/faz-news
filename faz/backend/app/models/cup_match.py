from sqlalchemy import Column, String, Integer, DateTime, Boolean, UUID, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models._base import Base, ToDictMixin
import uuid

class CupMatch(Base, ToDictMixin):
    __tablename__ = "cup_matches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cup_season_id = Column(UUID(as_uuid=True), ForeignKey("cup_seasons.id"), nullable=False)  # keep FK
    round_name = Column(String)
    home_team_id = Column(UUID(as_uuid=True), nullable=False)   # no FK to teams
    away_team_id = Column(UUID(as_uuid=True), nullable=False)   # no FK to teams
    team_type = Column(String, nullable=False, default="club")  # 'national' or 'club'
    home_score = Column(Integer, default=0)
    away_score = Column(Integer, default=0)
    match_date = Column(DateTime, nullable=False)
    venue = Column(String)
    is_played = Column(Boolean, default=False)
    winner_id = Column(UUID(as_uuid=True), nullable=True)       # no FK to teams
    created_at = Column(DateTime, server_default=func.now())

    season = relationship("CupSeason", back_populates="matches")

    def to_dict(self):
        return {
            "id": str(self.id),
            "cup_season_id": str(self.cup_season_id),
            "round_name": self.round_name,
            "home_team_id": str(self.home_team_id),
            "away_team_id": str(self.away_team_id),
            "team_type": self.team_type,
            "home_score": self.home_score,
            "away_score": self.away_score,
            "match_date": self.match_date.isoformat() if self.match_date else None,
            "venue": self.venue,
            "is_played": self.is_played,
            "winner_id": str(self.winner_id) if self.winner_id else None,
        }