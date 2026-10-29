from sqlalchemy import Column, String, Date, Boolean
from sqlalchemy.dialects.postgresql import UUID
from app.models._base import Base
import uuid

class Season(Base):
    __tablename__ = "seasons"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True)
    start_date = Column(Date)
    end_date = Column(Date)
    is_current = Column(Boolean, default=False)