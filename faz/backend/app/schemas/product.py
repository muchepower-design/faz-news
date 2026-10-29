# app/schemas/product.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from uuid import UUID

class ProductBase(BaseModel):
    name: str
    category_id: UUID
    description: str
    price: int
    compare_price: Optional[int] = None
    image_url: Optional[str] = None
    images: List[str] = []
    sizes: List[str] = []
    colors: List[str] = []
    stock_quantity: int = 0
    is_featured: bool = False
    is_active: bool = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    compare_price: Optional[int] = None
    image_url: Optional[str] = None
    images: Optional[List[str]] = None
    sizes: Optional[List[str]] = None
    colors: Optional[List[str]] = None
    stock_quantity: Optional[int] = None
    is_featured: Optional[bool] = None
    is_active: Optional[bool] = None

class ProductOut(ProductBase):
    id: UUID
    slug: str
    created_at: datetime

    class Config:
        from_attributes = True