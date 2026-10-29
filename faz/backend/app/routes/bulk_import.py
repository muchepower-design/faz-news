import csv, io, json
from flask import Blueprint, request, jsonify, abort
from flask_jwt_extended import jwt_required
from app.database import db
from app.models import Player, Match, MatchEvent, UserRole, NationalTeam, Club
from app.auth import get_current_user, admin_required
from datetime import datetime

bp = Blueprint('bulk_import', __name__)

@bp.route('/teams', methods=['POST'])
@jwt_required()
@admin_required
def import_teams():
    file = request.files.get('file')
    if not file:
        abort(400, "No file")
    content = file.read().decode('utf-8')
    try:
        reader = csv.DictReader(io.StringIO(content))
        count = 0
        for row in reader:
            team_type = row.get('type', '').lower()
            if team_type == 'national':
                team = NationalTeam(
                    name=row['name'],
                    short_name=row.get('short_name', ''),
                    country_id=row['country_id'],
                    age_group=row.get('age_group', 'Senior'),
                    gender=row.get('gender', 'male'),
                    coach=row.get('coach'),
                    fifa_code=row['fifa_code'],
                    flag_image_url=row.get('flag_image_url'),
                    age=row.get('age', 'Senior'),
                    nickname=row.get('nickname')
                )
            elif team_type == 'club':
                team = Club(
                    name=row['name'],
                    short_name=row.get('short_name', ''),
                    country_id=row['country_id'],
                    gender=row.get('gender', 'male'),
                    logo_url=row.get('logo_url'),
                    description=row.get('description'),
                    is_active=True
                )
            else:
                continue  # skip invalid rows
            db.session.add(team)
            count += 1
        db.session.commit()
        return jsonify({"success": True, "rows_imported": count})
    except Exception as e:
        return jsonify({"success": False, "rows_imported": 0, "errors": str(e)}), 400

@bp.route('/players', methods=['POST'])
@jwt_required()
@admin_required
def import_players():
    file = request.files.get('file')
    if not file:
        abort(400)
    content = file.read().decode('utf-8')
    try:
        reader = csv.DictReader(io.StringIO(content))
        count = 0
        for row in reader:
            # Try to find team in both tables
            team = NationalTeam.query.filter_by(name=row['team_name']).first()
            if not team:
                team = Club.query.filter_by(name=row['team_name']).first()
            if not team:
                continue
            player = Player(
                name=row['name'],
                position=row['position'],
                jersey_number=int(row['jersey_number']),
                date_of_birth=datetime.strptime(row['date_of_birth'], '%Y-%m-%d').date(),
                nationality=row['nationality'],
                team_id=team.id,
                goals=int(row.get('goals', 0)),
                assists=int(row.get('assists', 0)),
                appearances=int(row.get('appearances', 0))
            )
            db.session.add(player)
            count += 1
        db.session.commit()
        return jsonify({"success": True, "rows_imported": count})
    except Exception as e:
        return jsonify({"success": False, "rows_imported": 0, "errors": str(e)}), 400

@bp.route('/matches', methods=['POST'])
@jwt_required()
@admin_required
def import_matches():
    file = request.files.get('file')
    if not file:
        abort(400)
    content = file.read().decode('utf-8')
    try:
        data = json.loads(content)
        count = 0
        for item in data:
            home = NationalTeam.query.filter_by(name=item['home_team']).first()
            if not home:
                home = Club.query.filter_by(name=item['home_team']).first()
            away = NationalTeam.query.filter_by(name=item['away_team']).first()
            if not away:
                away = Club.query.filter_by(name=item['away_team']).first()
            if not home or not away:
                continue
            match = Match(
                home_team=home.name,
                away_team=away.name,
                home_score=item['home_score'],
                away_score=item['away_score'],
                match_date=datetime.fromisoformat(item['match_date']),
                venue=item['venue'],
                competition=item.get('competition', 'Super League'),
                status=item.get('status', 'finished')
            )
            db.session.add(match)
            db.session.flush()
            for evt in item.get('events', []):
                player = Player.query.filter_by(name=evt['player_name']).first()
                if not player:
                    continue
                assist_player = None
                if evt.get('assist_player'):
                    assist_player = Player.query.filter_by(name=evt['assist_player']).first()
                event = MatchEvent(
                    match_id=match.id,
                    event_type=evt['event_type'],
                    player_id=player.id,
                    related_player_id=assist_player.id if assist_player else None,
                    minute=evt['minute'],
                    minute_added=evt.get('minute_added', 0)
                )
                db.session.add(event)
            count += 1
        db.session.commit()
        return jsonify({"success": True, "rows_imported": count})
    except Exception as e:
        return jsonify({"success": False, "rows_imported": 0, "errors": str(e)}), 400