from flask import Blueprint, request, jsonify, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database import db
from app.models import League, LeagueStanding, PromotionRelegationRule, PromotionRelegation
from app.schemas import LeagueCreate
from app.auth import get_current_user, admin_required
import uuid

bp = Blueprint('leagues', __name__)

@bp.route('/', methods=['GET'])
def get_leagues():
    gender = request.args.get('gender')
    season = request.args.get('season')
    query = League.query
    if gender:
        query = query.filter_by(gender=gender)
    if season:
        query = query.filter_by(season=season)
    return jsonify([l.to_dict() for l in query.all()])

@bp.route('/<league_id>', methods=['GET'])
def get_league(league_id):
    try:
        lid = uuid.UUID(league_id)
    except:
        abort(400)
    league = League.query.get(lid)
    if not league:
        abort(404)
    return jsonify(league.to_dict())

@bp.route('/<league_id>/standings', methods=['GET'])
def get_league_standings(league_id):
    try:
        lid = uuid.UUID(league_id)
    except:
        abort(400)
    league = League.query.get(lid)
    if not league:
        abort(404)
    season = request.args.get('season')
    if not season:
        abort(400, "season required")
    
    # Eagerly load the team relationship
    standings = LeagueStanding.query.options(
        db.joinedload(LeagueStanding.team)
    ).filter(
        LeagueStanding.league_id == lid,
        LeagueStanding.season == season
    ).order_by(
        LeagueStanding.points.desc(),
        (LeagueStanding.goals_for - LeagueStanding.goals_against).desc(),
        LeagueStanding.goals_for.desc()
    ).all()
    
    # Convert to dict with team data
    result = []
    for s in standings:
        data = s.to_dict()
        # Add team info
        if s.team:
            data['team'] = {
                'id': str(s.team.id),
                'name': s.team.name,
                'short_name': s.team.short_name,
                'logo': s.team.logo
            }
        result.append(data)
    
    return jsonify(result)

@bp.route('/promotion-relegation/apply', methods=['POST'])
@jwt_required()
@admin_required
def apply_promotion_relegation():
    data = request.get_json()
    season = data.get('season')
    if not season:
        abort(400, "season required")
    rules = PromotionRelegationRule.query.filter_by(season=season).all()
    results = []
    for rule in rules:
        standings = LeagueStanding.query.filter_by(league_id=rule.from_league_id, season=season)\
            .order_by(LeagueStanding.points.desc()).limit(rule.positions_promoted if rule.positions_promoted > 0 else rule.positions_relegated).all()
        for standing in standings:
            action = "promoted" if rule.positions_promoted > 0 else "relegated"
            team = standing.team
            target_league = League.query.get(rule.to_league_id)
            if team and target_league:
                team.current_league_level = target_league.level
                team.league_tier = target_league.tier
                pr = PromotionRelegation(
                    team_id=team.id,
                    from_league_id=rule.from_league_id,
                    to_league_id=rule.to_league_id,
                    season=season,
                    action=action
                )
                db.session.add(pr)
                results.append({
                    "team": team.name,
                    "action": action,
                    "from_league": rule.from_league.name,
                    "to_league": target_league.name
                })
    db.session.commit()
    return jsonify({"message": "Promotion/relegation applied", "results": results})