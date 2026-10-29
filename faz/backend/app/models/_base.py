from app.database import db
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Table, JSON, Date, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
import uuid

# ------------------ Custom base model with to_dict ------------------
class Base(db.Model):
    __abstract__ = True

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# Mixin for models that don't inherit from Base (optional)
class ToDictMixin:
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# ------------------ Enums (unchanged) ------------------
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