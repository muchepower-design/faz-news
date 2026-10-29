from flask import Blueprint, request, jsonify
from app.database import db
from app.models import Player

bp = Blueprint('players', __name__)

@bp.route('/', methods=['GET'])
def get_players():
    team_id = request.args.get('team_id')
    position = request.args.get('position')
    skip = int(request.args.get('skip', 0))
    limit = int(request.args.get('limit', 50))
    query = Player.query
    if team_id:
        query = query.filter_by(team_id=team_id)
    if position:
        query = query.filter_by(position=position)
    players = query.offset(skip).limit(limit).all()
    return jsonify([p.to_dict() for p in players])

@bp.route('/top-scorers', methods=['GET'])
def get_top_scorers():
    limit = int(request.args.get('limit', 10))
    players = Player.query.order_by(Player.goals.desc()).limit(limit).all()
    return jsonify([p.to_dict() for p in players])