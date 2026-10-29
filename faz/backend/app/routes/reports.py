from flask import Blueprint, request, jsonify, abort
from flask_jwt_extended import jwt_required
from app.database import db
from app.models import MatchReport, Match
from app.auth import get_current_user

bp = Blueprint('reports', __name__)

@bp.route('/match-reports', methods=['POST'])
@jwt_required()
def submit_report():
    user = get_current_user()
    if user.role != 'referee':
        abort(403, "Only referees can submit reports")
    data = request.get_json()
    match = Match.query.get(data['match_id'])
    if not match:
        abort(404, "Match not found")
    if match.referee_id != user.id:
        abort(403, "This match is not assigned to you")
    existing = MatchReport.query.filter_by(match_id=data['match_id']).first()
    if existing:
        abort(400, "Report already submitted")
    report = MatchReport(
        match_id=data['match_id'],
        referee_id=user.id,
        content=data['content'],
        yellow_cards=data.get('yellow_cards', []),
        red_cards=data.get('red_cards', []),
        incidents=data.get('incidents', [])
    )
    db.session.add(report)
    db.session.commit()
    return jsonify({"id": str(report.id)}), 201

@bp.route('/match-reports/match/<match_id>', methods=['GET'])
def get_report_by_match(match_id):
    report = MatchReport.query.filter_by(match_id=match_id).first()
    if not report:
        abort(404)
    return jsonify(report.to_dict())

@bp.route('/match-reports/<report_id>', methods=['PUT'])
@jwt_required()
def update_report(report_id):
    user = get_current_user()
    report = MatchReport.query.get(report_id)
    if not report:
        abort(404)
    if report.referee_id != user.id:
        abort(403)
    data = request.get_json()
    report.content = data.get('content', report.content)
    report.yellow_cards = data.get('yellow_cards', report.yellow_cards)
    report.red_cards = data.get('red_cards', report.red_cards)
    report.incidents = data.get('incidents', report.incidents)
    db.session.commit()
    return jsonify({"message": "Report updated"})