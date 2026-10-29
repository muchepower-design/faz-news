# app/ticketing/club.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database import db
from app.models import User, Club, CompetitionMatch, TicketType
from datetime import datetime

bp = Blueprint('ticketing_club', __name__, url_prefix='/api/ticketing/club')


def club_access_required(f):
    from functools import wraps

    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 401
        if user.role in ['admin', 'super_admin', 'faz_admin', 'club_admin', 'club_officer']:
            return f(*args, **kwargs)
        return jsonify({'error': 'Access denied'}), 403

    return decorated


def _club_matches(club_id):
    """Every CompetitionMatch where the club is either side."""
    return CompetitionMatch.query.filter(
        (CompetitionMatch.home_team_id == club_id) |
        (CompetitionMatch.away_team_id == club_id)
    )


@bp.route('/dashboard', methods=['GET'])
@club_access_required
def dashboard():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user.role in ['admin', 'super_admin', 'faz_admin']:
        club = Club.query.filter_by(is_active=True).first()
    else:
        club = Club.query.get(user.club_id)
        if not club:
            return jsonify({
                'club': None,
                'upcoming_matches': [],
                'total_tickets_sold': 0,
                'total_revenue': 0,
                'needs_club_assignment': True,
                'message': 'Your account is not yet linked to a club. Please contact an administrator.',
            }), 200

    if not club:
        return jsonify({
            'club': None,
            'upcoming_matches': [],
            'total_tickets_sold': 0,
            'total_revenue': 0,
            'needs_club_setup': True,
            'message': 'No active clubs found. Please create a club first.',
        }), 200

    matches = (
        _club_matches(club.id)
        .filter(CompetitionMatch.is_ticketed.is_(True))
        .filter(CompetitionMatch.status != 'finished')
        .order_by(CompetitionMatch.match_date.desc())
        .limit(5)
        .all()
    )

    total_tickets_sold = 0
    total_revenue = 0
    for match in matches:
        for tt in match.ticket_types:
            total_tickets_sold += tt.tickets_sold or 0
            total_revenue += (tt.tickets_sold or 0) * float(tt.price)

    return jsonify({
        'club': club.to_dict(),
        'upcoming_matches': [m.to_dict() for m in matches],
        'total_tickets_sold': total_tickets_sold,
        'total_revenue': total_revenue,
    }), 200


@bp.route('/matches', methods=['GET'])
@club_access_required
def get_club_matches():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user.role in ['admin', 'super_admin', 'faz_admin']:
        club_id_param = request.args.get('club_id')
        if club_id_param:
            matches = _club_matches(club_id_param).filter(
                CompetitionMatch.is_ticketed.is_(True)
            ).order_by(CompetitionMatch.match_date.desc()).all()
        else:
            matches = CompetitionMatch.query.filter(
                CompetitionMatch.is_ticketed.is_(True)
            ).order_by(CompetitionMatch.match_date.desc()).all()
    else:
        if not user.club_id:
            return jsonify([]), 200
        matches = _club_matches(user.club_id).filter(
            CompetitionMatch.is_ticketed.is_(True)
        ).order_by(CompetitionMatch.match_date.desc()).all()

    return jsonify([m.to_dict() for m in matches]), 200


@bp.route('/tickets/sales', methods=['GET'])
@club_access_required
def club_ticket_sales():
    from app.models import TicketType, OrderItem, Order
    from sqlalchemy import func

    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    club_id = user.club_id if user.role not in ['admin', 'super_admin', 'faz_admin'] else request.args.get('club_id')

    if not club_id:
        return jsonify([]), 200

    # All ticket types belonging to this club's matches
    rows = (
        db.session.query(
            TicketType.name.label('type'),
            func.coalesce(func.sum(OrderItem.quantity), 0).label('sold'),
            func.coalesce(func.sum(OrderItem.quantity * OrderItem.unit_price), 0).label('revenue'),
            CompetitionMatch.home_team_id,
            CompetitionMatch.away_team_id,
        )
        .join(OrderItem, OrderItem.ticket_type_id == TicketType.id)
        .join(CompetitionMatch, CompetitionMatch.id == TicketType.match_id)
        .filter(
            (CompetitionMatch.home_team_id == club_id) |
            (CompetitionMatch.away_team_id == club_id)
        )
        .group_by(TicketType.name, CompetitionMatch.home_team_id, CompetitionMatch.away_team_id)
        .all()
    )

    def team_name(team_id):
        from app.models import NationalTeam, Club
        t = NationalTeam.query.get(team_id) or Club.query.get(team_id)
        return t.name if t else 'TBD'

    result = [
        {
            'match': f"{team_name(r.home_team_id)} vs {team_name(r.away_team_id)}",
            'type': r.type,
            'sold': int(r.sold),
            'revenue': float(r.revenue),
        }
        for r in rows
    ]
    return jsonify(result), 200

# NOTE: I've removed `create_match` from this file. Matches are created
# via Competition Management now, not from the ticketing subsystem. If
# you still want club admins to be able to create a match here, tell me
# and I'll restore it — but it would need to create a CompetitionMatch,
# which means picking a Competition / Season / Stage, so it doesn't fit
# cleanly into the club portal anymore.