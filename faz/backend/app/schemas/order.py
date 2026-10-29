# app/schemas/order.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID

class CheckoutData(BaseModel):
    customer_name: str
    customer_email: str
    customer_phone: str
    shipping_address: str

class PaymentInitiate(BaseModel):
    order_id: UUID
    provider: str
    phone_number: str

class OrderOut(BaseModel):
    id: UUID
    order_number: str
    customer_name: str
    customer_email: str
    customer_phone: str
    subtotal: int
    total_amount: int
    payment_status: str
    order_status: str
    created_at: datetime

    class Config:
        from_attributes = True