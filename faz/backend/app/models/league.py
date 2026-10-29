from sqlalchemy import Column, String, Integer, Date, ForeignKey, UUID, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models._base import Base, ToDictMixin
import uuid

class League(Base, ToDictMixin):
    __tablename__ = "leagues"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    season = Column(String, nullable=False)
    gender = Column(String)  # male/female
    # winner details – we no longer use a foreign key
    winner_id = Column(UUID(as_uuid=True), nullable=True)   # can be either national_team or club
    winner_type = Column(String, nullable=True)  # 'national' or 'club'
    started_at = Column(Date)
    ended_at = Column(Date, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Remove any relationship like 'winner' – we'll handle via lookup in code.
    # If you need to access the winner, write a helper method.

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "season": self.season,
            "gender": self.gender,
            "winner_id": str(self.winner_id) if self.winner_id else None,
            "winner_type": self.winner_type,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
        }