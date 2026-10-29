from sqlalchemy import Column, String, ForeignKey, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models._base import Base, ToDictMixin
import uuid

class NationalTeam(Base, ToDictMixin):
    __tablename__ = "national_teams"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)   # <-- NO foreign key!
    name = Column(String, nullable=False)
    short_name = Column(String(100), nullable=False)
    gender = Column(String)
    age_group = Column(String)
    coach = Column(String, nullable=True)
    captain_id = Column(UUID(as_uuid=True), ForeignKey("players.id"), nullable=True)
    country_id = Column(UUID(as_uuid=True), ForeignKey("countries.id", ondelete="CASCADE"), nullable=False)
    age = Column(String(100), nullable=False, default="Senior")
    nickname = Column(String(200), nullable=True)
    fifa_code = Column(String(50), nullable=False)
    flag_image_url = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    country = relationship("Country", back_populates="national_teams")
    captain = relationship("Player", foreign_keys=[captain_id])
    groups = relationship("Group", secondary="group_national_teams", back_populates="national_teams")

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "short_name": self.short_name,
            "gender": self.gender,
            "age_group": self.age_group,
            "coach": self.coach,
            "country_id": str(self.country_id) if self.country_id else None,
            "fifa_code": self.fifa_code,
            "flag_image_url": self.flag_image_url,
            "nickname": self.nickname,
            # include other fields as needed
        }