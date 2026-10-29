from flask import Blueprint, request, jsonify, abort
from flask_jwt_extended import jwt_required
from app.database import db
from app.models import MatchEvent, Match, Player
from app.schemas import MatchEventCreate
from app.auth import get_current_user

bp = Blueprint('match_events', __name__)

@bp.route('/', methods=['POST'])
@jwt_required()
def create_event():
    user = get_current_user()
    if user.role not in ['admin', 'match_commissioner']:
        abort(403)
    data = request.get_json()
    match = Match.query.get(data['match_id'])
    if not match:
        abort(404, "Match not found")
    player = Player.query.get(data['player_id'])
    if not player:
        abort(404, "Player not found")
    if data.get('related_player_id'):
        related = Player.query.get(data['related_player_id'])
        if not related:
            abort(404, "Related player not found")
    event = MatchEvent(
        match_id=data['match_id'],
        event_type=data['event_type'],
        player_id=data['player_id'],
        related_player_id=data.get('related_player_id'),
        minute=data['minute'],
        minute_added=data.get('minute_added', 0),
        description=data.get('description')
    )
    db.session.add(event)
    db.session.commit()
    return jsonify({"id": str(event.id)}), 201

@bp.route('/match/<match_id>', methods=['GET'])
def get_events(match_id):
    events = MatchEvent.query.filter_by(match_id=match_id).order_by(MatchEvent.minute).all()
    return jsonify([e.to_dict() for e in events])

@bp.route('/<event_id>', methods=['DELETE'])
@jwt_required()
def delete_event(event_id):
    user = get_current_user()
    if user.role not in ['admin', 'match_commissioner']:
        abort(403)
    event = MatchEvent.query.get(event_id)
    if not event:
        abort(404)
    db.session.delete(event)
    db.session.commit()
    return jsonify({"message": "Deleted"})