from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, date
from typing import Optional, List
import uuid
from uuid import UUID
import enum

# ---------- Enums ----------
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

class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"

class LeagueLevel(str, enum.Enum):
    SUPER_LEAGUE = "super_league"
    DIVISION_ONE = "division_one"
    DIVISION_TWO = "division_two"
    DIVISION_THREE = "division_three"
    PROVINCIAL = "provincial"
    NATIONAL_LEAGUE_SOUTH = "national_league_south"
    NATIONAL_LEAGUE_NORTH = "national_league_north"

class MatchType(str, enum.Enum):
    LEAGUE = "league"
    CUP = "cup"
    FRIENDLY = "friendly"
    TOURNAMENT = "tournament"
    QUALIFIER = "qualifier"

class TournamentCategory(str, enum.Enum):
    FRIENDLY = "friendly"
    COSAFA = "cosafa"
    AFCON = "afcon"
    WAFCON = "wafcon"
    FOUR_NATIONS = "four_nations"
    CHAN = "chan"
    FIFA_WORLD_CUP = "fifa_world_cup"
    OLYMPICS = "olympics"

# ---------- User Schemas ----------
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str
    role: UserRoleEnum = UserRoleEnum.VIEWER
    club_id: Optional[uuid.UUID] = None

class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr
    username: str
    full_name: str
    role: UserRoleEnum
    club_id: Optional[uuid.UUID]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class User(UserBase):
    id: uuid.UUID
    full_name: str
    role: UserRoleEnum
    club_id: Optional[uuid.UUID]
    is_active: bool
    is_admin: bool = False
    created_at: datetime

    class Config:
        from_attributes = True

# ---------- Token Schemas ----------
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# ---------- News Schemas ----------
class NewsBase(BaseModel):
    title: str
    content: str
    excerpt: str
    featured_image: Optional[str] = None

class NewsCreate(NewsBase):
    tags: Optional[List[str]] = []

class News(NewsBase):
    id: uuid.UUID
    slug: str
    views: int
    is_published: bool
    published_at: datetime
    author_id: uuid.UUID

    class Config:
        from_attributes = True

# ---------- Video Schemas ----------
class VideoBase(BaseModel):
    title: str
    youtube_url: str
    description: Optional[str] = None
    duration: Optional[str] = None
    is_published: bool = True

class VideoCreate(VideoBase):
    pass

class VideoOut(VideoBase):
    id: uuid.UUID
    youtube_id: str
    thumbnail_url: Optional[str]
    views: int
    published_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True

# ---------- Gallery Schemas ----------
class GalleryImageBase(BaseModel):
    image_url: str
    caption: Optional[str] = None
    order: int = 0

class GalleryImageCreate(GalleryImageBase):
    pass

class GalleryImageOut(GalleryImageBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True

class GalleryBase(BaseModel):
    title: str
    description: Optional[str] = None
    cover_image: Optional[str] = None
    event_date: Optional[date] = None
    is_published: bool = True

class GalleryCreate(GalleryBase):
    pass

class GalleryOut(GalleryBase):
    id: uuid.UUID
    created_at: datetime
    images: List[GalleryImageOut] = []

    class Config:
        from_attributes = True

# ---------- Match Schemas ----------
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

class MatchCreate(MatchBase):
    pass

class Match(MatchBase):
    id: uuid.UUID
    referee_id: Optional[uuid.UUID] = None

    class Config:
        from_attributes = True

class MatchDetail(Match):
    events: List['MatchEventOut'] = []

# ---------- Team Schemas ----------
class TeamBase(BaseModel):
    name: str
    short_name: str
    logo: Optional[str] = None
    founded: int
    stadium: str
    coach: str
    description: Optional[str] = None

class TeamCreate(TeamBase):
    gender: str = "male"
    team_type: str = "club"
    current_league_level: Optional[str] = None
    league_tier: int = 3

class Team(TeamBase):
    id: uuid.UUID
    gender: str
    team_type: str
    current_league_level: Optional[str]
    league_tier: int
    created_at: datetime

    class Config:
        from_attributes = True

# ---------- Player Schemas ----------
class PlayerBase(BaseModel):
    name: str
    position: str
    jersey_number: int
    date_of_birth: date
    nationality: str
    photo: Optional[str] = None
    team_id: uuid.UUID

class PlayerCreate(PlayerBase):
    pass

class Player(PlayerBase):
    id: uuid.UUID
    goals: int
    assists: int
    appearances: int

    class Config:
        from_attributes = True

# ---------- League Table Schemas ----------
class LeagueTableBase(BaseModel):
    team_id: uuid.UUID
    played: int = 0
    won: int = 0
    drawn: int = 0
    lost: int = 0
    goals_for: int = 0
    goals_against: int = 0
    points: int = 0
    season: str

class LeagueTable(LeagueTableBase):
    id: uuid.UUID
    team: Optional[Team] = None

    class Config:
        from_attributes = True

# ---------- League Schemas ----------
class LeagueBase(BaseModel):
    name: str
    gender: Gender
    level: LeagueLevel
    tier: int
    season: str

class LeagueCreate(LeagueBase):
    pass

class League(LeagueBase):
    id: uuid.UUID
    current_champion_id: Optional[uuid.UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True

# ---------- League Standing Schemas ----------
class LeagueStandingBase(BaseModel):
    league_id: uuid.UUID
    team_id: uuid.UUID
    season: str
    played: int = 0
    won: int = 0
    drawn: int = 0
    lost: int = 0
    goals_for: int = 0
    goals_against: int = 0
    points: int = 0

class LeagueStanding(LeagueStandingBase):
    id: uuid.UUID
    league: Optional[League] = None
    team: Optional[Team] = None

    class Config:
        from_attributes = True

# ---------- Match Event Schemas ----------
class MatchEventBase(BaseModel):
    event_type: MatchEventType
    player_id: uuid.UUID
    related_player_id: Optional[uuid.UUID] = None
    minute: int
    minute_added: int = 0
    description: Optional[str] = None

class MatchEventCreate(MatchEventBase):
    match_id: uuid.UUID

class MatchEventOut(MatchEventBase):
    id: uuid.UUID
    match_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True

# ---------- Cup Competition Schemas ----------
class CupCompetitionBase(BaseModel):
    name: str
    gender: Gender
    competition_type: str
    season: str

class CupCompetitionCreate(CupCompetitionBase):
    pass

class CupCompetitionOut(CupCompetitionBase):
    id: uuid.UUID
    current_champion_id: Optional[uuid.UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True

class CupSeasonBase(BaseModel):
    season: str
    started_at: date
    ended_at: Optional[date] = None

class CupSeasonCreate(CupSeasonBase):
    cup_competition_id: uuid.UUID

class CupSeasonOut(CupSeasonBase):
    id: uuid.UUID
    winner_id: Optional[uuid.UUID]
    runner_up_id: Optional[uuid.UUID]
    cup_competition_id: uuid.UUID

    class Config:
        from_attributes = True

class CupMatchCreate(BaseModel):
    round_name: str
    home_team_id: uuid.UUID
    away_team_id: uuid.UUID
    match_date: datetime
    venue: str

class CupMatchOut(CupMatchCreate):
    id: uuid.UUID
    home_score: int
    away_score: int
    is_played: bool
    winner_id: Optional[uuid.UUID]
    cup_season_id: uuid.UUID

    class Config:
        from_attributes = True

# ---------- National Team Schemas ----------
class NationalTeamBase(BaseModel):
    gender: Gender
    age_group: str
    name: str
    coach: Optional[str] = None

class NationalTeamCreate(NationalTeamBase):
    captain_id: Optional[uuid.UUID] = None

class NationalTeamOut(NationalTeamBase):
    id: uuid.UUID
    captain_id: Optional[uuid.UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True

class NationalTeamFixtureCreate(BaseModel):
    opponent: str
    match_date: datetime
    venue: str
    competition: str
    match_type: MatchType
    home_away: str
    is_qualifier: bool = False

class NationalTeamFixtureOut(NationalTeamFixtureCreate):
    id: uuid.UUID
    national_team_id: uuid.UUID
    goals_for: int
    goals_against: int
    result: Optional[str]
    is_played: bool
    created_at: datetime

    class Config:
        from_attributes = True

# ---------- Tournament Schemas ----------
class TournamentBase(BaseModel):
    name: str
    category: TournamentCategory
    gender: Gender
    age_group: Optional[str] = None
    has_qualifiers: bool = False
    is_major_tournament: bool = True
    continent: Optional[str] = None

class TournamentCreate(TournamentBase):
    pass

class TournamentOut(TournamentBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True

class TournamentParticipationBase(BaseModel):
    tournament_name: str
    year: str
    round_reached: Optional[str] = None

class TournamentParticipationCreate(TournamentParticipationBase):
    national_team_id: uuid.UUID

class TournamentParticipationOut(TournamentParticipationBase):
    id: uuid.UUID
    national_team_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True

# ---------- Promotion/Relegation Schemas ----------
class PromotionRelegationRuleBase(BaseModel):
    from_league_id: uuid.UUID
    to_league_id: uuid.UUID
    positions_promoted: int = 2
    positions_relegated: int = 2
    season: str

class PromotionRelegationRuleCreate(PromotionRelegationRuleBase):
    pass

class PromotionRelegationRuleOut(PromotionRelegationRuleBase):
    id: uuid.UUID

    class Config:
        from_attributes = True

class PromotionRelegationBase(BaseModel):
    team_id: uuid.UUID
    from_league_id: uuid.UUID
    to_league_id: uuid.UUID
    season: str
    action: str

class PromotionRelegationCreate(PromotionRelegationBase):
    pass

class PromotionRelegationOut(PromotionRelegationBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True

# ---------- Continental Qualification Schemas ----------
class ContinentalQualificationBase(BaseModel):
    season: str
    competition_name: str
    gender: Gender
    qualifying_team_id: uuid.UUID
    qualification_reason: str

class ContinentalQualificationCreate(ContinentalQualificationBase):
    pass

class ContinentalQualificationOut(ContinentalQualificationBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True

# ---------- Bulk Import Schemas ----------
class BulkImportResponse(BaseModel):
    success: bool
    rows_imported: int
    errors: Optional[str] = None

# ---------- Season Schemas ----------
class SeasonBase(BaseModel):
    name: str
    start_date: date
    end_date: date
    is_current: bool = False

class SeasonCreate(SeasonBase):
    pass

class SeasonOut(SeasonBase):
    id: uuid.UUID

    class Config:
        from_attributes = True

# ---------- Competition Schemas ----------
class CompetitionBase(BaseModel):
    name: str
    gender: str
    competition_type: str
    level: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None
    season: str
    is_archived: bool = False
    started_at: Optional[date] = None
    ended_at: Optional[date] = None

class CompetitionCreate(CompetitionBase):
    current_champion_id: Optional[UUID] = None

class CompetitionOut(CompetitionBase):
    id: UUID
    current_champion_id: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CompetitionSeasonBase(BaseModel):
    season: str
    started_at: Optional[date] = None
    ended_at: Optional[date] = None
    is_archived: bool = False

class CompetitionSeasonCreate(CompetitionSeasonBase):
    competition_id: UUID
    champion_id: Optional[UUID] = None
    runner_up_id: Optional[UUID] = None

class CompetitionSeasonOut(CompetitionSeasonBase):
    id: uuid.UUID
    competition_id: uuid.UUID
    champion_id: Optional[uuid.UUID] = None
    runner_up_id: Optional[uuid.UUID] = None
    champion: Optional[Team] = None
    runner_up: Optional[Team] = None

    class Config:
        from_attributes = True

# ---------- Forward references ----------
MatchDetail.model_rebuild()


# Add these to your schemas.py

# Product Category Schemas
class ProductCategoryBase(BaseModel):
    name: str
    display_name: str
    icon: Optional[str] = None
    description: Optional[str] = None
    display_order: int = 0
    is_active: bool = True

class ProductCategoryCreate(ProductCategoryBase):
    pass

class ProductCategoryUpdate(BaseModel):
    display_name: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None

class ProductCategoryOut(ProductCategoryBase):
    id: uuid.UUID
    created_at: datetime

# Product Schemas
class ProductBase(BaseModel):
    name: str
    category_id: uuid.UUID
    description: str
    price: int
    compare_price: Optional[int] = None
    image_url: Optional[str] = None
    images: List[str] = []
    sizes: List[str] = []
    colors: List[str] = []
    stock_quantity: int = 0
    is_featured: bool = False
    is_active: bool = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    compare_price: Optional[int] = None
    image_url: Optional[str] = None
    images: Optional[List[str]] = None
    sizes: Optional[List[str]] = None
    colors: Optional[List[str]] = None
    stock_quantity: Optional[int] = None
    is_featured: Optional[bool] = None
    is_active: Optional[bool] = None

class ProductOut(ProductBase):
    id: uuid.UUID
    slug: str
    created_at: datetime

# Cart Schemas
class AddToCart(BaseModel):
    product_id: uuid.UUID
    quantity: int = 1
    size: Optional[str] = None
    color: Optional[str] = None

class CartItemOut(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    product_name: str
    product_image: Optional[str]
    quantity: int
    size: Optional[str]
    color: Optional[str]
    unit_price: int
    subtotal: int

class CartOut(BaseModel):
    items: List[CartItemOut] = []
    subtotal: int
    total: int

# Checkout Schemas
class CheckoutData(BaseModel):
    customer_name: str
    customer_email: str
    customer_phone: str
    shipping_address: str

class PaymentInitiate(BaseModel):
    order_id: uuid.UUID
    provider: str
    phone_number: str

class OrderOut(BaseModel):
    id: uuid.UUID
    order_number: str
    customer_name: str
    customer_email: str
    customer_phone: str
    subtotal: int
    total_amount: int
    payment_status: str
    order_status: str
    created_at: datetime