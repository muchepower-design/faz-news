from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models._base import Base
import uuid


class Match(Base):
    """
    DEPRECATED.

    `Match` is kept as a table for backwards compatibility but is no longer
    used by the ticketing subsystem. Ticket types, tickets, and seat holds
    now belong to `CompetitionMatch`. No new Match rows are created.
    """
    __tablename__ = "matches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    home_team = Column(String, index=True)
    away_team = Column(String, index=True)
    home_score = Column(Integer, default=0)
    away_score = Column(Integer, default=0)
    match_date = Column(DateTime(timezone=True))
    venue = Column(String)
    competition = Column(String)
    status = Column(String, default="upcoming")
    is_home_match = Column(Boolean, default=True)
    referee_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Legacy ticketing flags — kept so historical rows still deserialize,
    # but nothing reads or writes them anymore.
    is_ticketed = Column(Boolean, default=False)
    club_id = Column(UUID(as_uuid=True), ForeignKey("clubs.id"), nullable=True)
    match_type = Column(String)
    competition_match_id = Column(
        UUID(as_uuid=True),
        ForeignKey('competition_matches.id', ondelete='SET NULL'),
        nullable=True,
        unique=True,
    )

    # ------------------------------------------------------------------
    # Non-ticketing relationships
    # ------------------------------------------------------------------
    events = relationship("MatchEvent", back_populates="match", cascade="all, delete-orphan")
    report = relationship("MatchReport", back_populates="match", uselist=False)
    referee = relationship("User", foreign_keys=[referee_id])
    club = relationship("Club", back_populates="matches")

    # ------------------------------------------------------------------
    # Ticketing relationships removed:
    #   tickets — Ticket now belongs to CompetitionMatch
    #   holds   — SeatHold now belongs to CompetitionMatch
    #   ticket_types was on this model earlier; also removed
    # ------------------------------------------------------------------

    @property
    def date_time(self):
        """Alias for match_date, kept for any lingering frontend expectations."""
        return self.match_date

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}