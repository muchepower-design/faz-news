# app/schemas/_base.py
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, date
from typing import Optional, List
import uuid
from uuid import UUID
import enum

# ---------- Enums (for schemas) ----------
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