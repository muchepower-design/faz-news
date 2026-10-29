# app/routes/countries.py
from flask import Blueprint, jsonify
from app.models import Country

bp = Blueprint('countries', __name__)


@bp.route('/', methods=['GET'])
def list_countries():
    q = Country.query.order_by(Country.name.asc()).all()
    return jsonify([c.to_dict() for c in q]), 200


@bp.route('/<country_id>', methods=['GET'])
def get_country(country_id):
    c = Country.query.get_or_404(country_id)
    return jsonify(c.to_dict()), 200