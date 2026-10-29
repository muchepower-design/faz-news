# app/schemas/cart.py
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID

class AddToCart(BaseModel):
    product_id: UUID
    quantity: int = 1
    size: Optional[str] = None
    color: Optional[str] = None

class CartItemOut(BaseModel):
    id: UUID
    product_id: UUID
    product_name: str
    product_image: Optional[str]
    quantity: int
    size: Optional[str]
    color: Optional[str]
    unit_price: int
    subtotal: int

class CartOut(BaseModel):
    items: List[CartItemOut] = []
    subtotal: int
    total: int