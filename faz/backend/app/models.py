from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Table, JSON, Date, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import enum
import uuid

# Association table for news and tags
news_tags = Table(
    'news_tags',
    Base.metadata,
    Column('news_id', UUID(as_uuid=True), ForeignKey('news.id')),
    Column('tag_id', UUID(as_uuid=True), ForeignKey('tags.id'))
)

# ---------- Enums ----------
class UserRole(str, enum.Enum):
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

# ---------- Team ----------
class Team(Base):
    __tablename__ = "teams"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, index=True)
    short_name = Column(String)
    logo = Column(String, nullable=True)
    founded = Column(Integer)
    stadium = Column(String)
    coach = Column(String)
    description = Column(Text, nullable=True)
    gender = Column(String, default="male")
    team_type = Column(String, default="club")
    current_league_level = Column(String, nullable=True)
    league_tier = Column(Integer, default=3)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# ---------- User ----------
class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    role = Column(SQLEnum(UserRole), default=UserRole.VIEWER)
    club_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    club = relationship("Team")
    matches_as_referee = relationship("Match", foreign_keys="Match.referee_id", backref="referee")

# ---------- Player ----------
class Player(Base):
    __tablename__ = "players"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True)
    position = Column(String)
    jersey_number = Column(Integer)
    date_of_birth = Column(Date)
    nationality = Column(String)
    photo = Column(String, nullable=True)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"))
    goals = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    appearances = Column(Integer, default=0)
    
    team = relationship("Team")

# ---------- League ----------
class League(Base):
    __tablename__ = "leagues"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, index=True)
    gender = Column(SQLEnum(Gender))
    level = Column(SQLEnum(LeagueLevel))
    tier = Column(Integer)
    season = Column(String)
    current_champion_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    current_champion = relationship("Team", foreign_keys=[current_champion_id])

# ---------- LeagueStanding ----------
class LeagueStanding(Base):
    __tablename__ = "league_standings"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    league_id = Column(UUID(as_uuid=True), ForeignKey("leagues.id"))
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"))
    season = Column(String)
    played = Column(Integer, default=0)
    won = Column(Integer, default=0)
    drawn = Column(Integer, default=0)
    lost = Column(Integer, default=0)
    goals_for = Column(Integer, default=0)
    goals_against = Column(Integer, default=0)
    points = Column(Integer, default=0)
    
    league = relationship("League")
    team = relationship("Team")

# ---------- Match ----------
class Match(Base):
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
    
    events = relationship("MatchEvent", back_populates="match", cascade="all, delete-orphan")
    report = relationship("MatchReport", back_populates="match", uselist=False)

# ---------- MatchEvent ----------
class MatchEvent(Base):
    __tablename__ = "match_events"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_id = Column(UUID(as_uuid=True), ForeignKey("matches.id"))
    event_type = Column(SQLEnum(MatchEventType))
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id"))
    related_player_id = Column(UUID(as_uuid=True), ForeignKey("players.id"), nullable=True)
    minute = Column(Integer)
    minute_added = Column(Integer, default=0)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    match = relationship("Match", back_populates="events")
    player = relationship("Player", foreign_keys=[player_id])
    related_player = relationship("Player", foreign_keys=[related_player_id])

# ---------- MatchReport ----------
class MatchReport(Base):
    __tablename__ = "match_reports"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_id = Column(UUID(as_uuid=True), ForeignKey("matches.id"), unique=True)
    referee_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    content = Column(Text)
    yellow_cards = Column(JSON, default=[])
    red_cards = Column(JSON, default=[])
    incidents = Column(JSON, default=[])
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    match = relationship("Match", back_populates="report")
    referee = relationship("User", foreign_keys=[referee_id])

# ---------- News & Tags ----------
class News(Base):
    __tablename__ = "news"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, index=True)
    slug = Column(String, unique=True, index=True)
    content = Column(Text)
    excerpt = Column(String(500))
    featured_image = Column(String, nullable=True)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    views = Column(Integer, default=0)
    is_published = Column(Boolean, default=True)
    published_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    author = relationship("User")
    tags = relationship("Tag", secondary=news_tags, back_populates="news")

class Tag(Base):
    __tablename__ = "tags"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, index=True)
    slug = Column(String, unique=True)
    news = relationship("News", secondary=news_tags, back_populates="tags")

# ---------- VIDEO MODEL ----------
class Video(Base):
    __tablename__ = "videos"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, index=True, nullable=False)
    youtube_url = Column(String, nullable=False)
    youtube_id = Column(String, nullable=False)  # Extract from URL
    thumbnail_url = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    duration = Column(String, nullable=True)  # e.g., "5:30"
    views = Column(Integer, default=0)
    published_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_published = Column(Boolean, default=True)

# ---------- GALLERY MODELS ----------
class Gallery(Base):
    __tablename__ = "galleries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    cover_image = Column(String, nullable=True)
    event_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_published = Column(Boolean, default=True)
    
    images = relationship("GalleryImage", back_populates="gallery", cascade="all, delete-orphan")

class GalleryImage(Base):
    __tablename__ = "gallery_images"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    gallery_id = Column(UUID(as_uuid=True), ForeignKey("galleries.id", ondelete="CASCADE"))
    image_url = Column(String, nullable=False)
    caption = Column(String, nullable=True)
    order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    gallery = relationship("Gallery", back_populates="images")

# ---------- Cup Competitions ----------
class CupCompetition(Base):
    __tablename__ = "cup_competitions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    gender = Column(SQLEnum(Gender))
    competition_type = Column(String)
    season = Column(String)
    current_champion_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    current_champion = relationship("Team", foreign_keys=[current_champion_id])

class CupSeason(Base):
    __tablename__ = "cup_seasons"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cup_competition_id = Column(UUID(as_uuid=True), ForeignKey("cup_competitions.id"))
    season = Column(String)
    winner_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)
    runner_up_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)
    started_at = Column(Date)
    ended_at = Column(Date, nullable=True)
    
    cup_competition = relationship("CupCompetition")
    winner = relationship("Team", foreign_keys=[winner_id])
    runner_up = relationship("Team", foreign_keys=[runner_up_id])

class CupMatch(Base):
    __tablename__ = "cup_matches"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cup_season_id = Column(UUID(as_uuid=True), ForeignKey("cup_seasons.id"))
    round_name = Column(String)
    home_team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"))
    away_team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"))
    home_score = Column(Integer, default=0)
    away_score = Column(Integer, default=0)
    match_date = Column(DateTime(timezone=True))
    venue = Column(String)
    is_played = Column(Boolean, default=False)
    winner_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    cup_season = relationship("CupSeason")
    home_team = relationship("Team", foreign_keys=[home_team_id])
    away_team = relationship("Team", foreign_keys=[away_team_id])
    winner = relationship("Team", foreign_keys=[winner_id])

# ---------- National Teams ----------
class NationalTeam(Base):
    __tablename__ = "national_teams"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    gender = Column(SQLEnum(Gender))
    age_group = Column(String)
    name = Column(String)
    coach = Column(String, nullable=True)
    captain_id = Column(UUID(as_uuid=True), ForeignKey("players.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    captain = relationship("Player", foreign_keys=[captain_id])

class NationalTeamFixture(Base):
    __tablename__ = "national_team_fixtures"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    national_team_id = Column(UUID(as_uuid=True), ForeignKey("national_teams.id"))
    opponent = Column(String)
    match_date = Column(DateTime(timezone=True))
    venue = Column(String)
    competition = Column(String)
    match_type = Column(SQLEnum(MatchType))
    home_away = Column(String)
    goals_for = Column(Integer, default=0)
    goals_against = Column(Integer, default=0)
    result = Column(String, nullable=True)
    is_played = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    national_team = relationship("NationalTeam")

# ---------- Tournaments ----------
class Tournament(Base):
    __tablename__ = "tournaments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True)
    category = Column(SQLEnum(TournamentCategory))
    gender = Column(SQLEnum(Gender))
    age_group = Column(String, nullable=True)
    has_qualifiers = Column(Boolean, default=False)
    is_major_tournament = Column(Boolean, default=True)
    continent = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class TournamentParticipation(Base):
    __tablename__ = "tournament_participations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    national_team_id = Column(UUID(as_uuid=True), ForeignKey("national_teams.id"))
    tournament_name = Column(String)
    year = Column(String)
    round_reached = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    national_team = relationship("NationalTeam")

# ---------- Promotion/Relegation ----------
class PromotionRelegationRule(Base):
    __tablename__ = "promotion_relegation_rules"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    from_league_id = Column(UUID(as_uuid=True), ForeignKey("leagues.id"))
    to_league_id = Column(UUID(as_uuid=True), ForeignKey("leagues.id"))
    positions_promoted = Column(Integer, default=2)
    positions_relegated = Column(Integer, default=2)
    season = Column(String)
    
    from_league = relationship("League", foreign_keys=[from_league_id])
    to_league = relationship("League", foreign_keys=[to_league_id])

class PromotionRelegation(Base):
    __tablename__ = "promotion_relegations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"))
    from_league_id = Column(UUID(as_uuid=True), ForeignKey("leagues.id"))
    to_league_id = Column(UUID(as_uuid=True), ForeignKey("leagues.id"))
    season = Column(String)
    action = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    team = relationship("Team")
    from_league = relationship("League", foreign_keys=[from_league_id])
    to_league = relationship("League", foreign_keys=[to_league_id])

# ---------- Continental Qualification ----------
class ContinentalQualification(Base):
    __tablename__ = "continental_qualifications"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    season = Column(String)
    competition_name = Column(String)
    gender = Column(SQLEnum(Gender))
    qualifying_team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"))
    qualification_reason = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    qualifying_team = relationship("Team")

# ---------- Bulk Import Log ----------
class BulkImportLog(Base):
    __tablename__ = "bulk_import_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    table_name = Column(String)
    file_name = Column(String)
    rows_imported = Column(Integer)
    errors = Column(Text, nullable=True)
    imported_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    imported_at = Column(DateTime(timezone=True), server_default=func.now())
    
    importer = relationship("User")

# ---------- Season ----------
class Season(Base):
    __tablename__ = "seasons"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True)
    start_date = Column(Date)
    end_date = Column(Date)
    is_current = Column(Boolean, default=False)

# ---------- League Tables (legacy) ----------
class LeagueTable(Base):
    __tablename__ = "league_tables"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"))
    played = Column(Integer, default=0)
    won = Column(Integer, default=0)
    drawn = Column(Integer, default=0)
    lost = Column(Integer, default=0)
    goals_for = Column(Integer, default=0)
    goals_against = Column(Integer, default=0)
    points = Column(Integer, default=0)
    season = Column(String)
    
    team = relationship("Team")


# ---------- Competition (Main competition structure) ----------
class Competition(Base):
    __tablename__ = "competitions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, index=True)
    gender = Column(String)  # 'male', 'female', 'both'
    competition_type = Column(String)  # 'league', 'cup', 'tournament', 'continental'
    level = Column(String, nullable=True)  # 'tier1', 'tier2', 'tier3'
    icon = Column(String, nullable=True)  # emoji or icon name
    description = Column(Text, nullable=True)
    season = Column(String)  # e.g., "2025-2026"
    current_champion_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)
    is_archived = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    current_champion = relationship("Team", foreign_keys=[current_champion_id])
    seasons = relationship("CompetitionSeason", back_populates="competition", cascade="all, delete-orphan")

class CompetitionSeason(Base):
    __tablename__ = "competition_seasons"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competition_id = Column(UUID(as_uuid=True), ForeignKey("competitions.id"), nullable=False)
    season = Column(String, nullable=False)
    champion_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)
    runner_up_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)
    started_at = Column(Date, nullable=True)
    ended_at = Column(Date, nullable=True)
    is_archived = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    competition = relationship("Competition", back_populates="seasons")
    champion = relationship("Team", foreign_keys=[champion_id])
    runner_up = relationship("Team", foreign_keys=[runner_up_id])


    # Add these new models to your models.py

class ProductCategory(Base):
    __tablename__ = "product_categories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, index=True)  # replicas, legends, training, accessories
    display_name = Column(String)  # "Official Replicas", "Legends Collection", etc.
    icon = Column(String, nullable=True)  # emoji or icon class
    description = Column(Text, nullable=True)
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Product(Base):
    __tablename__ = "products"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True)
    slug = Column(String, unique=True, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("product_categories.id"))
    description = Column(Text)
    price = Column(Integer)  # in Zambian Kwacha (ZMW) - stored as cents? or whole number
    compare_price = Column(Integer, nullable=True)  # original price for sale display
    image_url = Column(String, nullable=True)
    images = Column(JSON, default=[])  # array of additional image URLs
    sizes = Column(JSON, default=[])  # array of available sizes (e.g., ["S", "M", "L", "XL"])
    colors = Column(JSON, default=[])  # array of available colors
    stock_quantity = Column(Integer, default=0)
    is_featured = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    category = relationship("ProductCategory", backref="products")

class Cart(Base):
    __tablename__ = "carts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # null for guest carts
    session_id = Column(String, index=True)  # for guest users
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")

class CartItem(Base):
    __tablename__ = "cart_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cart_id = Column(UUID(as_uuid=True), ForeignKey("carts.id"))
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"))
    quantity = Column(Integer, default=1)
    size = Column(String, nullable=True)
    color = Column(String, nullable=True)
    price_at_add = Column(Integer)  # price when added to cart
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    cart = relationship("Cart", back_populates="items")
    product = relationship("Product")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_number = Column(String, unique=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    customer_name = Column(String)
    customer_email = Column(String)
    customer_phone = Column(String)
    shipping_address = Column(Text)
    subtotal = Column(Integer)
    delivery_fee = Column(Integer, default=0)
    total_amount = Column(Integer)
    payment_method = Column(String, nullable=True)  # e.g., "mtn_momo", "airtel_momo", "card"
    payment_reference = Column(String, nullable=True)  # deposit_id from PawaPay
    payment_status = Column(String, default="pending")  # pending, paid, failed, refunded
    order_status = Column(String, default="pending")  # pending, processing, shipped, delivered, cancelled
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"))
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"))
    product_name = Column(String)
    product_image = Column(String, nullable=True)
    quantity = Column(Integer)
    size = Column(String, nullable=True)
    color = Column(String, nullable=True)
    unit_price = Column(Integer)
    subtotal = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    order = relationship("Order", back_populates="items")
    product = relationship("Product")