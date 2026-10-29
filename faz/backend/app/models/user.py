# app/models/user.py
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models._base import Base, ToDictMixin
import uuid


class User(Base, ToDictMixin):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    full_name = Column(String)
    phone = Column(String(20), nullable=True)

    # Legacy single-role column. Kept because auth guards and other code
    # read `user.role`. It is automatically synced to roles[0] on write.
    role = Column(String, default='viewer')

    club_id = Column(UUID(as_uuid=True), ForeignKey("clubs.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    club = relationship("Club", back_populates="users")
    orders = relationship("Order", back_populates="user")

    # The real relationship — the source of truth for permissions
    roles = relationship(
        "Role",
        secondary="user_roles",
        back_populates="users",
        lazy="selectin",
    )

    def has_role(self, role_name):
        """Check for a role by name. Falls back to the legacy column if the
        many-to-many relationship hasn't been populated yet."""
        if self.roles:
            return any(r.name == role_name for r in self.roles)
        return self.role == role_name

    def sync_primary_role(self):
        """Keep the legacy `role` column in step with the `roles` list."""
        if self.roles:
            self.role = self.roles[0].name
        # If roles is empty, leave `role` as-is so existing data isn't lost.

    def to_dict(self):
        role_names = [r.name for r in self.roles] if self.roles else []
        if not role_names and self.role:
            role_names = [self.role]

        return {
            "id": str(self.id),
            "email": self.email,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "phone": self.phone,
            "is_active": self.is_active,
            "role": self.role,
            "roles": role_names,
            "club_id": str(self.club_id) if self.club_id else None,
        }