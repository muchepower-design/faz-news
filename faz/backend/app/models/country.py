from sqlalchemy import Column, String, Date, ForeignKey, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models._base import Base, ToDictMixin
import uuid


class Country(Base, ToDictMixin):
    __tablename__ = "countries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4 )
    name = Column(String(150), nullable=False, unique=True)

    short_name = Column(String(50), nullable=False, unique=True )

    currency = Column(String(100), nullable=False)

    currency_short = Column(String(50), nullable=False )

    flag_image_url = Column(Text, nullable=True)

    cordinates = Column(String(100), nullable=True)  # e.g., "latitude,longitude")

    continent = Column(String(50), nullable=False)

    national_teams = relationship("NationalTeam", back_populates="country", cascade="all, delete-orphan", lazy=True)

    def __repr__(self):
        return f"<Country {self.name}>"