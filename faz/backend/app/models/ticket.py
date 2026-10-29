from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models._base import Base, ToDictMixin
import uuid
import qrcode
import io
import base64


class Ticket(Base, ToDictMixin):
    __tablename__ = "tickets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_number = Column(String(36), unique=True, nullable=False, index=True)
    order_item_id = Column(UUID(as_uuid=True), ForeignKey("order_items.id"), nullable=False)
    match_id = Column(
        UUID(as_uuid=True),
        ForeignKey("competition_matches.id"),
        nullable=False,
        index=True,
    )
    section = Column(String(80), nullable=True)
    row = Column(String(20), nullable=True)
    seat = Column(String(20), nullable=True)
    ticket_type_id = Column(UUID(as_uuid=True), ForeignKey("ticket_types.id"), nullable=False)
    qr_code_data = Column(Text)
    is_used = Column(Boolean, default=False)
    used_at = Column(DateTime)
    verified_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=func.now())

    match = relationship("CompetitionMatch", back_populates="tickets")
    ticket_type = relationship("TicketType", back_populates="tickets")
    order_item = relationship("OrderItem", back_populates="tickets")

    def generate_qr_code(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        data = f"FAZ-TICKET:{self.ticket_number}:{self.match_id}:{self.ticket_type_id}"
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = io.BytesIO()
        img.save(buffered, "PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        self.qr_code_data = img_str
        return img_str

    def to_dict(self):
        return {
            'id': str(self.id),
            'ticket_number': self.ticket_number,
            'match_id': str(self.match_id),
            'ticket_type': self.ticket_type.name if self.ticket_type else None,
            'qr_code': self.qr_code_data,
            'is_used': self.is_used,
            'used_at': self.used_at.isoformat() if self.used_at else None,
            'match': self.match.to_dict() if self.match else None,
            'image_url': f'/assets/tickets/{self.id}.png',
            'section': self.section,
            'row': self.row,
            'seat': self.seat,
        }