from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from typing import Optional, List
import enum

# Enums for roles and match events (must match models)
class UserRoleEnum(str, enum.Enum):
    ADMIN = "admin"
    MATCH_COMMISSIONER = "match_commissioner"
    MEDIA_OFFICER = "media_officer"
    CLUB_REP = "club_rep"
    REFEREE = "referee"
    VIEWER = "viewer"

class MatchEventType(str, enum.Enum):
    GOAL = "goal"
    ASSIST = "assist"
    YELLOW_CARD = "yellow_card"
    RED_CARD = "red_card"
    SUBSTITUTION = "substitution"
    PENALTY = "penalty"
    OWN_GOAL = "own_goal"

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str
    role: UserRoleEnum = UserRoleEnum.VIEWER
    club_id: Optional[int] = None

class User(UserBase):
    id: int
    full_name: str
    role: UserRoleEnum
    club_id: Optional[int]
    is_active: bool
    is_admin: bool  # legacy, can be derived from role
    created_at: datetime
    
    class Config:
        from_attributes = True

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# News schemas
class NewsBase(BaseModel):
    title: str
    content: str
    excerpt: str
    featured_image: Optional[str] = None

class NewsCreate(NewsBase):
    tags: Optional[List[str]] = []

class News(NewsBase):
    id: int
    slug: str
    views: int
    is_published: bool
    published_at: datetime
    author_id: int
    
    class Config:
        from_attributes = True

# Match schemas
class MatchBase(BaseModel):
    home_team: str
    away_team: str
    home_score: int = 0
    away_score: int = 0
    match_date: datetime
    venue: str
    competition: str
    status: str = "upcoming"
    is_home_match: bool = True

class Match(MatchBase):
    id: int
    
    class Config:
        from_attributes = True

# Team schemas
class TeamBase(BaseModel):
    name: str
    short_name: str
    logo: Optional[str] = None
    founded: int
    stadium: str
    coach: str
    description: Optional[str] = None

class Team(TeamBase):
    id: int
    
    class Config:
        from_attributes = True

# Player schemas
class PlayerBase(BaseModel):
    name: str
    position: str
    jersey_number: int
    date_of_birth: date
    nationality: str
    photo: Optional[str] = None
    team_id: int

class Player(PlayerBase):
    id: int
    goals: int
    assists: int
    appearances: int
    
    class Config:
        from_attributes = True

# League Table schemas
class LeagueTableBase(BaseModel):
    team_id: int
    played: int = 0
    won: int = 0
    drawn: int = 0
    lost: int = 0
    goals_for: int = 0
    goals_against: int = 0
    points: int = 0
    season: str

class LeagueTable(LeagueTableBase):
    id: int
    team: Optional["Team"] = None  # ← Add this line
    
    class Config:
        from_attributes = True

# Match Event schemas
class MatchEventBase(BaseModel):
    event_type: MatchEventType
    player_id: int
    related_player_id: Optional[int] = None
    minute: int
    minute_added: int = 0
    description: Optional[str] = None

class MatchEventCreate(MatchEventBase):
    match_id: int

class MatchEventOut(MatchEventBase):
    id: int
    match_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Extended Match with events
class MatchDetail(Match):
    events: List[MatchEventOut] = []

# Bulk Import response
class BulkImportResponse(BaseModel):
    success: bool
    rows_imported: int
    errors: Optional[str] = None

# Additional schemas for user output (without password)
class UserOut(UserBase):
    id: int
    full_name: str
    role: UserRoleEnum
    club_id: Optional[int]
    is_active: bool
    created_at: datetime

class MatchCreate(MatchBase):
    pass

class TeamCreate(TeamBase):
    pass

class PlayerCreate(PlayerBase):
    pass



# ---------- Cup Schemas ----------
class CupCompetitionBase(BaseModel):
    name: str
    gender: str
    competition_type: str
    season: str

class CupCompetitionCreate(CupCompetitionBase):
    pass

class CupCompetitionOut(CupCompetitionBase):
    id: int
    created_at: datetime

class CupSeasonBase(BaseModel):
    season: str
    started_at: date

class CupSeasonCreate(CupSeasonBase):
    cup_competition_id: int

class CupSeasonOut(CupSeasonBase):
    id: int
    winner_id: Optional[int]
    runner_up_id: Optional[int]
    ended_at: Optional[date]

class CupMatchCreate(BaseModel):
    round_name: str
    home_team_id: int
    away_team_id: int
    match_date: datetime
    venue: str

class CupMatchOut(CupMatchCreate):
    id: int
    home_score: int
    away_score: int
    is_played: bool
    winner_id: Optional[int]

class ContinentalQualificationOut(BaseModel):
    id: int
    season: str
    competition_name: str
    gender: str
    qualifying_team_id: int
    qualification_reason: str

# ---------- National Team Fixture Create ----------
class NationalTeamFixtureCreate(BaseModel):
    opponent: str
    match_date: datetime
    venue: str
    competition: str
    match_type: str
    home_away: str
    is_qualifier: bool = False