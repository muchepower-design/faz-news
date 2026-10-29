from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models._base import Base
import uuid

class NationalTeamFixture(Base):
    __tablename__ = "national_team_fixtures"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    national_team_id = Column(UUID(as_uuid=True), ForeignKey("national_teams.id"))
    opponent = Column(String)
    match_date = Column(DateTime(timezone=True))
    venue = Column(String)
    competition = Column(String)
    match_type = Column(String)
    home_away = Column(String)
    goals_for = Column(Integer, default=0)
    goals_against = Column(Integer, default=0)
    result = Column(String, nullable=True)
    is_played = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    national_team = relationship("NationalTeam")