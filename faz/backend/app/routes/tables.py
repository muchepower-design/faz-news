from flask import Blueprint, request, jsonify
from app.database import db
from app.models import LeagueTable, LeagueStanding
from sqlalchemy import desc

bp = Blueprint('tables', __name__)

@bp.route('/', methods=['GET'])
def get_league_table():
    season = request.args.get('season')
    if not season:
        abort(400, "season required")
    # try league_standings first
    standings = LeagueStanding.query.filter_by(season=season).order_by(LeagueStanding.points.desc()).all()
    if standings:
        return jsonify([s.to_dict() for s in standings])
    # fallback to league_tables
    table = LeagueTable.query.filter_by(season=season).order_by(LeagueTable.points.desc()).all()
    return jsonify([t.to_dict() for t in table])

@bp.route('/seasons', methods=['GET'])
def get_seasons():
    seasons = db.session.query(LeagueStanding.season).distinct().order_by(LeagueStanding.season.desc()).all()
    seasons_list = [s[0] for s in seasons if s[0]]
    if not seasons_list:
        seasons = db.session.query(LeagueTable.season).distinct().order_by(LeagueTable.season.desc()).all()
        seasons_list = [s[0] for s in seasons if s[0]]
    return jsonify(seasons_list)