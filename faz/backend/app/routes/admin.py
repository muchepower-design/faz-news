from flask import Blueprint, request, jsonify, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database import db
from app.models import User, UserRole, News, Match, Player, NationalTeam, Club
from app.schemas import UserCreate, NewsCreate, MatchCreate, TeamCreate, PlayerCreate
from app.auth import admin_required, get_current_user, get_password_hash
from datetime import datetime

bp = Blueprint('admin', __name__)

# ---------- User Management (Admin only) ----------
@bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def get_all_users():
    users = User.query.all()
    return jsonify([u.to_dict() for u in users])  # assuming you have to_dict, or use schemas

@bp.route('/users', methods=['POST'])
@jwt_required()
@admin_required
def create_user():
    data = request.get_json()
    # validate with schema
    # For simplicity we'll just use data directly
    existing = User.query.filter((User.username == data['username']) | (User.email == data['email'])).first()
    if existing:
        abort(400, "Username or email exists")
    hashed = get_password_hash(data['password'])
    user = User(
        username=data['username'],
        email=data['email'],
        hashed_password=hashed,
        full_name=data['full_name'],
        role=data.get('role', UserRole.VIEWER.value),
        club_id=data.get('club_id'),
        is_active=True
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"id": str(user.id)}), 201

@bp.route('/users/<user_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        abort(404)
    current = get_current_user()
    if user.id == current.id:
        abort(400, "Cannot delete yourself")
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"})

# ---------- News CRUD ----------
@bp.route('/news', methods=['POST'])
@jwt_required()
def create_news():
    user = get_current_user()
    if user.role not in [UserRole.ADMIN.value, UserRole.MEDIA_OFFICER.value]:
        abort(403, "Not authorized")
    data = request.get_json()
    slug = data['title'].lower().replace(" ", "-")
    news = News(
        title=data['title'],
        content=data['content'],
        excerpt=data['excerpt'],
        featured_image=data.get('featured_image'),
        slug=slug,
        author_id=user.id,
        is_published=True
    )
    db.session.add(news)
    db.session.commit()
    return jsonify({"id": str(news.id)}), 201

@bp.route('/news/<news_id>', methods=['PUT'])
@jwt_required()
def update_news(news_id):
    user = get_current_user()
    if user.role not in [UserRole.ADMIN.value, UserRole.MEDIA_OFFICER.value]:
        abort(403)
    news = News.query.get(news_id)
    if not news:
        abort(404)
    data = request.get_json()
    news.title = data.get('title', news.title)
    news.content = data.get('content', news.content)
    news.excerpt = data.get('excerpt', news.excerpt)
    news.featured_image = data.get('featured_image', news.featured_image)
    news.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({"message": "Updated"})

@bp.route('/news/<news_id>', methods=['DELETE'])
@jwt_required()
def delete_news(news_id):
    user = get_current_user()
    if user.role not in [UserRole.ADMIN.value, UserRole.MEDIA_OFFICER.value]:
        abort(403)
    news = News.query.get(news_id)
    if not news:
        abort(404)
    db.session.delete(news)
    db.session.commit()
    return jsonify({"message": "Deleted"})

# ---------- Matches CRUD ----------
@bp.route('/matches', methods=['POST'])
@jwt_required()
def create_match():
    user = get_current_user()
    if user.role not in [UserRole.ADMIN.value, UserRole.MATCH_COMMISSIONER.value]:
        abort(403)
    data = request.get_json()
    match = Match(
        home_team=data['home_team'],
        away_team=data['away_team'],
        home_score=data.get('home_score', 0),
        away_score=data.get('away_score', 0),
        match_date=datetime.fromisoformat(data['match_date']),
        venue=data['venue'],
        competition=data['competition'],
        status=data.get('status', 'upcoming'),
        is_home_match=data.get('is_home_match', True)
    )
    db.session.add(match)
    db.session.commit()
    return jsonify({"id": str(match.id)}), 201

# ... similarly update, delete

# ---------- Teams CRUD ----------
@bp.route('/teams', methods=['POST'])
@jwt_required()
@admin_required
def create_team():
    data = request.get_json()
    team_type = data.get('type')  # 'national' or 'club'
    if team_type == 'national':
        # Expect fields for NationalTeam
        # We need to pass all data, but we can filter only relevant fields
        # For simplicity, we'll use **data and hope keys match
        team = NationalTeam(**data)
    elif team_type == 'club':
        team = Club(**data)
    else:
        abort(400, "Missing or invalid 'type' field (must be 'national' or 'club')")
    db.session.add(team)
    db.session.commit()
    return jsonify({"id": str(team.id)}), 201

@bp.route('/teams/<team_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_team(team_id):
    # Try NationalTeam first, then Club
    team = NationalTeam.query.get(team_id)
    if not team:
        team = Club.query.get(team_id)
    if not team:
        abort(404, "Team not found")
    data = request.get_json()
    # Update only fields that exist in the model (ignore extra keys)
    for key, value in data.items():
        if hasattr(team, key):
            setattr(team, key, value)
    db.session.commit()
    return jsonify({"message": "Updated"})

@bp.route('/teams/<team_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_team(team_id):
    team = NationalTeam.query.get(team_id)
    if not team:
        team = Club.query.get(team_id)
    if not team:
        abort(404, "Team not found")
    db.session.delete(team)
    db.session.commit()
    return jsonify({"message": "Deleted"})

# ---------- Players CRUD ----------
@bp.route('/players', methods=['POST'])
@jwt_required()
def create_player():
    user = get_current_user()
    if user.role not in [UserRole.ADMIN.value, UserRole.CLUB_REP.value]:
        abort(403)
    data = request.get_json()
    player = Player(**data)
    db.session.add(player)
    db.session.commit()
    return jsonify({"id": str(player.id)}), 201

# Similar for PUT and DELETE

# ---------- Registration (public) ----------
@bp.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    existing = User.query.filter((User.username == data['username']) | (User.email == data['email'])).first()
    if existing:
        abort(400, "Username or email exists")
    hashed = get_password_hash(data['password'])
    user = User(
        username=data['username'],
        email=data['email'],
        hashed_password=hashed,
        full_name=data['full_name'],
        role=data.get('role', UserRole.VIEWER.value),
        club_id=data.get('club_id'),
        is_active=True
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"})