# app/ticketing/api.py
from flask import Blueprint, jsonify, request
from flask_jwt_extended import decode_token
from app.database import db
from app.models import (
    CompetitionMatch, Club, TicketType, Order, OrderItem, Ticket, SeatHold, User,
    CompetitionSeason, Competition,
)
from datetime import datetime, timedelta
import uuid

bp = Blueprint('ticketing_api', __name__, url_prefix='/api/ticketing')


def _enrich(m):
    d = m.to_dict()
    match_type = 'club'
    if m.season_id:
        s = CompetitionSeason.query.get(m.season_id)
        if s:
            c = Competition.query.get(s.competition_id)
            if c:
                d['competition'] = c.name
                d['competition_id'] = str(c.id)
                name = (c.name or '').lower()
                if 'national' in name or 'international' in name or c.participant_type == 'countries':
                    match_type = 'national'
    d['match_type'] = match_type
    return d


def clean_expired_holds():
    now = datetime.utcnow()
    expired = SeatHold.query.filter(SeatHold.expires_at < now).all()
    if expired:
        for h in expired:
            db.session.delete(h)
        db.session.commit()


def _ensure_ticket_images(order):
    if not order:
        return
    try:
        from app.utils.ticket_generator import generate_order_tickets
        generate_order_tickets(order)
    except Exception as e:
        print(f"[orders] ticket generation failed for order "
              f"{getattr(order, 'id', '?')}: {e}")


@bp.route('/clubs', methods=['GET'])
def get_clubs():
    active_only = request.args.get('active_only', 'true').lower() == 'true'
    query = Club.query
    if active_only:
        query = query.filter_by(is_active=True)
    return jsonify([c.to_dict() for c in query.all()]), 200


@bp.route('/clubs/<club_id>', methods=['GET'])
def get_club(club_id):
    club = Club.query.get_or_404(club_id)
    return jsonify(club.to_dict()), 200


@bp.route('/matches', methods=['GET'])
def get_matches():
    match_type_filter = request.args.get('type')
    club_id = request.args.get('club_id')
    active_only = request.args.get('active_only', 'true').lower() == 'true'

    q = CompetitionMatch.query.filter(CompetitionMatch.is_ticketed.is_(True))

    if club_id:
        q = q.filter(
            (CompetitionMatch.home_team_id == club_id) |
            (CompetitionMatch.away_team_id == club_id)
        )
    if active_only:
        q = q.filter(CompetitionMatch.status != 'finished')

    matches = q.order_by(CompetitionMatch.match_date.asc()).all()
    out = [_enrich(m) for m in matches]

    if match_type_filter in ('national', 'club'):
        out = [m for m in out if m.get('match_type') == match_type_filter]

    return jsonify(out), 200


@bp.route('/matches/<match_id>', methods=['GET'])
def get_match(match_id):
    clean_expired_holds()
    m = CompetitionMatch.query.get_or_404(match_id)
    if not m.is_ticketed:
        return jsonify({'error': 'Match is not ticketed'}), 404
    return jsonify(_enrich(m)), 200


@bp.route('/matches/<match_id>/ticket-types', methods=['GET'])
def get_match_ticket_types(match_id):
    m = CompetitionMatch.query.get_or_404(match_id)
    if not m.is_ticketed:
        return jsonify({'error': 'Match is not ticketed'}), 404
    return jsonify([tt.to_dict() for tt in m.ticket_types]), 200


# ----------------------------------------------------------------------
# Seat map (public) — grouped by ticket type
# ----------------------------------------------------------------------
@bp.route('/matches/<match_id>/seat-map', methods=['GET'])
def get_seat_map(match_id):
    from app.models import StadiumSection

    m = CompetitionMatch.query.get(match_id)
    if not m:
        return jsonify({'error': 'Match not found'}), 404

    sections = (
        StadiumSection.query
        .filter_by(match_id=match_id)
        .order_by(StadiumSection.section_order.asc(), StadiumSection.name.asc())
        .all()
    )

    if not sections:
        return jsonify({'has_sections': False, 'ticket_types': []}), 200

    # Pre-compute sold and held lookups
    sold_map = {}
    for t in Ticket.query.filter_by(match_id=match_id).all():
        if not t.section:
            continue
        key = (t.section, t.row or '', t.seat or '')
        sold_map[key] = True

    now = datetime.utcnow()
    held_map = {}
    for h in SeatHold.query.filter(
        SeatHold.match_id == match_id,
        SeatHold.expires_at > now,
    ).all():
        if not h.section:
            continue
        key = (h.section, h.row or '', h.seat or '')
        held_map[key] = True

    def build_rows_for_section(sec):
        rows_out = []
        for r_idx in range(sec.rows):
            row_label = chr(ord('A') + r_idx) if r_idx < 26 else f'R{r_idx + 1}'
            seats_out = []
            for seat_n in range(1, sec.seats_per_row + 1):
                seat_label = str(seat_n)
                key = (sec.name, row_label, seat_label)
                if key in sold_map:
                    status = 'sold'
                elif key in held_map:
                    status = 'held'
                else:
                    status = 'available'
                seats_out.append({'seat': seat_label, 'status': status})
            rows_out.append({'label': row_label, 'seats': seats_out})
        return rows_out

    # Group sections by ticket type
    tt_ids = []
    seen = set()
    for s in sections:
        if s.ticket_type_id and s.ticket_type_id not in seen:
            tt_ids.append(s.ticket_type_id)
            seen.add(s.ticket_type_id)

    ticket_type_payload = []
    for tt_id in tt_ids:
        tt = TicketType.query.get(tt_id)
        if not tt:
            continue
        tt_sections = [s for s in sections if s.ticket_type_id == tt_id]
        ticket_type_payload.append({
            'id': str(tt.id),
            'name': tt.name,
            'price': float(tt.price),
            'capacity': tt.capacity,
            'tickets_sold': tt.tickets_sold,
            'sections': [
                {
                    **s.to_dict(),
                    'rows_detail': build_rows_for_section(s),
                }
                for s in tt_sections
            ],
        })

    return jsonify({
        'has_sections': True,
        'ticket_types': ticket_type_payload,
    }), 200


# ----------------------------------------------------------------------
# Holds
# ----------------------------------------------------------------------
@bp.route('/matches/<match_id>/hold', methods=['POST'])
def hold_tickets(match_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    ticket_type_id = data.get('ticket_type_id')
    try:
        quantity = int(data.get('quantity', 0))
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid quantity'}), 400

    hold_token = data.get('hold_token')
    section = (data.get('section') or '').strip() or None
    row_label = (data.get('row') or '').strip() or None
    seat_label = (data.get('seat') or '').strip() or None

    clean_expired_holds()

    try:
        match_uuid = uuid.UUID(match_id)
    except ValueError:
        return jsonify({'error': 'Invalid match ID format'}), 400

    match = CompetitionMatch.query.get(match_uuid)
    if not match:
        return jsonify({'error': 'Match not found'}), 404
    if not match.is_ticketed:
        return jsonify({'error': 'Match is not ticketed'}), 400

    try:
        tt_uuid = uuid.UUID(ticket_type_id)
    except ValueError:
        return jsonify({'error': 'Invalid ticket type ID format'}), 400

    ticket_type = TicketType.query.get(tt_uuid)
    if not ticket_type:
        return jsonify({'error': 'Ticket type not found'}), 404
    if ticket_type.match_id != match_uuid:
        return jsonify({'error': 'Ticket type does not belong to this match'}), 404

    current_hold = None
    if hold_token:
        current_hold = SeatHold.query.filter_by(hold_token=hold_token).first()

    if section and row_label and seat_label:
        conflict_q = SeatHold.query.filter(
            SeatHold.match_id == match_uuid,
            SeatHold.section == section,
            SeatHold.row == row_label,
            SeatHold.seat == seat_label,
            SeatHold.expires_at > datetime.utcnow(),
        )
        if current_hold:
            conflict_q = conflict_q.filter(SeatHold.id != current_hold.id)
        if conflict_q.first():
            return jsonify({
                'error': 'Seat already held by another shopper',
                'seat_status': 'held',
            }), 409

        already_sold = Ticket.query.filter_by(
            match_id=match_uuid, section=section, row=row_label, seat=seat_label
        ).first()
        if already_sold:
            return jsonify({
                'error': 'Seat already sold',
                'seat_status': 'sold',
            }), 409

    query = db.session.query(db.func.sum(SeatHold.quantity)).filter(
        SeatHold.ticket_type_id == tt_uuid
    )
    if current_hold:
        query = query.filter(SeatHold.id != current_hold.id)
    held_by_others = query.scalar() or 0

    available = ticket_type.capacity - ticket_type.tickets_sold - held_by_others
    if quantity > available:
        return jsonify({
            'error': f'Only {available} seats available',
            'available': available,
        }), 409

    if current_hold:
        current_hold.quantity = quantity
        current_hold.section = section
        current_hold.row = row_label
        current_hold.seat = seat_label
        current_hold.expires_at = datetime.utcnow() + timedelta(minutes=10)
        db.session.commit()
        return jsonify({
            'hold_token': current_hold.hold_token,
            'quantity': quantity,
            'available': available - quantity,
            'section': section,
            'row': row_label,
            'seat': seat_label,
        }), 200

    if quantity == 0:
        return jsonify({'error': 'Quantity must be positive'}), 400

    new_hold = SeatHold(
        match_id=match_uuid,
        ticket_type_id=tt_uuid,
        quantity=quantity,
        section=section,
        row=row_label,
        seat=seat_label,
        expires_at=datetime.utcnow() + timedelta(minutes=10),
    )
    db.session.add(new_hold)
    db.session.commit()
    return jsonify({
        'hold_token': new_hold.hold_token,
        'quantity': quantity,
        'available': available - quantity,
        'section': section,
        'row': row_label,
        'seat': seat_label,
    }), 201


@bp.route('/matches/<match_id>/hold/<hold_token>', methods=['DELETE'])
def release_hold(match_id, hold_token):
    hold = SeatHold.query.filter_by(hold_token=hold_token, match_id=match_id).first()
    if not hold:
        return jsonify({'error': 'Hold not found'}), 404
    db.session.delete(hold)
    db.session.commit()
    return jsonify({'message': 'Hold released'}), 200


# ----------------------------------------------------------------------
# Orders
# ----------------------------------------------------------------------
@bp.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    user_id = None
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        try:
            decoded = decode_token(auth_header.split(' ')[1])
            user_id = decoded['sub']
        except Exception:
            pass

    customer_email = data.get('customer_email')
    customer_name = data.get('customer_name')
    customer_phone = data.get('customer_phone')
    items = data.get('items', [])
    hold_tokens = data.get('hold_tokens', [])

    if not customer_email or not items:
        return jsonify({'error': 'Email and items required'}), 400

    with db.session.begin_nested():
        total = 0
        order_items = []
        for item in items:
            ticket_type_id = item.get('ticket_type_id')
            quantity = item.get('quantity')
            if not ticket_type_id or not quantity or quantity <= 0:
                db.session.rollback()
                return jsonify({'error': 'Invalid item data'}), 400

            try:
                tt_uuid = uuid.UUID(ticket_type_id)
            except ValueError:
                db.session.rollback()
                return jsonify({'error': 'Invalid ticket type ID'}), 400

            ticket_type = (
                db.session.query(TicketType)
                .filter(TicketType.id == tt_uuid)
                .with_for_update()
                .one_or_none()
            )
            if not ticket_type:
                db.session.rollback()
                return jsonify({'error': f'Ticket type {ticket_type_id} not found'}), 404

            available = ticket_type.capacity - ticket_type.tickets_sold
            if quantity > available:
                db.session.rollback()
                return jsonify({
                    'error': f'Only {available} tickets available for {ticket_type.name}'
                }), 400

            section = (item.get('section') or '').strip() or None
            row_label = (item.get('row') or '').strip() or None
            seat_label = (item.get('seat') or '').strip() or None

            if section and row_label and seat_label:
                already = Ticket.query.filter_by(
                    match_id=ticket_type.match_id,
                    section=section, row=row_label, seat=seat_label,
                ).first()
                if already:
                    db.session.rollback()
                    return jsonify({
                        'error': f'Seat {section} {row_label}-{seat_label} is already sold'
                    }), 409

            total += float(ticket_type.price) * quantity
            order_items.append({
                'ticket_type': ticket_type,
                'quantity': quantity,
                'price': float(ticket_type.price),
                'section': section,
                'row': row_label,
                'seat': seat_label,
            })
            ticket_type.tickets_sold += quantity
            db.session.add(ticket_type)

        order = Order(
            user_id=user_id,
            customer_email=customer_email,
            customer_name=customer_name,
            customer_phone=customer_phone,
            total_amount=total,
            payment_status='pending',
            payment_method='demo',
        )
        db.session.add(order)
        db.session.flush()

        for item in order_items:
            db.session.add(OrderItem(
                order_id=order.id,
                ticket_type_id=item['ticket_type'].id,
                quantity=item['quantity'],
                unit_price=item['ticket_type'].price,
                section=item['section'],
                row=item['row'],
                seat=item['seat'],
            ))

        for token in hold_tokens:
            hold = SeatHold.query.filter_by(hold_token=token).first()
            if hold:
                db.session.delete(hold)

    db.session.commit()
    return jsonify(order.to_dict()), 201


@bp.route('/orders/<order_id>/cancel', methods=['POST'])
def cancel_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.payment_status != 'pending':
        return jsonify({'error': 'Only pending orders can be cancelled'}), 400

    for item in order.items:
        tt = TicketType.query.get(item.ticket_type_id)
        if tt:
            tt.tickets_sold = max(0, tt.tickets_sold - item.quantity)
            db.session.add(tt)
        db.session.delete(item)

    db.session.delete(order)
    db.session.commit()
    return jsonify({'message': 'Order cancelled'}), 200


@bp.route('/orders/by-number/<order_number>', methods=['GET'])
def get_order_by_number(order_number):
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    _ensure_ticket_images(order)
    return jsonify(order.to_dict()), 200


@bp.route('/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    order = Order.query.get_or_404(order_id)
    _ensure_ticket_images(order)
    return jsonify(order.to_dict()), 200


@bp.route('/tickets/verify', methods=['POST'])
def verify_ticket():
    data = request.get_json()
    ticket_number = data.get('ticket_number')
    if not ticket_number:
        return jsonify({'valid': False, 'message': 'Ticket number required'}), 400

    ticket = Ticket.query.filter_by(ticket_number=ticket_number).first()
    if not ticket:
        return jsonify({'valid': False, 'message': 'Ticket not found'}), 404
    if ticket.is_used:
        return jsonify({'valid': False, 'message': 'Ticket already used'}), 400

    ticket.is_used = True
    ticket.used_at = db.func.now()
    db.session.commit()

    return jsonify({
        'valid': True,
        'ticket': ticket.to_dict(),
        'match': ticket.match.to_dict() if ticket.match else None,
    }), 200


@bp.route('/tickets/<ticket_number>', methods=['GET'])
def get_ticket(ticket_number):
    ticket = Ticket.query.filter_by(ticket_number=ticket_number).first_or_404()
    return jsonify(ticket.to_dict()), 200


@bp.route('/debug/ticket-types', methods=['GET'])
def debug_ticket_types():
    result = []
    for tt in TicketType.query.all():
        m = CompetitionMatch.query.get(tt.match_id)
        result.append({
            'ticket_type_id': str(tt.id),
            'match_id': str(tt.match_id),
            'match_home': m.home_team if m else None,
            'name': tt.name,
        })
    return jsonify(result)


@bp.route('/debug/matches', methods=['GET'])
def debug_matches():
    matches = CompetitionMatch.query.filter(CompetitionMatch.is_ticketed.is_(True)).all()
    return jsonify([{
        'id': str(m.id),
        'home_team': m.home_team,
        'away_team': m.away_team,
        'ticket_types': [{'id': str(tt.id), 'name': tt.name} for tt in m.ticket_types],
    } for m in matches]), 200