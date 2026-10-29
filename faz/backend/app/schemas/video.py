# app/schemas/video.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID

class VideoBase(BaseModel):
    title: str
    youtube_url: str
    description: Optional[str] = None
    duration: Optional[str] = None
    is_published: bool = True

class VideoCreate(VideoBase):
    pass

class VideoOut(VideoBase):
    id: UUID
    youtube_id: str
    thumbnail_url: Optional[str]
    views: int
    published_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True