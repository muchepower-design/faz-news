from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models._base import Base
import uuid

class PromotionRelegation(Base):
    __tablename__ = "promotion_relegations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id = Column(UUID(as_uuid=True), nullable=False)   # no FK
    team_type = Column(String, nullable=False)             # 'national' or 'club'
    from_league_id = Column(UUID(as_uuid=True), ForeignKey("leagues.id"))
    to_league_id = Column(UUID(as_uuid=True), ForeignKey("leagues.id"))
    season = Column(String)
    action = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Remove team relationship; we'll handle lookups via helper
    from_league = relationship("League", foreign_keys=[from_league_id])
    to_league = relationship("League", foreign_keys=[to_league_id])

    def to_dict(self):
        return {
            "id": str(self.id),
            "team_id": str(self.team_id),
            "team_type": self.team_type,
            "from_league_id": str(self.from_league_id) if self.from_league_id else None,
            "to_league_id": str(self.to_league_id) if self.to_league_id else None,
            "season": self.season,
            "action": self.action,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }