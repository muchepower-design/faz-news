from flask import Blueprint, request, jsonify, abort
from flask_jwt_extended import jwt_required
from app.database import db
from app.models import CupCompetition, CupSeason, CupMatch, NationalTeam, Club, ContinentalQualification, League, LeagueStanding, Gender
from app.schemas import CupMatchCreate
from app.auth import get_current_user, admin_required
from datetime import datetime

bp = Blueprint('cups', __name__)

# Helper to get team by ID and type
def get_team_by_id(team_id, team_type):
    if team_type == 'national':
        return NationalTeam.query.get(team_id)
    elif team_type == 'club':
        return Club.query.get(team_id)
    return None

@bp.route('/', methods=['GET'])
def get_cup_competitions():
    gender = request.args.get('gender')
    season = request.args.get('season')
    query = CupCompetition.query
    if gender:
        query = query.filter_by(gender=gender)
    if season:
        query = query.filter_by(season=season)
    return jsonify([c.to_dict() for c in query.all()])

@bp.route('/<cup_id>', methods=['GET'])
def get_cup_competition(cup_id):
    cup = CupCompetition.query.get(cup_id)
    if not cup:
        abort(404)
    return jsonify(cup.to_dict())

@bp.route('/<cup_id>/seasons', methods=['GET'])
def get_cup_seasons(cup_id):
    seasons = CupSeason.query.filter_by(cup_competition_id=cup_id).order_by(CupSeason.season.desc()).all()
    return jsonify([s.to_dict() for s in seasons])

@bp.route('/<cup_id>/seasons', methods=['POST'])
@jwt_required()
def create_cup_season(cup_id):
    user = get_current_user()
    if user.role not in ['admin', 'match_commissioner']:
        abort(403)
    cup = CupCompetition.query.get(cup_id)
    if not cup:
        abort(404)
    data = request.get_json()
    season = data.get('season')
    started_at = data.get('started_at')
    if not season or not started_at:
        abort(400, "season and started_at required")
    existing = CupSeason.query.filter_by(cup_competition_id=cup_id, season=season).first()
    if existing:
        abort(400, "Season already exists")
    try:
        start_date = datetime.strptime(started_at, '%Y-%m-%d').date()
    except:
        abort(400, "Invalid date format, use YYYY-MM-DD")
    cup_season = CupSeason(
        cup_competition_id=cup_id,
        season=season,
        started_at=start_date
    )
    db.session.add(cup_season)
    db.session.commit()
    return jsonify({"id": str(cup_season.id)}), 201

@bp.route('/seasons/<season_id>/matches', methods=['GET'])
def get_cup_matches(season_id):
    round_name = request.args.get('round_name')
    query = CupMatch.query.filter_by(cup_season_id=season_id)
    if round_name:
        query = query.filter_by(round_name=round_name)
    matches = query.order_by(CupMatch.match_date).all()
    return jsonify([m.to_dict() for m in matches])

@bp.route('/seasons/<season_id>/matches', methods=['POST'])
@jwt_required()
def add_cup_match(season_id):
    user = get_current_user()
    if user.role not in ['admin', 'match_commissioner']:
        abort(403)
    season = CupSeason.query.get(season_id)
    if not season:
        abort(404)
    data = request.get_json()
    team_type = data.get('team_type', 'club')  # 'national' or 'club'
    home = get_team_by_id(data['home_team_id'], team_type)
    away = get_team_by_id(data['away_team_id'], team_type)
    if not home or not away:
        abort(404, "One or both teams not found")
    match = CupMatch(
        cup_season_id=season_id,
        round_name=data['round_name'],
        home_team_id=data['home_team_id'],
        away_team_id=data['away_team_id'],
        team_type=team_type,
        match_date=datetime.fromisoformat(data['match_date']),
        venue=data['venue'],
        is_played=False
    )
    db.session.add(match)
    db.session.commit()
    return jsonify({"id": str(match.id)}), 201

@bp.route('/matches/<match_id>', methods=['PATCH'])
@jwt_required()
def update_cup_match_result(match_id):
    user = get_current_user()
    if user.role not in ['admin', 'match_commissioner']:
        abort(403)
    match = CupMatch.query.get(match_id)
    if not match:
        abort(404)
    data = request.get_json()
    match.home_score = data.get('home_score', match.home_score)
    match.away_score = data.get('away_score', match.away_score)
    match.is_played = True
    if data.get('winner_id'):
        winner = get_team_by_id(data['winner_id'], match.team_type)
        if not winner:
            abort(404, "Winner team not found")
        match.winner_id = data['winner_id']
    db.session.commit()
    return jsonify({"message": "Updated"})

# Continental Qualifications (unchanged except team lookup)
@bp.route('/continental-qualifications', methods=['GET'])
def get_continental_qualifications():
    season = request.args.get('season')
    if not season:
        abort(400, "season required")
    quals = ContinentalQualification.query.filter_by(season=season).all()
    return jsonify([q.to_dict() for q in quals])

@bp.route('/continental-qualifications/apply', methods=['POST'])
@jwt_required()
@admin_required
def apply_continental_qualifications():
    data = request.get_json()
    season = data.get('season')
    if not season:
        abort(400, "season required")
    results = []

    # Men's Super League
    men_super = League.query.filter_by(name="MTN Super League", season=season).first()
    if men_super:
        standings = LeagueStanding.query.filter_by(league_id=men_super.id, season=season)\
            .order_by(LeagueStanding.points.desc()).limit(2).all()
        if len(standings) >= 1:
            champ = standings[0]
            # Get team name based on type
            team = get_team_by_id(champ.team_id, champ.team_type)
            team_name = team.name if team else "Unknown"
            existing = ContinentalQualification.query.filter_by(season=season, competition_name="CAF Champions League", qualifying_team_id=champ.team_id).first()
            if not existing:
                qual = ContinentalQualification(
                    season=season,
                    competition_name="CAF Champions League",
                    gender=Gender.MALE.value,
                    qualifying_team_id=champ.team_id,
                    qualifying_team_type=champ.team_type,
                    qualification_reason="Super League Winner"
                )
                db.session.add(qual)
                results.append({"team": team_name, "competition": "CAF Champions League"})
        if len(standings) >= 2:
            runner = standings[1]
            team = get_team_by_id(runner.team_id, runner.team_type)
            team_name = team.name if team else "Unknown"
            existing = ContinentalQualification.query.filter_by(season=season, competition_name="CAF Confederation Cup", qualifying_team_id=runner.team_id).first()
            if not existing:
                qual = ContinentalQualification(
                    season=season,
                    competition_name="CAF Confederation Cup",
                    gender=Gender.MALE.value,
                    qualifying_team_id=runner.team_id,
                    qualifying_team_type=runner.team_type,
                    qualification_reason="Super League Runner-up"
                )
                db.session.add(qual)
                results.append({"team": team_name, "competition": "CAF Confederation Cup"})

    # Women's Super League
    women_super = League.query.filter_by(name="Women's Super League", season=season).first()
    if women_super:
        winner = LeagueStanding.query.filter_by(league_id=women_super.id, season=season)\
            .order_by(LeagueStanding.points.desc()).first()
        if winner:
            team = get_team_by_id(winner.team_id, winner.team_type)
            team_name = team.name if team else "Unknown"
            existing = ContinentalQualification.query.filter_by(season=season, competition_name="COSAFA Women's Champions League", qualifying_team_id=winner.team_id).first()
            if not existing:
                qual = ContinentalQualification(
                    season=season,
                    competition_name="COSAFA Women's Champions League",
                    gender=Gender.FEMALE.value,
                    qualifying_team_id=winner.team_id,
                    qualifying_team_type=winner.team_type,
                    qualification_reason="Women's Super League Winner"
                )
                db.session.add(qual)
                results.append({"team": team_name, "competition": "COSAFA Women's Champions League"})

    db.session.commit()
    return jsonify({"message": f"Continental qualifications applied for {season}", "qualifications": results})