from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models._base import Base
import uuid

class TournamentParticipation(Base):
    __tablename__ = "tournament_participations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    national_team_id = Column(UUID(as_uuid=True), ForeignKey("national_teams.id"))
    tournament_name = Column(String)
    year = Column(String)
    round_reached = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    national_team = relationship("NationalTeam")