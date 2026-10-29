from sqlalchemy import Column, String, Text, Integer, Boolean, JSON, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models._base import Base
import uuid

class Product(Base):
    __tablename__ = "products"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True)
    slug = Column(String, unique=True, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("product_categories.id"))
    description = Column(Text)
    price = Column(Integer)
    compare_price = Column(Integer, nullable=True)
    image_url = Column(String, nullable=True)
    images = Column(JSON, default=[])
    sizes = Column(JSON, default=[])
    colors = Column(JSON, default=[])
    stock_quantity = Column(Integer, default=0)
    is_featured = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    category = relationship("ProductCategory", backref="products")