from sqlalchemy import Column, String, Integer, ForeignKey, UUID, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models._base import Base, ToDictMixin
import uuid

class LeagueStanding(Base, ToDictMixin):
    __tablename__ = "league_standings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    league_id = Column(UUID(as_uuid=True), ForeignKey("leagues.id"), nullable=False)
    season = Column(String, nullable=False)
    # Instead of a foreign key to teams, use a plain UUID and a type
    team_id = Column(UUID(as_uuid=True), nullable=False)   # no FK
    team_type = Column(String, nullable=False)  # 'national' or 'club'
    played = Column(Integer, default=0)
    won = Column(Integer, default=0)
    drawn = Column(Integer, default=0)
    lost = Column(Integer, default=0)
    goals_for = Column(Integer, default=0)
    goals_against = Column(Integer, default=0)
    points = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationship to League (no team relationship)
    league = relationship("League", backref="standings")

    def to_dict(self):
        return {
            "id": str(self.id),
            "league_id": str(self.league_id),
            "season": self.season,
            "team_id": str(self.team_id),
            "team_type": self.team_type,
            "played": self.played,
            "won": self.won,
            "drawn": self.drawn,
            "lost": self.lost,
            "goals_for": self.goals_for,
            "goals_against": self.goals_against,
            "points": self.points,
        }