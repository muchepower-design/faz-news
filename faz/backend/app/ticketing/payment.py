# app/ticketing/payment.py
from flask import Blueprint, request, jsonify
from app.database import db
from app.models import Order, Ticket, TicketType
import os
import uuid
import requests
from datetime import datetime

bp = Blueprint('ticketing_payment', __name__, url_prefix='/api/ticketing/payment')

PAWAPAY_API_KEY = os.environ.get('PAWAPAY_API_KEY', 'your-api-key-here')
PAWAPAY_BASE_URL = "https://api.pawapay.io/v2"


def get_pawapay_headers():
    return {
        "Authorization": f"Bearer {PAWAPAY_API_KEY}",
        "Content-Type": "application/json"
    }


@bp.route('/providers', methods=['GET'])
def get_providers():
    try:
        resp = requests.get(
            f"{PAWAPAY_BASE_URL}/availability",
            headers=get_pawapay_headers(),
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            providers = []
            for country in data:
                if country.get('country') == 'ZMB':
                    for prov in country.get('providers', []):
                        deposit_status = prov.get('operationTypes', {}).get('DEPOSIT', 'CLOSED')
                        providers.append({
                            'provider': prov['provider'],
                            'name': prov['provider'].replace('_ZMB', '').replace('_OAPI_ZMB', '').replace('MOMO', ' Mobile Money'),
                            'country': 'ZMB',
                            'deposit_operational': deposit_status == 'OPERATIONAL'
                        })
            return jsonify(providers), 200
        else:
            return jsonify({'error': 'Failed to fetch providers'}), 502
    except requests.exceptions.RequestException:
        return jsonify({'error': 'Service temporarily unavailable'}), 503


@bp.route('/deposit', methods=['POST'])
def initiate_deposit():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    order_id = data.get('order_id')
    provider = data.get('provider')
    phone_number = data.get('phone_number')
    amount = data.get('amount')
    customer_email = data.get('customer_email')

    if not all([order_id, provider, phone_number, amount]):
        return jsonify({'error': 'Missing required parameters'}), 400

    order = Order.query.get(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404

    if order.payment_status != 'pending':
        return jsonify({'error': 'Order is already paid or cancelled'}), 400

    deposit_id = str(uuid.uuid4())
    client_ref = f"FAZ-{order.id}-{uuid.uuid4().hex[:6].upper()}"

    payload = {
        "depositId": deposit_id,
        "payer": {
            "type": "MMO",
            "accountDetails": {
                "phoneNumber": phone_number,
                "provider": provider
            }
        },
        "amount": str(amount),
        "currency": "ZMW",
        "clientReferenceId": client_ref,
        "customerMessage": f"FAZ Order"[:22],
        "metadata": [
            {"orderId": str(order.id)},
            {"customerId": customer_email or order.customer_email, "isPII": True}
        ]
    }

    try:
        resp = requests.post(
            f"{PAWAPAY_BASE_URL}/deposits",
            json=payload,
            headers=get_pawapay_headers(),
            timeout=30
        )
        pawa_resp = resp.json()

        if resp.status_code == 200:
            status = pawa_resp.get('status')
            if status in ['ACCEPTED', 'DUPLICATE_IGNORED']:
                order.payment_reference = pawa_resp.get('depositId', deposit_id)
                order.payment_method = provider
                db.session.commit()
                return jsonify({
                    'success': True,
                    'depositId': order.payment_reference,
                    'message': 'Payment request sent. Please check your phone to approve.'
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'status': status,
                    'failureReason': pawa_resp.get('failureReason')
                }), 200
        else:
            return jsonify({
                'success': False,
                'status': pawa_resp.get('status', 'ERROR'),
                'failureReason': pawa_resp.get('failureReason'),
                'http_status': resp.status_code
            }), 200
    except requests.exceptions.RequestException:
        return jsonify({'error': 'Payment service unavailable'}), 503


@bp.route('/deposit/<deposit_id>/check', methods=['GET'])
def check_deposit_status(deposit_id):
    order = Order.query.filter_by(payment_reference=deposit_id).first()
    if not order:
        return jsonify({'error': 'Deposit not found'}), 404

    if order.payment_status == 'paid':
        return jsonify({
            'success': True,
            'status': 'COMPLETED',
            'message': 'Payment already completed.'
        }), 200

    try:
        resp = requests.get(
            f"{PAWAPAY_BASE_URL}/deposits/{deposit_id}",
            headers=get_pawapay_headers(),
            timeout=10
        )
        data = resp.json()

        if resp.status_code == 200:
            status = data.get('status')
            deposit_data = data.get('data') if status == 'FOUND' else None

            if status == 'FOUND' and deposit_data:
                deposit_status = deposit_data.get('status')

                if deposit_status == 'COMPLETED':
                    for item in order.items:
                        ticket_type = TicketType.query.get(item.ticket_type_id)
                        if not ticket_type:
                            order.payment_status = 'failed'
                            db.session.commit()
                            return jsonify({
                                'success': False,
                                'status': 'FAILED',
                                'failureReason': {'failureMessage': 'Ticket type missing'}
                            }), 200

                        available = ticket_type.capacity - ticket_type.tickets_sold
                        if item.quantity > available:
                            order.payment_status = 'failed'
                            db.session.commit()
                            return jsonify({
                                'success': False,
                                'status': 'FAILED',
                                'failureReason': {'failureMessage': f'Only {available} tickets available'}
                            }), 200

                        # Seat fields carried from the OrderItem
                        seat_section = getattr(item, 'section', None)
                        seat_row = getattr(item, 'row', None)
                        seat_number = getattr(item, 'seat', None)

                        for idx in range(item.quantity):
                            # If a specific seat was recorded and this is
                            # a single-seat line, stamp it on the ticket.
                            # Multi-quantity lines with one seat are unusual;
                            # blank the seat for those to avoid duplicates.
                            this_section = seat_section if item.quantity == 1 else None
                            this_row     = seat_row     if item.quantity == 1 else None
                            this_seat    = seat_number  if item.quantity == 1 else None

                            ticket = Ticket(
                                ticket_number=str(uuid.uuid4()),
                                order_item_id=item.id,
                                match_id=ticket_type.match_id,
                                ticket_type_id=ticket_type.id,
                                section=this_section,
                                row=this_row,
                                seat=this_seat,
                            )
                            ticket.generate_qr_code()
                            db.session.add(ticket)

                        ticket_type.tickets_sold += item.quantity
                        db.session.add(ticket_type)

                    order.payment_status = 'paid'
                    db.session.commit()
                    return jsonify({
                        'success': True,
                        'status': 'COMPLETED',
                        'message': 'Payment completed. Tickets generated.'
                    }), 200

                elif deposit_status == 'FAILED':
                    order.payment_status = 'failed'
                    db.session.commit()
                    return jsonify({
                        'success': False,
                        'status': 'FAILED',
                        'failureReason': deposit_data.get('failureReason')
                    }), 200

                elif deposit_status in ['ACCEPTED', 'PROCESSING', 'IN_RECONCILIATION']:
                    return jsonify({
                        'success': True,
                        'status': deposit_status,
                        'message': 'Payment still pending'
                    }), 200

                else:
                    return jsonify({'success': False, 'status': 'UNKNOWN'}), 200

            elif status == 'NOT_FOUND':
                order.payment_status = 'failed'
                db.session.commit()
                return jsonify({'success': False, 'status': 'NOT_FOUND'}), 200

            else:
                return jsonify({'success': False, 'status': 'UNKNOWN'}), 200

        else:
            return jsonify({
                'success': False,
                'status': 'ERROR',
                'failureReason': data.get('failureReason')
            }), 502

    except requests.exceptions.RequestException:
        return jsonify({'error': 'Payment service unavailable'}), 503