# app/models/role.py
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models._base import Base, ToDictMixin
import uuid


class Role(Base, ToDictMixin):
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)

    # Many-to-many with User via the user_roles association table
    users = relationship("User", secondary="user_roles", back_populates="roles")

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
        }

    def __repr__(self):
        return f"<Role {self.name}>"