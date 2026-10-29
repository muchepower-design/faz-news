# app/schemas/gallery.py
from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List
from uuid import UUID

class GalleryImageBase(BaseModel):
    image_url: str
    caption: Optional[str] = None
    order: int = 0

class GalleryImageCreate(GalleryImageBase):
    pass

class GalleryImageOut(GalleryImageBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class GalleryBase(BaseModel):
    title: str
    description: Optional[str] = None
    cover_image: Optional[str] = None
    event_date: Optional[date] = None
    is_published: bool = True

class GalleryCreate(GalleryBase):
    pass

class GalleryOut(GalleryBase):
    id: UUID
    created_at: datetime
    images: List[GalleryImageOut] = []

    class Config:
        from_attributes = True