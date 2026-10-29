from sqlalchemy import Column, Integer, String, UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models._base import Base
import uuid

class LeagueTable(Base):
    __tablename__ = "league_tables"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id = Column(UUID(as_uuid=True), nullable=False)   # no ForeignKey
    team_type = Column(String, nullable=False)  # 'national' or 'club'
    played = Column(Integer, default=0)
    won = Column(Integer, default=0)
    drawn = Column(Integer, default=0)
    lost = Column(Integer, default=0)
    goals_for = Column(Integer, default=0)
    goals_against = Column(Integer, default=0)
    points = Column(Integer, default=0)
    season = Column(String)

    # Remove the relationship to Team
    # team = relationship("Team")  # delete this line