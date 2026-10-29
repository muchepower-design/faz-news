from flask import Blueprint, request, jsonify, abort
from flask_jwt_extended import jwt_required
from app.database import db
from app.models import (
    NationalTeam, NationalTeamFixture, TournamentParticipation, Tournament,
    Country,
)
from app.auth import get_current_user
from sqlalchemy.orm import joinedload
from datetime import datetime
import uuid


bp = Blueprint('national_teams', __name__)


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def _enrich_team(team):
    """
    Extend NationalTeam.to_dict() with country fields.
    Handles the case where the relationship isn't loaded by falling back
    to an explicit query.
    """
    data = team.to_dict()

    country = team.country
    if country is None and team.country_id:
        country = Country.query.get(team.country_id)

    if country:
        data['country'] = {
            'id': str(country.id),
            'name': country.name,
            'short_name': country.short_name,
            'flag_image_url': country.flag_image_url,
            'continent': country.continent,
            'currency': country.currency,
            'currency_short': country.currency_short,
        }
        # Convenience top-level fields so the frontend doesn't have to dig
        data['country_name'] = country.name
        data['country_short_name'] = country.short_name
        data['country_flag_image_url'] = country.flag_image_url
    else:
        data['country'] = None
        data['country_name'] = None
        data['country_short_name'] = None
        data['country_flag_image_url'] = None

    # If the team has no flag of its own, borrow the country's flag
    if not data.get('flag_image_url') and country and country.flag_image_url:
        data['flag_image_url'] = country.flag_image_url

    return data


def _enrich_fixture(fixture):
    """Add optional opponent-country data if you later link fixtures to countries.
    For now it just returns the fixture dict."""
    return fixture.to_dict()


# ----------------------------------------------------------------------
# National Teams — public
# ----------------------------------------------------------------------
@bp.route('/', methods=['GET'])
def get_national_teams():
    gender = request.args.get('gender')
    age_group = request.args.get('age_group')
    skip = int(request.args.get('skip', 0))
    limit = int(request.args.get('limit', 1000))
    nation = "Zambia"

    query = (
        NationalTeam.query
        .options(joinedload(NationalTeam.country))
        .order_by(NationalTeam.name.asc())
        .filter(NationalTeam.name.ilike(f"%{nation}%"))
    )

    if gender:
        # Case-insensitive match so the frontend can send 'male' / 'female' freely
        query = query.filter(db.func.lower(NationalTeam.gender) == gender.lower())

    if age_group:
        query = query.filter(db.func.lower(NationalTeam.age_group) == age_group.lower())

    teams = query.offset(skip).limit(limit).all()
    return jsonify([_enrich_team(t) for t in teams]), 200


@bp.route('/<team_id>', methods=['GET'])
def get_national_team(team_id):
    try:
        tid = uuid.UUID(team_id)
    except ValueError:
        abort(400, "Invalid team id")

    team = (
        NationalTeam.query
        .options(joinedload(NationalTeam.country))
        .filter_by(id=tid)
        .first()
    )
    if not team:
        abort(404, "National team not found")

    return jsonify(_enrich_team(team)), 200


# ----------------------------------------------------------------------
# Fixtures — public
# ----------------------------------------------------------------------
@bp.route('/<team_id>/fixtures', methods=['GET'])
def get_national_team_fixtures(team_id):
    try:
        tid = uuid.UUID(team_id)
    except ValueError:
        abort(400, "Invalid team id")

    fixtures = (
        NationalTeamFixture.query
        .filter_by(national_team_id=tid)
        .order_by(NationalTeamFixture.match_date)
        .all()
    )
    return jsonify([_enrich_fixture(f) for f in fixtures]), 200


# ----------------------------------------------------------------------
# Tournaments — public
# ----------------------------------------------------------------------
@bp.route('/<team_id>/tournaments', methods=['GET'])
def get_national_team_tournaments(team_id):
    try:
        tid = uuid.UUID(team_id)
    except ValueError:
        abort(400, "Invalid team id")

    tournaments = (
        TournamentParticipation.query
        .filter_by(national_team_id=tid)
        .order_by(TournamentParticipation.year.desc())
        .all()
    )
    return jsonify([t.to_dict() for t in tournaments]), 200


@bp.route('/tournaments/all', methods=['GET'])
def get_all_tournaments():
    gender = request.args.get('gender')
    query = Tournament.query
    if gender:
        query = query.filter(
            db.func.lower(Tournament.gender) == gender.lower()
        )
    return jsonify([t.to_dict() for t in query.all()]), 200


# ----------------------------------------------------------------------
# Fixtures — admin
# ----------------------------------------------------------------------
@bp.route('/<team_id>/fixtures', methods=['POST'])
@jwt_required()
def add_fixture(team_id):
    user = get_current_user()
    if not user or user.role not in ['admin', 'super_admin', 'faz_admin', 'media_officer']:
        abort(403, "Not authorized")

    try:
        tid = uuid.UUID(team_id)
    except ValueError:
        abort(400, "Invalid team id")

    team = NationalTeam.query.get(tid)
    if not team:
        abort(404, "National team not found")

    data = request.get_json() or {}

    required = ['opponent', 'match_date', 'venue', 'competition', 'match_type', 'home_away']
    missing = [f for f in required if not data.get(f)]
    if missing:
        abort(400, f"Missing required fields: {', '.join(missing)}")

    fixture = NationalTeamFixture(
        national_team_id=tid,
        opponent=data['opponent'],
        match_date=datetime.fromisoformat(data['match_date']),
        venue=data['venue'],
        competition=data['competition'],
        match_type=data['match_type'],
        home_away=data['home_away'],
        is_played=False,
    )
    db.session.add(fixture)
    db.session.commit()
    return jsonify({"id": str(fixture.id)}), 201


@bp.route('/fixtures/<fixture_id>', methods=['PATCH'])
@jwt_required()
def update_fixture_result(fixture_id):
    user = get_current_user()
    if not user or user.role not in ['admin', 'super_admin', 'faz_admin', 'match_commissioner']:
        abort(403, "Not authorized")

    fixture = NationalTeamFixture.query.get(fixture_id)
    if not fixture:
        abort(404, "Fixture not found")

    data = request.get_json() or {}
    fixture.goals_for = data.get('goals_for', fixture.goals_for)
    fixture.goals_against = data.get('goals_against', fixture.goals_against)
    fixture.result = data.get('result', fixture.result)
    fixture.is_played = True
    db.session.commit()
    return jsonify({"message": "Updated"}), 200