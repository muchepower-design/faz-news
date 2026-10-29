# app/models/order_item.py
from sqlalchemy import Column, Integer, Numeric, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models._base import Base, ToDictMixin
import uuid


class OrderItem(Base, ToDictMixin):
    __tablename__ = "order_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)

    # Seat assignment carried through checkout → ticket generation
    section = Column(String(80), nullable=True)
    row = Column(String(20), nullable=True)
    seat = Column(String(20), nullable=True)

    ticket_type_id = Column(UUID(as_uuid=True), ForeignKey("ticket_types.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)

    order = relationship("Order", back_populates="items")
    ticket_type = relationship("TicketType", back_populates="order_items")
    tickets = relationship("Ticket", back_populates="order_item", lazy="dynamic")

    def to_dict(self):
        match_name = None
        match_id = None
        if self.ticket_type and self.ticket_type.match:
            match = self.ticket_type.match
            match_name = f"{match.home_team} vs {match.away_team}"
            match_id = str(match.id) if match.id else None

        return {
            'id': str(self.id),
            'ticket_type': self.ticket_type.name if self.ticket_type else None,
            'ticket_type_id': str(self.ticket_type_id) if self.ticket_type_id else None,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price) if self.unit_price is not None else 0.0,
            'match_id': match_id,
            'match_name': match_name,
            'tickets': [t.to_dict() for t in self.tickets],
            'section': self.section,
            'row': self.row,
            'seat': self.seat,
        }