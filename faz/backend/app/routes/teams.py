from flask import Blueprint, request, jsonify, abort
from app.database import db
from app.models import NationalTeam, Club

bp = Blueprint('teams', __name__)

@bp.route('/', methods=['GET'])
def get_teams():
    """Return all teams (national + club) with a 'type' field."""
    skip = int(request.args.get('skip', 0))
    limit = int(request.args.get('limit', 20))

    national = NationalTeam.query.offset(skip).limit(limit).all()
    clubs = Club.query.offset(skip).limit(limit).all()

    # Combine and add type
    result = []
    for t in national:
        d = t.to_dict()
        d['type'] = 'national'
        result.append(d)
    for t in clubs:
        d = t.to_dict()
        d['type'] = 'club'
        result.append(d)

    # Sort by name (optional)
    result.sort(key=lambda x: x.get('name', ''))
    return jsonify(result), 200

@bp.route('/<team_id>', methods=['GET'])
def get_team(team_id):
    """Fetch a team by ID, returns a 404 if not found in either table."""
    team = NationalTeam.query.get(team_id)
    if team:
        d = team.to_dict()
        d['type'] = 'national'
        return jsonify(d), 200

    team = Club.query.get(team_id)
    if team:
        d = team.to_dict()
        d['type'] = 'club'
        return jsonify(d), 200

    abort(404, "Team not found")