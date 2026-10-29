from flask import Blueprint, request, jsonify, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database import db
from app.models import Competition, CompetitionSeason, League, LeagueStanding
from app.schemas import CompetitionCreate, CompetitionSeasonCreate
from app.auth import admin_required, get_current_user
from sqlalchemy.orm import joinedload
import uuid

bp = Blueprint('competitions', __name__)

@bp.route('/', methods=['GET'])
def get_competitions():
    gender = request.args.get('gender')
    competition_type = request.args.get('competition_type')
    query = Competition.query.filter_by(is_archived=False)
    if gender:
        query = query.filter_by(gender=gender)
    if competition_type:
        query = query.filter_by(competition_type=competition_type)
    competitions = query.all()
    return jsonify([c.to_dict() for c in competitions])

@bp.route('/seasons', methods=['GET'])
def get_seasons():
    seasons = db.session.query(Competition.season).distinct().order_by(Competition.season.desc()).all()
    seasons_list = [s[0] for s in seasons if s[0]]
    # also from league_standings
    league_seasons = db.session.query(LeagueStanding.season).distinct().order_by(LeagueStanding.season.desc()).all()
    for s in league_seasons:
        if s[0] and s[0] not in seasons_list:
            seasons_list.append(s[0])
    seasons_list.sort(reverse=True)
    return jsonify(seasons_list)

@bp.route('/<competition_id>', methods=['GET'])
def get_competition_by_id(competition_id):
    try:
        comp_id = uuid.UUID(competition_id)
    except:
        abort(400, "Invalid competition ID format")

    # Load competition with current_champion relation
    competition = Competition.query.options(
        joinedload(Competition.current_champion)
    ).get(comp_id)
    if not competition:
        abort(404)

    season = request.args.get('season')
    target_season = season or competition.season

    # get standings
    league = League.query.filter_by(name=competition.name, season=target_season).first()
    standings = []
    if league:
        standings = LeagueStanding.query.filter_by(league_id=league.id, season=target_season)\
            .options(joinedload(LeagueStanding.team))\
            .order_by(LeagueStanding.points.desc()).all()

    # seasons history with champion & runner-up loaded
    seasons_history = CompetitionSeason.query.options(
        joinedload(CompetitionSeason.champion),
        joinedload(CompetitionSeason.runner_up)
    ).filter_by(competition_id=comp_id).order_by(CompetitionSeason.season.desc()).all()

    # Build response including relationships
    competition_data = competition.to_dict()
    if competition.current_champion:
        competition_data['current_champion'] = competition.current_champion.to_dict()
    else:
        competition_data['current_champion'] = None

    # Build history list with champion/runner-up names
    history_data = []
    for s in seasons_history:
        item = s.to_dict()
        item['champion'] = s.champion.to_dict() if s.champion else None
        item['runner_up'] = s.runner_up.to_dict() if s.runner_up else None
        history_data.append(item)

    return jsonify({
        "competition": competition_data,
        "standings": [s.to_dict() for s in standings],
        "current_season": target_season,
        "history": history_data
    })

@bp.route('/<competition_id>/standings', methods=['GET'])
def get_competition_standings(competition_id):
    try:
        comp_id = uuid.UUID(competition_id)
    except:
        abort(400)
    competition = Competition.query.get(comp_id)
    if not competition:
        abort(404)
    season = request.args.get('season')
    if not season:
        abort(400, "season required")
    league = League.query.filter_by(name=competition.name, season=season).first()
    if not league:
        # try fuzzy match
        league = League.query.filter(League.name.ilike(f"%{competition.name.split()[0]}%"), League.season==season).first()
    if league:
        standings = LeagueStanding.query.filter_by(league_id=league.id, season=season)\
            .options(joinedload(LeagueStanding.team))\
            .order_by(LeagueStanding.points.desc()).all()
        return jsonify([s.to_dict() for s in standings])
    return jsonify([])

@bp.route('/<competition_id>/seasons', methods=['POST'])
@jwt_required()
@admin_required
def add_competition_season(competition_id):
    try:
        comp_id = uuid.UUID(competition_id)
    except:
        abort(400)
    competition = Competition.query.get(comp_id)
    if not competition:
        abort(404)
    data = request.get_json()
    existing = CompetitionSeason.query.filter_by(competition_id=comp_id, season=data['season']).first()
    if existing:
        abort(400, "Season already exists")
    season = CompetitionSeason(
        competition_id=comp_id,
        season=data['season'],
        champion_id=data.get('champion_id'),
        runner_up_id=data.get('runner_up_id'),
        started_at=data.get('started_at'),
        ended_at=data.get('ended_at')
    )
    db.session.add(season)
    db.session.commit()
    return jsonify({"id": str(season.id)}), 201