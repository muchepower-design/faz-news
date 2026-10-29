from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models._base import Base, ToDictMixin
import uuid

class Standing(Base, ToDictMixin):
    __tablename__ = "standings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id"), nullable=True)
    season_id = Column(UUID(as_uuid=True), ForeignKey("competition_seasons.id"), nullable=True)
    team_id = Column(UUID(as_uuid=True), nullable=False)   # no FK
    # Optional: if you want to store the team type to help lookups
    # team_type = Column(String, nullable=False)           # you can add this if needed
    played = Column(Integer, default=0)
    won = Column(Integer, default=0)
    drawn = Column(Integer, default=0)
    lost = Column(Integer, default=0)
    goals_for = Column(Integer, default=0)
    goals_against = Column(Integer, default=0)
    points = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    group = relationship("Group", back_populates="standings")
    season = relationship("CompetitionSeason", back_populates="standings")
    # Remove team relationship entirely

    __table_args__ = (
        UniqueConstraint('group_id', 'team_id', name='uq_group_team'),
        UniqueConstraint('season_id', 'team_id', name='uq_season_team'),
    )

    def to_dict(self):
        return {
            "id": str(self.id),
            "group_id": str(self.group_id) if self.group_id else None,
            "season_id": str(self.season_id) if self.season_id else None,
            "team_id": str(self.team_id),
            "played": self.played,
            "won": self.won,
            "drawn": self.drawn,
            "lost": self.lost,
            "goals_for": self.goals_for,
            "goals_against": self.goals_against,
            "points": self.points,
        }