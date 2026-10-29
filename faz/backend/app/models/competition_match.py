from sqlalchemy import Column, String, Integer, Boolean, DateTime, UUID, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models._base import Base, ToDictMixin
import uuid


def _resolve_team_info(team_id):
    """
    Resolve a UUID to a rich team info dict.

    Looks in NationalTeam first, then Club. Returns:
        {
            "id":           str | None,
            "name":         str,
            "type":         "national" | "club" | None,
            "country_id":   str | None,
            "country_name": str | None,
        }
    Falls back to a TBD stub if the team cannot be found.
    """
    if not team_id:
        return {
            "id": None,
            "name": "TBD",
            "type": None,
            "country_id": None,
            "country_name": None,
        }

    # Lazy imports to avoid circulars
    from app.models.national_team import NationalTeam
    from app.models.club import Club

    # --- NationalTeam? ---
    nt = NationalTeam.query.get(team_id)
    if nt:
        country = nt.country  # relationship on NationalTeam
        return {
            "id": str(nt.id),
            "name": nt.name,
            "type": "national",
            "country_id": str(nt.country_id) if nt.country_id else None,
            "country_name": country.name if country else None,
        }

    # --- Club? ---
    club = Club.query.get(team_id)
    if club:
        country = getattr(club, "country", None)
        # Club model above doesn't declare a `country` relationship,
        # so fall back to a direct lookup if needed.
        if country is None and club.country_id:
            from app.models.country import Country
            country = Country.query.get(club.country_id)
        return {
            "id": str(club.id),
            "name": club.name,
            "type": "club",
            "country_id": str(club.country_id) if club.country_id else None,
            "country_name": country.name if country else None,
        }

    # --- Unknown / legacy ---
    return {
        "id": str(team_id),
        "name": "TBD",
        "type": None,
        "country_id": None,
        "country_name": None,
    }


def _resolve_team_name(team_id):
    """Backwards-compatible string-only resolver."""
    return _resolve_team_info(team_id)["name"]


class CompetitionMatch(Base, ToDictMixin):
    __tablename__ = "competition_matches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    season_id = Column(UUID(as_uuid=True), ForeignKey("competition_seasons.id"), nullable=False)
    stage_id = Column(UUID(as_uuid=True), ForeignKey("stages.id"), nullable=False)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id"), nullable=True)
    home_team_id = Column(UUID(as_uuid=True), nullable=False)
    away_team_id = Column(UUID(as_uuid=True), nullable=False)
    home_score = Column(Integer, default=0)
    away_score = Column(Integer, default=0)
    match_date = Column(DateTime, nullable=False)
    venue = Column(String)
    status = Column(String, default="scheduled")
    is_ticketed = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Competition structure
    season = relationship("CompetitionSeason", back_populates="matches")
    stage = relationship("Stage", back_populates="matches")
    group = relationship("Group", back_populates="matches")

    # Ticketing
    ticket_types = relationship(
        "TicketType",
        back_populates="match",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    tickets = relationship(
        "Ticket",
        back_populates="match",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    seat_holds = relationship(
        "SeatHold",
        back_populates="match",
        cascade="all, delete-orphan",
    )

    # ------------------------------------------------------------------
    # Display helpers — resolve UUIDs to names for code that expects
    # `match.home_team` / `match.away_team` as strings.
    # ------------------------------------------------------------------
    @property
    def home_team(self):
        return _resolve_team_name(self.home_team_id)

    @property
    def away_team(self):
        return _resolve_team_name(self.away_team_id)

    def to_dict(self):
        tts = list(self.ticket_types or [])
        total_capacity = sum((tt.capacity or 0) for tt in tts)
        total_sold = sum((tt.tickets_sold or 0) for tt in tts)
        held = sum((h.quantity or 0) for h in (self.seat_holds or []))
        total_available = max(0, total_capacity - total_sold - held)

        # Resolve both teams exactly once
        home_info = _resolve_team_info(self.home_team_id)
        away_info = _resolve_team_info(self.away_team_id)

        return {
            "id": str(self.id),
            "season_id": str(self.season_id),
            "stage_id": str(self.stage_id),
            "group_id": str(self.group_id) if self.group_id else None,

            # --- Home team ---
            "home_team_id": str(self.home_team_id),
            "home_team": home_info["name"],
            "home_team_info": home_info,

            # --- Away team ---
            "away_team_id": str(self.away_team_id),
            "away_team": away_info["name"],
            "away_team_info": away_info,

            "home_score": self.home_score if self.home_score is not None else 0,
            "away_score": self.away_score if self.away_score is not None else 0,
            "match_date": self.match_date.isoformat() if self.match_date else None,
            "venue": self.venue,
            "status": self.status,
            "is_ticketed": bool(self.is_ticketed),
            "ticket_types": [tt.to_dict() for tt in tts],
            "total_capacity": total_capacity,
            "total_tickets_sold": total_sold,
            "total_available": total_available,
        }