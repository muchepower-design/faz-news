from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models._base import Base
import uuid

class PromotionRelegationRule(Base):
    __tablename__ = "promotion_relegation_rules"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    from_league_id = Column(UUID(as_uuid=True), ForeignKey("leagues.id"))
    to_league_id = Column(UUID(as_uuid=True), ForeignKey("leagues.id"))
    positions_promoted = Column(Integer, default=2)
    positions_relegated = Column(Integer, default=2)
    season = Column(String)

    from_league = relationship("League", foreign_keys=[from_league_id])
    to_league = relationship("League", foreign_keys=[to_league_id])