# app/schemas/product_category.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID

class ProductCategoryBase(BaseModel):
    name: str
    display_name: str
    icon: Optional[str] = None
    description: Optional[str] = None
    display_order: int = 0
    is_active: bool = True

class ProductCategoryCreate(ProductCategoryBase):
    pass

class ProductCategoryUpdate(BaseModel):
    display_name: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None

class ProductCategoryOut(ProductCategoryBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True