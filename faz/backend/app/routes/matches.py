from flask import Blueprint, request, jsonify, abort, Response
from flask_jwt_extended import jwt_required
from app.database import db
from app.models import (
    CompetitionMatch,
    CompetitionSeason,
    Competition,
    NationalTeam,
    Club,
)
from app.auth import get_current_user
from datetime import datetime, timedelta
import pytz
from icalendar import Calendar, Event

bp = Blueprint('matches', __name__)


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def enrich(m):
    """CompetitionMatch.to_dict() + competition name/id."""
    d = m.to_dict()
    if m.season_id:
        season = CompetitionSeason.query.get(m.season_id)
        if season:
            comp = Competition.query.get(season.competition_id)
            if comp:
                d["competition"] = comp.name
                d["competition_id"] = str(comp.id)
                d["competition_type"] = comp.competition_type
                d["participant_type"] = comp.participant_type
    return d


# ----------------------------------------------------------------------
# List
# ----------------------------------------------------------------------
@bp.route('/', methods=['GET'])
def get_matches():
    status = request.args.get('status')
    competition = request.args.get('competition')
    skip = int(request.args.get('skip', 0))
    limit = int(request.args.get('limit', 20))
    now = datetime.now()

    q = CompetitionMatch.query
    if status == 'upcoming':
        q = q.filter(
            CompetitionMatch.status.in_(['scheduled', 'live']),
            CompetitionMatch.match_date >= now,
        )
    elif status == 'finished':
        q = q.filter(CompetitionMatch.status == 'finished')
    elif status == 'live':
        q = q.filter(CompetitionMatch.status == 'live')
    elif status:
        q = q.filter(CompetitionMatch.status == status)

    matches = q.order_by(CompetitionMatch.match_date.desc()).all()
    result = [enrich(m) for m in matches]

    if competition:
        result = [r for r in result if r.get("competition") == competition]

    return jsonify(result[skip:skip + limit]), 200


# ----------------------------------------------------------------------
# Latest
# ----------------------------------------------------------------------
@bp.route('/latest', methods=['GET'])
def get_latest_matches():
    limit = int(request.args.get('limit', 5))
    matches = (
        CompetitionMatch.query
        .filter_by(status='finished')
        .order_by(CompetitionMatch.match_date.desc())
        .limit(limit)
        .all()
    )
    return jsonify([enrich(m) for m in matches]), 200


# ----------------------------------------------------------------------
# Upcoming
# ----------------------------------------------------------------------
@bp.route('/upcoming', methods=['GET'])
def get_upcoming_matches():
    limit = int(request.args.get('limit', 5))
    now = datetime.now()
    matches = (
        CompetitionMatch.query
        .filter(
            CompetitionMatch.status.in_(['scheduled', 'live']),
            CompetitionMatch.match_date >= now,
        )
        .order_by(CompetitionMatch.match_date.asc())
        .limit(limit)
        .all()
    )
    return jsonify([enrich(m) for m in matches]), 200


# ----------------------------------------------------------------------
# Single
# ----------------------------------------------------------------------
@bp.route('/<match_id>', methods=['GET'])
def get_match(match_id):
    m = CompetitionMatch.query.get(match_id)
    if not m:
        abort(404)
    return jsonify(enrich(m)), 200


# ----------------------------------------------------------------------
# Update score
# ----------------------------------------------------------------------
@bp.route('/<match_id>/score', methods=['PATCH'])
@jwt_required()
def update_match_score(match_id):
    user = get_current_user()
    if user.role not in ['admin', 'match_commissioner', 'super_admin', 'faz_admin']:
        abort(403)
    m = CompetitionMatch.query.get_or_404(match_id)
    data = request.get_json() or {}
    m.home_score = data.get('home_score', m.home_score)
    m.away_score = data.get('away_score', m.away_score)
    m.status = data.get('status', 'finished')
    db.session.commit()
    return jsonify({"message": "Score updated"}), 200


# ----------------------------------------------------------------------
# iCal export
# ----------------------------------------------------------------------
@bp.route('/export/calendar', methods=['GET'])
def export_calendar():
    team_id = request.args.get('team_id')
    competition = request.args.get('competition')

    q = CompetitionMatch.query.filter(CompetitionMatch.status != 'finished')
    if team_id:
        q = q.filter(
            (CompetitionMatch.home_team_id == team_id) |
            (CompetitionMatch.away_team_id == team_id)
        )
    matches = q.all()

    if competition:
        matches = [m for m in matches if enrich(m).get("competition") == competition]

    cal = Calendar()
    cal.add('prodid', '-//FAZ Match Calendar//faz.zm//')
    cal.add('version', '2.0')

    for m in matches:
        d = enrich(m)
        event = Event()
        event.add('summary', f"{d['home_team']} vs {d['away_team']}")
        md = m.match_date
        if md and md.tzinfo is None:
            md = pytz.UTC.localize(md)
        event.add('dtstart', md)
        event.add('dtend', md + timedelta(hours=2))
        event.add('location', m.venue or '')
        event.add('description', f"Competition: {d.get('competition') or '—'}\nStatus: {m.status}")
        cal.add_component(event)

    headers = {'Content-Disposition': 'attachment; filename="faz_matches.ics"'}
    return Response(cal.to_ical(), mimetype='text/calendar', headers=headers)


# ----------------------------------------------------------------------
# Referee — kept for backwards-compat, returns empty (no referee field)
# ----------------------------------------------------------------------
@bp.route('/referee/<referee_id>', methods=['GET'])
def get_matches_by_referee(referee_id):
    return jsonify([]), 200