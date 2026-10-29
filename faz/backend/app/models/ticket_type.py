from sqlalchemy import Column, String, Integer, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models._base import Base, ToDictMixin
import uuid


class TicketType(Base, ToDictMixin):
    __tablename__ = "ticket_types"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_id = Column(
        UUID(as_uuid=True),
        ForeignKey("competition_matches.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(50), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    capacity = Column(Integer, nullable=False)
    tickets_sold = Column(Integer, default=0)

    match = relationship("CompetitionMatch", back_populates="ticket_types")
    order_items = relationship("OrderItem", back_populates="ticket_type")
    tickets = relationship("Ticket", back_populates="ticket_type")
    holds = relationship("SeatHold", back_populates="ticket_type")
    sections = relationship(
        "StadiumSection",
        back_populates="ticket_type",
        cascade="all, delete-orphan",
        order_by="StadiumSection.section_order",
    )

    def to_dict(self):
        return {
            'id': str(self.id),
            'match_id': str(self.match_id),
            'name': self.name,
            'price': float(self.price),
            'capacity': self.capacity,
            'tickets_sold': self.tickets_sold or 0,
            'available': (self.capacity or 0) - (self.tickets_sold or 0),
        }