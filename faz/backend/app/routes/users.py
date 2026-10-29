from flask import Blueprint, request, jsonify, abort
from flask_jwt_extended import jwt_required
from app.database import db
from app.models import User
from app.schemas import UserCreate
from app.auth import get_current_user, admin_required, get_password_hash

bp = Blueprint('users', __name__)

@bp.route('/', methods=['GET'])
@jwt_required()
def get_users():
    user = get_current_user()
    if user.role != 'admin':
        abort(403)
    skip = int(request.args.get('skip', 0))
    limit = int(request.args.get('limit', 100))
    users = User.query.offset(skip).limit(limit).all()
    return jsonify([u.to_dict() for u in users])

@bp.route('/', methods=['POST'])
@jwt_required()
def create_user():
    user = get_current_user()
    if user.role != 'admin':
        abort(403)
    data = request.get_json()
    existing = User.query.filter((User.username == data['username']) | (User.email == data['email'])).first()
    if existing:
        abort(400, "Username or email already exists")
    hashed = get_password_hash(data['password'])
    new_user = User(
        username=data['username'],
        email=data['email'],
        hashed_password=hashed,
        full_name=data['full_name'],
        role=data.get('role', 'viewer'),
        club_id=data.get('club_id')
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"id": str(new_user.id)}), 201

@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user_info():
    user = get_current_user()
    return jsonify(user.to_dict())