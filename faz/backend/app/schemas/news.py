# app/schemas/news.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from uuid import UUID

class NewsBase(BaseModel):
    title: str
    content: str
    excerpt: str
    featured_image: Optional[str] = None

class NewsCreate(NewsBase):
    tags: Optional[List[str]] = []

class News(NewsBase):
    id: UUID
    slug: str
    views: int
    is_published: bool
    published_at: datetime
    author_id: UUID

    class Config:
        from_attributes = True