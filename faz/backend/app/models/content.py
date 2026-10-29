# app/models/content.py
from sqlalchemy import Column, String, Boolean, Integer, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
from app.models._base import Base, ToDictMixin
import uuid


# ============ EXISTING (keep) ============
class HeroSlide(Base, ToDictMixin):
    __tablename__ = "hero_slides"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    subtitle = Column(String(300), nullable=True)
    image_url = Column(Text, nullable=False)
    cta_text = Column(String(100), nullable=True)
    cta_link = Column(String(300), nullable=True)
    slide_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def to_dict(self):
        return {
            "id": str(self.id),
            "title": self.title,
            "subtitle": self.subtitle,
            "image_url": self.image_url,
            "cta_text": self.cta_text,
            "cta_link": self.cta_link,
            "slide_order": self.slide_order or 0,
            "is_active": bool(self.is_active),
        }


class Partner(Base, ToDictMixin):
    __tablename__ = "partners"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    logo_url = Column(Text, nullable=False)
    website_url = Column(String(300), nullable=True)
    tier = Column(String(50), nullable=True)
    partner_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "logo_url": self.logo_url,
            "website_url": self.website_url,
            "tier": self.tier,
            "partner_order": self.partner_order or 0,
            "is_active": bool(self.is_active),
        }


class GovernanceMember(Base, ToDictMixin):
    __tablename__ = "governance_members"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    position = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False)
    province = Column(String(100), nullable=True)
    image_url = Column(Text, nullable=True)
    bio = Column(Text, nullable=True)
    email = Column(String(200), nullable=True)
    term_start = Column(String(20), nullable=True)
    term_end = Column(String(20), nullable=True)
    member_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "position": self.position,
            "category": self.category,
            "province": self.province,
            "image_url": self.image_url,
            "bio": self.bio,
            "email": self.email,
            "term_start": self.term_start,
            "term_end": self.term_end,
            "member_order": self.member_order or 0,
            "is_active": bool(self.is_active),
        }


class Page(Base, ToDictMixin):
    __tablename__ = "pages"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    path = Column(String(300), unique=True, index=True, nullable=False)
    title = Column(String(300), nullable=False)
    subtitle = Column(String(500), nullable=True)
    excerpt = Column(String(500), nullable=True)
    content = Column(Text, nullable=True)
    hero_image_url = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    meta_title = Column(String(200), nullable=True)
    meta_description = Column(Text, nullable=True)
    is_published = Column(Boolean, default=True)
    page_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def to_dict(self):
        return {
            "id": str(self.id),
            "path": self.path,
            "title": self.title,
            "subtitle": self.subtitle,
            "excerpt": self.excerpt,
            "content": self.content,
            "hero_image_url": self.hero_image_url,
            "category": self.category,
            "meta_title": self.meta_title,
            "meta_description": self.meta_description,
            "is_published": bool(self.is_published),
            "page_order": self.page_order or 0,
        }


# ============ NEW ============
class NavItem(Base, ToDictMixin):
    """Self-referential tree for the main navigation / mega-menu."""
    __tablename__ = "nav_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    label = Column(String(200), nullable=False)
    path = Column(String(500), nullable=True)          # null => header-only (children only)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("nav_items.id", ondelete="CASCADE"), nullable=True)
    item_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    is_external = Column(Boolean, default=False)        # renders as <a target="_blank">
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    children = relationship(
        "NavItem",
        backref=backref("parent", remote_side=[id]),
        cascade="all, delete-orphan",
        order_by="NavItem.item_order",
    )

    def to_dict(self, admin=False):
        kids = list(self.children) if admin else [c for c in self.children if c.is_active]
        return {
            "id": str(self.id),
            "label": self.label,
            "path": self.path,
            "parent_id": str(self.parent_id) if self.parent_id else None,
            "item_order": self.item_order or 0,
            "is_active": bool(self.is_active),
            "is_external": bool(self.is_external),
            "children": [c.to_dict(admin=admin) for c in kids],
        }


class FooterSection(Base, ToDictMixin):
    """A column in the footer link area (e.g. 'Quick Links')."""
    __tablename__ = "footer_sections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    section_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    links = relationship(
        "FooterLink",
        backref="section",
        cascade="all, delete-orphan",
        order_by="FooterLink.link_order",
    )

    def to_dict(self, admin=False):
        lks = list(self.links) if admin else [l for l in self.links if l.is_active]
        return {
            "id": str(self.id),
            "title": self.title,
            "section_order": self.section_order or 0,
            "is_active": bool(self.is_active),
            "links": [l.to_dict() for l in lks],
        }


class FooterLink(Base, ToDictMixin):
    __tablename__ = "footer_links"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    section_id = Column(UUID(as_uuid=True), ForeignKey("footer_sections.id", ondelete="CASCADE"), nullable=False)
    label = Column(String(200), nullable=False)
    path = Column(String(500), nullable=True)
    is_external = Column(Boolean, default=False)
    link_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def to_dict(self):
        return {
            "id": str(self.id),
            "section_id": str(self.section_id),
            "label": self.label,
            "path": self.path,
            "is_external": bool(self.is_external),
            "link_order": self.link_order or 0,
            "is_active": bool(self.is_active),
        }