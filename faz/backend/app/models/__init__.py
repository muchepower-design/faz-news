# app/models/__init__.py
from app.models._base import Base, UserRole, MatchEventType, Gender, LeagueLevel, MatchType, TournamentCategory, ToDictMixin
from app.models.associations import news_tags
from app.models.user import User
from app.models.player import Player
from app.models.league import League
from app.models.league_standing import LeagueStanding
from app.models.match import Match
from app.models.match_event import MatchEvent
from app.models.match_report import MatchReport
from app.models.news import News
from app.models.tag import Tag
from app.models.video import Video
from app.models.gallery import Gallery
from app.models.gallery_image import GalleryImage
from app.models.cup_competition import CupCompetition
from app.models.cup_season import CupSeason
from app.models.cup_match import CupMatch
from app.models.national_team import NationalTeam
from app.models.national_team_fixture import NationalTeamFixture
from app.models.tournament import Tournament
from app.models.tournament_participation import TournamentParticipation
from app.models.promotion_relegation_rule import PromotionRelegationRule
from app.models.promotion_relegation import PromotionRelegation
from app.models.continental_qualification import ContinentalQualification
from app.models.bulk_import_log import BulkImportLog
from app.models.season import Season
from app.models.league_table import LeagueTable
from app.models.competition import Competition
from app.models.competition_season import CompetitionSeason
from app.models.product_category import ProductCategory
from app.models.product import Product
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.country import Country

# Ticketing models (updated to use Match)
from app.models.club import Club
from app.models.ticket_type import TicketType
from app.models.ticket import Ticket
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.hold import SeatHold
from app.models.role import Role
from app.models.user_role import UserRole

# Other models
from app.models.stage import Stage
from app.models.group import Group
from app.models.competition_match import CompetitionMatch
from app.models.standing import Standing
from app.models.qualification_rule import QualificationRule
from app.models.group_national_team import GroupNationalTeam
from app.models.group_club import GroupClub
from backend.app.models.content_old import HeroSlide, Partner, GovernanceMember, Page
from .stadium_section import StadiumSection

__all__ = [
    'Base', 'Role', 'UserRole', 'MatchEventType', 'Gender', 'LeagueLevel', 'MatchType', 'TournamentCategory', 'ToDictMixin',
    'news_tags',
    'User', 'Player', 'League', 'LeagueStanding', 'Match', 'MatchEvent', 'MatchReport',
    'News', 'Tag', 'Video', 'Gallery', 'GalleryImage',
    'CupCompetition', 'CupSeason', 'CupMatch',
    'NationalTeam', 'NationalTeamFixture',
    'Tournament', 'TournamentParticipation',
    'PromotionRelegationRule', 'PromotionRelegation',
    'ContinentalQualification', 'BulkImportLog', 'Season', 'LeagueTable',
    'Competition', 'CompetitionSeason',
    'ProductCategory', 'Product', 'Cart', 'CartItem', 'Country',
    # Ticketing
    'Club', 'TicketType', 'Ticket', 'Order', 'OrderItem', 'SeatHold',
    'Stage', 'Group', 'CompetitionMatch', 'Standing', 'QualificationRule',
    'GroupNationalTeam', 'GroupClub', 'StadiumSection', 'HeroSlide', 'Partner', 'GovernanceMember', 'Page',
]