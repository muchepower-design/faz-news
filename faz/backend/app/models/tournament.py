from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.models._base import Base
import uuid

class Tournament(Base):
    __tablename__ = "tournaments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True)
    category = Column(String)
    gender = Column(String)
    age_group = Column(String, nullable=True)
    has_qualifiers = Column(Boolean, default=False)
    is_major_tournament = Column(Boolean, default=True)
    continent = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())