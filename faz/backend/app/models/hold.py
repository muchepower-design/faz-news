from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models._base import Base
import uuid
from datetime import datetime, timedelta


class SeatHold(Base):
    __tablename__ = "seat_holds"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hold_token = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    match_id = Column(
        UUID(as_uuid=True),
        ForeignKey("competition_matches.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    section = Column(String(80), nullable=True)
    row = Column(String(20), nullable=True)
    seat = Column(String(20), nullable=True)
    ticket_type_id = Column(UUID(as_uuid=True), ForeignKey("ticket_types.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=False)

    match = relationship("CompetitionMatch", back_populates="seat_holds")
    ticket_type = relationship("TicketType", back_populates="holds")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.expires_at:
            self.expires_at = datetime.utcnow() + timedelta(minutes=10)

    def is_expired(self):
        return datetime.utcnow() > self.expires_at