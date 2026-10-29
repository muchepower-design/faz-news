from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models._base import Base, ToDictMixin
import uuid


class StadiumSection(Base, ToDictMixin):
    __tablename__ = 'stadium_sections'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_id = Column(
        UUID(as_uuid=True),
        ForeignKey('competition_matches.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    ticket_type_id = Column(
        UUID(as_uuid=True),
        ForeignKey('ticket_types.id', ondelete='CASCADE'),
        nullable=True,
        index=True,
    )
    name = Column(String(80), nullable=False)
    deck = Column(String(50), nullable=True)
    rows = Column(Integer, nullable=False, default=0)
    seats_per_row = Column(Integer, nullable=False, default=0)
    section_order = Column(Integer, nullable=False, default=0)
    side = Column(String(20), nullable=True)   # 'north' | 'east' | 'south' | 'west' | None
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    match = relationship('CompetitionMatch', backref='stadium_sections')
    ticket_type = relationship('TicketType', back_populates='sections')

    @property
    def total_seats(self):
        return max(0, (self.rows or 0) * (self.seats_per_row or 0))

    def to_dict(self):
        return {
            'id': str(self.id),
            'match_id': str(self.match_id),
            'ticket_type_id': str(self.ticket_type_id) if self.ticket_type_id else None,
            'name': self.name,
            'deck': self.deck,
            'rows': self.rows,
            'seats_per_row': self.seats_per_row,
            'total_seats': self.total_seats,
            'section_order': self.section_order,
            'side': self.side,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }