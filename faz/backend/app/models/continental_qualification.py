from sqlalchemy import Column, String, ForeignKey, UUID, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models._base import Base, ToDictMixin
import uuid

class ContinentalQualification(Base, ToDictMixin):
    __tablename__ = "continental_qualifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    season = Column(String, nullable=False)
    competition_name = Column(String, nullable=False)
    gender = Column(String)
    qualifying_team_id = Column(UUID(as_uuid=True), nullable=False)   # no FK
    qualifying_team_type = Column(String, nullable=False)  # 'national' or 'club'
    qualification_reason = Column(String)
    created_at = Column(DateTime, server_default=func.now())

    def to_dict(self):
        return {
            "id": str(self.id),
            "season": self.season,
            "competition_name": self.competition_name,
            "gender": self.gender,
            "qualifying_team_id": str(self.qualifying_team_id),
            "qualifying_team_type": self.qualifying_team_type,
            "qualification_reason": self.qualification_reason,
        }