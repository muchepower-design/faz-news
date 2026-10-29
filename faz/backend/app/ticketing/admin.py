# app/ticketing/admin.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database import db
from app.models import (
    Club, TicketType, User, Order,
    CompetitionMatch, NationalTeam, CompetitionSeason, Competition,
)
from app.auth import get_current_user, get_password_hash
from datetime import datetime

bp = Blueprint('ticketing_admin', __name__, url_prefix='/api/ticketing/admin')


def admin_required(f):
    from functools import wraps

    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or user.role not in ['admin', 'super_admin', 'faz_admin']:
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)

    return decorated


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def resolve_team_name(team_id):
    if not team_id:
        return 'TBD'
    t = NationalTeam.query.get(team_id)
    if t:
        return t.name
    t = Club.query.get(team_id)
    if t:
        return t.name
    return 'Unknown'


def get_competition_name_for_season(season_id):
    if not season_id:
        return ''
    season = CompetitionSeason.query.get(season_id)
    if not season:
        return ''
    comp = Competition.query.get(season.competition_id)
    return comp.name if comp else ''


def _upsert_ticket_types(match, incoming_list):
    from app.models import StadiumSection, Ticket

    existing_map = {tt.id: tt for tt in (match.ticket_types or [])}
    kept_ids = set()

    for item in incoming_list:
        name = (item.get('name') or '').strip()
        price = item.get('price')
        capacity = item.get('capacity')

        if not name or price in (None, ''):
            continue
        try:
            price = float(price)
        except (TypeError, ValueError):
            continue

        tt_id = item.get('id')
        if tt_id and tt_id in existing_map:
            tt = existing_map[tt_id]
            tt.name = name
            tt.price = price
            kept_ids.add(tt_id)
        else:
            tt = TicketType(
                match_id=match.id,
                name=name,
                price=price,
                capacity=int(capacity) if capacity not in (None, '') else 1,  # temporary
            )
            db.session.add(tt)
            db.session.flush()
            kept_ids.add(tt.id)

        # Sections
        if isinstance(item.get('sections'), list):
            error = _upsert_sections_for_type(match, tt, item['sections'])
            if error:
                return error

        # ⬇️ Derive capacity from sections
        section_total = sum(
            (s.rows or 0) * (s.seats_per_row or 0)
            for s in StadiumSection.query.filter_by(
                match_id=match.id, ticket_type_id=tt.id
            ).all()
        )
        if section_total > 0:
            tt.capacity = section_total
        elif capacity not in (None, ''):
            tt.capacity = int(capacity)
        # else: keep existing capacity

    for tt in list(match.ticket_types):
        if tt.id in kept_ids:
            continue
        sold = getattr(tt, 'tickets_sold', 0) or 0
        if sold > 0:
            return f"Cannot remove ticket type '{tt.name}': {sold} sold"
        db.session.delete(tt)

    return None

def _upsert_sections_for_type(match, ticket_type, incoming):
    """
    Replace all sections for one ticket type. Caller is responsible for commit.

    Each section may carry:
        {
            name: str,
            side: 'north' | 'east' | 'south' | 'west' | None,  # compass position
            deck: str | None,
            rows: int,
            seats_per_row: int,
            section_order: int (optional)
        }
    """
    from app.models import StadiumSection, Ticket

    existing = StadiumSection.query.filter_by(
        match_id=match.id,
        ticket_type_id=ticket_type.id,
    ).all()
    existing_by_name = {s.name: s for s in existing}
    incoming_names = set()

    for idx, s in enumerate(incoming or []):
        name = (s.get('name') or '').strip()
        if not name:
            continue
        incoming_names.add(name)

        side = (s.get('side') or '').strip().lower() or None
        if side not in (None, 'north', 'east', 'south', 'west'):
            side = None

        deck = (s.get('deck') or '').strip() or None
        rows = int(s.get('rows') or 0)
        seats_per_row = int(s.get('seats_per_row') or 0)
        order = int(s.get('section_order') or idx)

        if name in existing_by_name:
            sec = existing_by_name[name]
            sec.side = side
            sec.deck = deck
            sec.rows = rows
            sec.seats_per_row = seats_per_row
            sec.section_order = order
        else:
            db.session.add(StadiumSection(
                match_id=match.id,
                ticket_type_id=ticket_type.id,
                name=name,
                side=side,
                deck=deck,
                rows=rows,
                seats_per_row=seats_per_row,
                section_order=order,
            ))

    # Delete removed sections (only if nothing sold in them)
    for old in existing:
        if old.name in incoming_names:
            continue
        sold = Ticket.query.filter_by(
            match_id=match.id,
            section=old.name,
            ticket_type_id=ticket_type.id,
        ).count()
        if sold > 0:
            return (
                f"Cannot remove section '{old.name}': "
                f"{sold} ticket(s) have already been sold in it"
            )
        db.session.delete(old)

    return None

# ----------------------------------------------------------------------
# Clubs
# ----------------------------------------------------------------------
@bp.route('/clubs', methods=['POST'])
@admin_required
def create_club():
    data = request.get_json()
    club = Club(
        name=data['name'],
        short_name=data.get('short_name'),
        logo_url=data.get('logo_url'),
        description=data.get('description')
    )
    db.session.add(club)
    db.session.commit()
    return jsonify(club.to_dict()), 201


@bp.route('/clubs/<club_id>', methods=['PUT'])
@admin_required
def update_club(club_id):
    club = Club.query.get_or_404(club_id)
    data = request.get_json()
    for field in ['name', 'short_name', 'logo_url', 'description', 'is_active']:
        if field in data:
            setattr(club, field, data[field])
    db.session.commit()
    return jsonify(club.to_dict()), 200


@bp.route('/clubs/<club_id>', methods=['DELETE'])
@admin_required
def delete_club(club_id):
    club = Club.query.get_or_404(club_id)
    club.is_active = False
    db.session.commit()
    return jsonify({'message': 'Club deactivated'}), 200


# ----------------------------------------------------------------------
# Matches (ticketing)
# ----------------------------------------------------------------------
@bp.route('/matches', methods=['POST'])
@admin_required
def create_match():
    data = request.get_json() or {}
    competition_match_id = data.get('competition_match_id')

    if not competition_match_id:
        return jsonify({
            "error": "Missing 'competition_match_id'. Ticketing must reference an existing CompetitionMatch."
        }), 400

    cm = CompetitionMatch.query.get(competition_match_id)
    if not cm:
        return jsonify({"error": "Competition match not found"}), 404

    if not cm.is_ticketed:
        cm.is_ticketed = True

    error = _upsert_ticket_types(cm, data.get('ticket_types') or [])
    if error:
        db.session.rollback()
        return jsonify({"error": error}), 400

    db.session.commit()
    return jsonify(cm.to_dict()), 201


@bp.route('/matches/<match_id>', methods=['PUT'])
@admin_required
def update_match(match_id):
    cm = CompetitionMatch.query.get_or_404(match_id)
    data = request.get_json() or {}

    if 'ticket_types' in data:
        error = _upsert_ticket_types(cm, data['ticket_types'])
        if error:
            db.session.rollback()
            return jsonify({"error": error}), 400

    db.session.commit()
    db.session.refresh(cm)
    return jsonify(cm.to_dict()), 200


@bp.route('/matches/<match_id>', methods=['DELETE'])
@admin_required
def delete_match(match_id):
    from app.models import StadiumSection

    cm = CompetitionMatch.query.get_or_404(match_id)

    for tt in list(cm.ticket_types or []):
        sold = getattr(tt, 'tickets_sold', 0) or 0
        if sold > 0:
            return jsonify({
                "error": f"Cannot remove ticketing: '{tt.name}' has already sold {sold} ticket(s)"
            }), 400
        db.session.delete(tt)

    for sec in StadiumSection.query.filter_by(match_id=cm.id).all():
        db.session.delete(sec)

    cm.is_ticketed = False
    db.session.commit()
    return jsonify({'message': 'Ticketing removed for match'}), 200


@bp.route('/matches/<match_id>/sections', methods=['GET'])
@admin_required
def list_sections(match_id):
    from app.models import StadiumSection
    sections = (
        StadiumSection.query
        .filter_by(match_id=match_id)
        .order_by(StadiumSection.section_order.asc(), StadiumSection.name.asc())
        .all()
    )
    return jsonify([s.to_dict() for s in sections]), 200


# ----------------------------------------------------------------------
# Roles
# ----------------------------------------------------------------------
@bp.route('/roles', methods=['GET'])
@admin_required
def list_roles():
    from app.models import Role
    roles = Role.query.order_by(Role.name.asc()).all()
    return jsonify([r.to_dict() for r in roles]), 200


# ----------------------------------------------------------------------
# Users
# ----------------------------------------------------------------------
@bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    users = User.query.all()
    return jsonify([u.to_dict() for u in users]), 200


@bp.route('/users', methods=['POST'])
@admin_required
def create_user():
    from app.models import Role

    data = request.get_json() or {}

    email = (data.get('email') or '').strip().lower()
    if not email:
        return jsonify({'error': 'Email is required'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'A user with that email already exists'}), 409

    # Roles come in as an array of role names (frontend sends ["club_admin", ...])
    role_names = data.get('roles') or []
    if not isinstance(role_names, list):
        role_names = [role_names] if role_names else []
    role_names = [r for r in role_names if r]

    primary_role = role_names[0] if role_names else data.get('role', 'viewer')

    first = (data.get('first_name') or '').strip()
    last = (data.get('last_name') or '').strip()

    user = User(
        email=email,
        username=email,
        first_name=first or None,
        last_name=last or None,
        full_name=f"{first} {last}".strip() or None,
        phone=data.get('phone') or None,
        role=primary_role,
        club_id=data.get('club_id') or None,
        is_active=True,
    )
    user.hashed_password = get_password_hash(data['password'])

    # Attach Role rows
    if role_names:
        roles = Role.query.filter(Role.name.in_(role_names)).all()
        user.roles = roles
        # Ensure the legacy column reflects the primary role even if the
        # provided primary_role wasn't in the DB yet (shouldn't happen).

    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201


@bp.route('/users/<user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    from app.models import Role

    user = User.query.get_or_404(user_id)
    data = request.get_json() or {}

    for field in ['email', 'first_name', 'last_name', 'full_name', 'phone']:
        if field in data and hasattr(user, field):
            val = data[field]
            if isinstance(val, str):
                val = val.strip() or None
            setattr(user, field, val)

    if 'club_id' in data:
        user.club_id = data['club_id'] or None

    if 'is_active' in data:
        user.is_active = data['is_active']

    if data.get('password'):
        user.hashed_password = get_password_hash(data['password'])

    # Update roles if provided
    if 'roles' in data:
        role_names = data['roles'] if isinstance(data['roles'], list) else [data['roles']]
        role_names = [r for r in role_names if r]

        if role_names:
            roles = Role.query.filter(Role.name.in_(role_names)).all()
            user.roles = roles
            user.role = role_names[0]
        else:
            user.roles = []
            # Leave user.role as the last known value rather than clobbering it

    db.session.commit()
    return jsonify(user.to_dict()), 200

# ----------------------------------------------------------------------
# Orders
# ----------------------------------------------------------------------
@bp.route('/orders', methods=['GET'])
@admin_required
def get_all_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return jsonify([o.to_dict() for o in orders]), 200


@bp.route('/orders/<order_id>', methods=['GET'])
@admin_required
def get_order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    return jsonify(order.to_dict()), 200