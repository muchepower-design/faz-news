# app/routes/clubs.py
from flask import Blueprint, request, jsonify, abort
from flask_jwt_extended import jwt_required
from app.database import db
from app.models import Club, Country
from app.auth import admin_required

bp = Blueprint('clubs', __name__)


@bp.route('/', methods=['GET'])
def list_clubs():
    skip = int(request.args.get('skip', 0))
    limit = int(request.args.get('limit', 500))
    q = Club.query.order_by(Club.name.asc())
    clubs = q.offset(skip).limit(limit).all()
    return jsonify([c.to_dict() for c in clubs]), 200


@bp.route('/<club_id>', methods=['GET'])
def get_club(club_id):
    c = Club.query.get_or_404(club_id)
    return jsonify(c.to_dict()), 200


@bp.route('/', methods=['POST'])
@jwt_required()
@admin_required
def create_club():
    data = request.get_json() or {}

    name = (data.get('name') or '').strip()
    country_id = data.get('country_id')

    if not name or not country_id:
        abort(400, "name and country_id are required")

    country = Country.query.get(country_id)
    if not country:
        abort(404, "Country not found")

    existing = Club.query.filter_by(name=name).first()
    if existing:
        abort(409, "A club with that name already exists")

    club = Club(
        name=name,
        short_name=data.get('short_name'),
        age=data.get('age'),
        gender=data.get('gender') or 'male',
        logo_url=data.get('logo_url'),
        description=data.get('description'),
        is_active=data.get('is_active', True),
        country_id=country.id,
    )
    db.session.add(club)
    db.session.commit()
    return jsonify(club.to_dict()), 201


@bp.route('/<club_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_club(club_id):
    club = Club.query.get_or_404(club_id)
    data = request.get_json() or {}

    for field in ['name', 'short_name', 'age', 'gender', 'logo_url',
                  'description', 'is_active']:
        if field in data:
            setattr(club, field, data[field])

    if 'country_id' in data and data['country_id']:
        country = Country.query.get(data['country_id'])
        if not country:
            abort(404, "Country not found")
        club.country_id = country.id

    db.session.commit()
    return jsonify(club.to_dict()), 200


@bp.route('/<club_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_club(club_id):
    club = Club.query.get_or_404(club_id)
    db.session.delete(club)
    db.session.commit()
    return jsonify({'message': 'Club deleted'}), 200