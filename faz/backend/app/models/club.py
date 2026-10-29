from sqlalchemy import Column, String, Text, ForeignKey, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models._base import Base, ToDictMixin
import uuid

class Club(Base, ToDictMixin):
    __tablename__ = "clubs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)   # <-- NO foreign key!
    name = Column(String(100), nullable=False, unique=True)
    short_name = Column(String(50))
    age = Column(String(50))
    gender = Column(String(50))
    logo_url = Column(String(255))
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    country_id = Column(UUID(as_uuid=True), ForeignKey("countries.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    users = relationship("User", back_populates="club")
    matches = relationship("Match", back_populates="club")
    groups = relationship("Group", secondary="group_clubs", back_populates="clubs")

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "short_name": self.short_name,
            "gender": self.gender,
            "age": self.age,
            "logo_url": self.logo_url,
            "description": self.description,
            "is_active": self.is_active,
            "country_id": str(self.country_id) if self.country_id else None,
        }