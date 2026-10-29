from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.models._base import Base
import uuid

class Video(Base):
    __tablename__ = "videos"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, index=True, nullable=False)
    youtube_url = Column(String, nullable=False)
    youtube_id = Column(String, nullable=False)
    thumbnail_url = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    duration = Column(String, nullable=True)
    views = Column(Integer, default=0)
    published_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_published = Column(Boolean, default=True)