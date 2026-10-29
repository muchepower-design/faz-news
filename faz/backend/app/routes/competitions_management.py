from flask import Blueprint, request, jsonify, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database import db
from app.models import (
    Competition, CompetitionSeason, Stage, Group,
    CompetitionMatch, Standing, QualificationRule,
    User, NationalTeam, Club
)
from app.auth import get_current_user, admin_required
from sqlalchemy import or_, func as sqlfunc
from sqlalchemy.orm import joinedload
from datetime import datetime
import uuid

bp = Blueprint('competitions_management', __name__, url_prefix='/competitions-management')




# ---------- Helper: Recalculate standings ----------
def recalc_standings(season_id=None, group_id=None):
    """Recalculate standings for a given season or group."""
    matches = CompetitionMatch.query
    if season_id:
        matches = matches.filter_by(season_id=season_id)
    if group_id:
        matches = matches.filter_by(group_id=group_id)
    matches = matches.filter_by(status='finished').all()

    if season_id:
        standings_q = Standing.query.filter_by(season_id=season_id)
    elif group_id:
        standings_q = Standing.query.filter_by(group_id=group_id)
    else:
        return

    standings = {s.team_id: s for s in standings_q.all()}

    # Reset all existing stats to zero
    for s in standings.values():
        s.played = 0
        s.won = 0
        s.drawn = 0
        s.lost = 0
        s.goals_for = 0
        s.goals_against = 0
        s.points = 0

    for match in matches:
        home_team_id = match.home_team_id
        away_team_id = match.away_team_id
        hs = match.home_score or 0
        as_ = match.away_score or 0

        # Create missing Standing rows with explicit zeroes
        if home_team_id not in standings:
            s = Standing(
                team_id=home_team_id,
                season_id=season_id,
                group_id=group_id,
                played=0, won=0, drawn=0, lost=0,
                goals_for=0, goals_against=0, points=0,
            )
            db.session.add(s)
            standings[home_team_id] = s

        if away_team_id not in standings:
            s = Standing(
                team_id=away_team_id,
                season_id=season_id,
                group_id=group_id,
                played=0, won=0, drawn=0, lost=0,
                goals_for=0, goals_against=0, points=0,
            )
            db.session.add(s)
            standings[away_team_id] = s

        home_stand = standings[home_team_id]
        away_stand = standings[away_team_id]

        home_stand.played += 1
        away_stand.played += 1
        home_stand.goals_for += hs
        home_stand.goals_against += as_
        away_stand.goals_for += as_
        away_stand.goals_against += hs

        if hs > as_:
            home_stand.won += 1
            home_stand.points += 3
            away_stand.lost += 1
        elif hs < as_:
            away_stand.won += 1
            away_stand.points += 3
            home_stand.lost += 1
        else:
            home_stand.drawn += 1
            home_stand.points += 1
            away_stand.drawn += 1
            away_stand.points += 1

    db.session.commit()

# ---------- Helper: Filter teams by competition gender & age ----------
def filter_teams_by_competition(query, Model, competition):
    """
    Filter teams by gender and age, case-insensitively.
    - Skips gender filter when competition.gender is 'mixed', 'any', 'all', or empty/None.
    - Skips age filter when competition.age_group is empty/None.
    - Matches age against Model.age_group OR Model.age (whichever exists).
    """

    # ---- Gender ----
    if competition.gender:
        g = competition.gender.strip().lower()
        if g not in ('mixed', 'any', 'all', ''):
            query = query.filter(sqlfunc.lower(Model.gender) == g)

    # ---- Age ----
    if competition.age_group:
        target = competition.age_group.strip().lower()
        conditions = []
        if hasattr(Model, 'age_group'):
            conditions.append(sqlfunc.lower(Model.age_group) == target)
        if hasattr(Model, 'age'):
            conditions.append(sqlfunc.lower(Model.age) == target)
        if conditions:
            query = query.filter(or_(*conditions))

    return query


# ==================== COMPETITIONS ====================
@bp.route('/competitions', methods=['POST'])
@jwt_required()
@admin_required
def create_competition():
    data = request.get_json()
    comp = Competition(
        name=data['name'],
        competition_type=data['competition_type'],
        gender=data['gender'],
        age_group=data.get('age_group'),
        scope=data.get('scope'),
        description=data.get('description'),
        logo_url=data.get('logo_url'),
        participant_type=data.get('participant_type')
    )
    db.session.add(comp)
    db.session.commit()
    return jsonify(comp.to_dict()), 201

@bp.route('/competitions/<competition_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_competition(competition_id):
    comp = Competition.query.get_or_404(competition_id)
    data = request.get_json()
    for field in ['name', 'competition_type', 'gender', 'age_group', 'scope', 'description', 'logo_url', 'is_active', 'participant_type']:
        if field in data:
            setattr(comp, field, data[field])
    db.session.commit()
    return jsonify(comp.to_dict()), 200

@bp.route('/competitions/<competition_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_competition(competition_id):
    comp = Competition.query.get_or_404(competition_id)
    comp.is_active = False
    db.session.commit()
    return jsonify({'message': 'Competition deactivated'}), 200

@bp.route('/competitions', methods=['GET'])
def get_competitions():
    active_only = request.args.get('active_only', 'true').lower() == 'true'
    query = Competition.query
    if active_only:
        query = query.filter_by(is_active=True)
    competitions = query.all()
    return jsonify([c.to_dict() for c in competitions]), 200

@bp.route('/competitions/<competition_id>', methods=['GET'])
def get_competition(competition_id):
    comp = Competition.query.get_or_404(competition_id)
    return jsonify(comp.to_dict()), 200

# ==================== SEASONS ====================
@bp.route('/competitions/<competition_id>/seasons', methods=['POST'])
@jwt_required()
@admin_required
def create_season(competition_id):
    comp = Competition.query.get_or_404(competition_id)
    data = request.get_json()
    season = CompetitionSeason(
        competition_id=comp.id,
        season=data['name'],
        started_at=datetime.strptime(data['start_date'], '%Y-%m-%d').date() if data.get('start_date') else None,
        ended_at=datetime.strptime(data['end_date'], '%Y-%m-%d').date() if data.get('end_date') else None,
        is_archived=data.get('is_current', False)
    )
    db.session.add(season)
    db.session.commit()
    return jsonify(season.to_dict()), 201

@bp.route('/seasons/<season_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_season(season_id):
    season = CompetitionSeason.query.get_or_404(season_id)
    data = request.get_json()
    for field in ['name', 'status', 'is_current']:
        if field in data:
            setattr(season, field, data[field])
    if 'start_date' in data:
        season.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
    if 'end_date' in data:
        season.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
    db.session.commit()
    return jsonify(season.to_dict()), 200

@bp.route('/seasons/<season_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_season(season_id):
    season = CompetitionSeason.query.get_or_404(season_id)
    db.session.delete(season)
    db.session.commit()
    return jsonify({'message': 'Season deleted'}), 200

@bp.route('/competitions/<competition_id>/seasons', methods=['GET'])
def get_seasons(competition_id):
    comp = Competition.query.get_or_404(competition_id)
    seasons = comp.seasons
    return jsonify([s.to_dict() for s in seasons]), 200

@bp.route('/seasons/<season_id>', methods=['GET'])
def get_season(season_id):
    season = CompetitionSeason.query.get_or_404(season_id)
    return jsonify(season.to_dict()), 200

# ---------- FETCHING TEAMS (now filtered by competition gender + age) ----------
@bp.route('/teams/<competition_id>', methods=['GET'])
def get_teams(competition_id):
    skip = int(request.args.get('skip', 0))
    limit = int(request.args.get('limit', 20))
    skip_filter = request.args.get('skip_filter', 'false').lower() == 'true'

    comp = Competition.query.get(competition_id)
    if not comp:
        abort(404, "Competition not found")

    if comp.participant_type == "countries":
        query = NationalTeam.query
        if not skip_filter:
            query = filter_teams_by_competition(query, NationalTeam, comp)
    else:
        query = Club.query
        if not skip_filter:
            query = filter_teams_by_competition(query, Club, comp)

    teams = query.offset(skip).limit(limit).all()
    return jsonify([t.to_dict() for t in teams]), 200


# ---------- GET all groups for a season (keyed by stage_id) ----------
@bp.route('/seasons/<season_id>/groups', methods=['GET'])
def get_season_groups(season_id):
    season = CompetitionSeason.query.get_or_404(season_id)
    stages = Stage.query.filter_by(season_id=season_id).all()
    result = {}
    for stage in stages:
        stage_groups = Group.query.filter_by(stage_id=stage.id).order_by(Group.group_order).all()
        result[str(stage.id)] = [g.to_dict() for g in stage_groups]
    return jsonify(result), 200

# ---------- GET matches for a season ----------
@bp.route('/seasons/<season_id>/matches', methods=['GET'])
def get_season_matches(season_id):
    season = CompetitionSeason.query.get_or_404(season_id)
    matches = CompetitionMatch.query.filter_by(season_id=season_id).all()
    return jsonify([m.to_dict() for m in matches]), 200

# ==================== STAGES ====================
@bp.route('/seasons/<season_id>/stages', methods=['POST'])
@jwt_required()
@admin_required
def create_stage(season_id):
    season = CompetitionSeason.query.get_or_404(season_id)
    data = request.get_json()
    stage = Stage(
        season_id=season.id,
        name=data['name'],
        stage_order=data.get('stage_order', 0),
        is_knockout=data.get('is_knockout', False),
        is_group_stage=data.get('is_group_stage', False)
    )
    db.session.add(stage)
    db.session.commit()
    return jsonify(stage.to_dict()), 201

@bp.route('/stages/<stage_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_stage(stage_id):
    stage = Stage.query.get_or_404(stage_id)
    data = request.get_json()
    for field in ['name', 'stage_order', 'is_knockout', 'is_group_stage']:
        if field in data:
            setattr(stage, field, data[field])
    db.session.commit()
    return jsonify(stage.to_dict()), 200

@bp.route('/stages/<stage_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_stage(stage_id):
    stage = Stage.query.get_or_404(stage_id)
    db.session.delete(stage)
    db.session.commit()
    return jsonify({'message': 'Stage deleted'}), 200

@bp.route('/seasons/<season_id>/stages', methods=['GET'])
def get_stages(season_id):
    season = CompetitionSeason.query.get_or_404(season_id)
    stages = season.stages
    return jsonify([s.to_dict() for s in stages]), 200

# ==================== GROUPS ====================
@bp.route('/stages/<stage_id>/groups', methods=['POST'])
@jwt_required()
@admin_required
def create_group(stage_id):
    stage = Stage.query.get_or_404(stage_id)
    data = request.get_json()
    group = Group(
        stage_id=stage.id,
        name=data['name'],
        group_order=data.get('group_order', 0)
    )
    db.session.add(group)
    db.session.commit()
    return jsonify(group.to_dict()), 201

@bp.route('/groups/<group_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_group(group_id):
    group = Group.query.get_or_404(group_id)
    data = request.get_json()
    for field in ['name', 'group_order']:
        if field in data:
            setattr(group, field, data[field])
    db.session.commit()
    return jsonify(group.to_dict()), 200

@bp.route('/groups/<group_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_group(group_id):
    group = Group.query.get_or_404(group_id)
    db.session.delete(group)
    db.session.commit()
    return jsonify({'message': 'Group deleted'}), 200

@bp.route('/stages/<stage_id>/groups', methods=['GET'])
def get_groups(stage_id):
    stage = Stage.query.get_or_404(stage_id)
    groups = stage.groups
    return jsonify([g.to_dict() for g in groups]), 200

# ==================== GROUP TEAMS ====================
@bp.route('/groups/<group_id>/teams', methods=['GET'])
def get_group_teams(group_id):
    group = Group.query.get_or_404(group_id)
    teams = list(group.national_teams) + list(group.clubs)
    return jsonify([t.to_dict() for t in teams]), 200

@bp.route('/groups/<group_id>/teams', methods=['POST'])
@jwt_required()
@admin_required
def add_team_to_group(group_id):
    data = request.get_json()
    team_id = data.get('team_id')
    if not team_id:
        abort(400, "team_id required")

    group = Group.query.get_or_404(group_id)

    competition = (
        Competition.query
        .join(CompetitionSeason, CompetitionSeason.competition_id == Competition.id)
        .join(Stage, Stage.season_id == CompetitionSeason.id)
        .join(Group, Group.stage_id == Stage.id)
        .filter(Group.id == group_id)
        .first()
    )
    if not competition:
        abort(404, "Competition not found for this group")

    participant_type = competition.participant_type

    if participant_type == 'countries':
        team = NationalTeam.query.get(team_id)
        if not team:
            abort(404, f"National team with id {team_id} not found")
        if team not in group.national_teams:
            group.national_teams.append(team)
            db.session.commit()
        else:
            return jsonify({'message': 'Team already in group'}), 200
    elif participant_type == 'clubs':
        team = Club.query.get(team_id)
        if not team:
            abort(404, f"Club with id {team_id} not found")
        if team not in group.clubs:
            group.clubs.append(team)
            db.session.commit()
        else:
            return jsonify({'message': 'Team already in group'}), 200
    else:
        abort(400, "Competition participant_type not set; cannot add team")

    return jsonify({'message': 'Team added to group'}), 201

@bp.route('/groups/<group_id>/teams/<team_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def remove_team_from_group(group_id, team_id):
    group = Group.query.get_or_404(group_id)

    team_nat = NationalTeam.query.get(team_id)
    if team_nat and team_nat in group.national_teams:
        group.national_teams.remove(team_nat)
        db.session.commit()
        return jsonify({'message': 'National team removed from group'}), 200

    team_club = Club.query.get(team_id)
    if team_club and team_club in group.clubs:
        group.clubs.remove(team_club)
        db.session.commit()
        return jsonify({'message': 'Club removed from group'}), 200

    abort(404, "Team not found in this group")

# ==================== MATCHES ====================
@bp.route('/stages/<stage_id>/matches', methods=['POST'])
@jwt_required()
@admin_required
def create_match(stage_id):
    stage = Stage.query.get_or_404(stage_id)
    data = request.get_json()

    competition = (
        Competition.query
        .join(CompetitionSeason, CompetitionSeason.competition_id == Competition.id)
        .filter(CompetitionSeason.id == stage.season_id)
        .first()
    )
    if not competition:
        abort(404, "Competition not found for this stage")

    participant_type = competition.participant_type

    if participant_type == 'countries':
        home_team = NationalTeam.query.get(data['home_team_id'])
        away_team = NationalTeam.query.get(data['away_team_id'])
    elif participant_type == 'clubs':
        home_team = Club.query.get(data['home_team_id'])
        away_team = Club.query.get(data['away_team_id'])
    else:
        abort(400, "Competition participant_type not set")

    if not home_team or not away_team:
        abort(400, "One or both teams not found")

    match = CompetitionMatch(
        season_id=stage.season_id,
        stage_id=stage.id,
        group_id=data.get('group_id') or None,
        home_team_id=data['home_team_id'],
        away_team_id=data['away_team_id'],
        match_date=datetime.fromisoformat(data['match_date']),
        venue=data.get('venue'),
        is_ticketed=data.get('is_ticketed', False),
        status='scheduled'
    )
    db.session.add(match)
    db.session.commit()
    return jsonify(match.to_dict()), 201

@bp.route('/matches/<match_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_match(match_id):
    match = CompetitionMatch.query.get_or_404(match_id)
    data = request.get_json() or {}

    was_finished = match.status == 'finished'

    for field in [
        'home_team_id', 'away_team_id', 'group_id',
        'match_date', 'venue', 'home_score', 'away_score', 'status', 'is_ticketed',
    ]:
        if field in data:
            if field == 'match_date':
                match.match_date = datetime.fromisoformat(data[field])
            else:
                setattr(match, field, data[field])

    # Guard: a team cannot play itself
    if match.home_team_id == match.away_team_id:
        db.session.rollback()
        return jsonify({'error': 'Home and away team cannot be the same'}), 400

    db.session.commit()

    # Recalculate standings whenever a match becomes finished
    if match.status == 'finished':
        if match.group_id:
            recalc_standings(group_id=match.group_id)
        else:
            recalc_standings(season_id=match.season_id)

    return jsonify(match.to_dict()), 200


@bp.route('/matches/<match_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_match(match_id):
    match = CompetitionMatch.query.get_or_404(match_id)
    db.session.delete(match)
    db.session.commit()
    return jsonify({'message': 'Match deleted'}), 200

@bp.route('/stages/<stage_id>/matches', methods=['GET'])
def get_matches(stage_id):
    stage = Stage.query.get_or_404(stage_id)
    matches = stage.matches
    return jsonify([m.to_dict() for m in matches]), 200


# ==================== ALL MATCHES (read-only feed for the ticketing subsystem) ====================
@bp.route('/all-matches', methods=['GET'])
def get_all_matches_with_details():
    """
    Return every CompetitionMatch with joined competition / season / stage / group info,
    resolved team names, and an 'is_past' flag. The ticketing subsystem uses this
    to display matches that the main system has already created.
    """
    # Optional filtering from the frontend
    competition_id = request.args.get('competition_id')
    season_id = request.args.get('season_id')
    ticketed_only = request.args.get('ticketed_only', 'false').lower() == 'true'

    q = (
        CompetitionMatch.query
        .join(CompetitionSeason, CompetitionMatch.season_id == CompetitionSeason.id)
        .join(Competition, CompetitionSeason.competition_id == Competition.id)
        .outerjoin(Stage, CompetitionMatch.stage_id == Stage.id)
        .outerjoin(Group, CompetitionMatch.group_id == Group.id)
    )
    if competition_id:
        q = q.filter(Competition.id == competition_id)
    if season_id:
        q = q.filter(CompetitionMatch.season_id == season_id)
    if ticketed_only:
        q = q.filter(CompetitionMatch.is_ticketed.is_(True))

    matches = q.order_by(CompetitionMatch.match_date.desc()).all()

    # Cache for team name lookups
    nat_cache = {}
    club_cache = {}

    def resolve_team_name(team_id):
        if not team_id:
            return "TBD"
        key = str(team_id)
        if key in nat_cache:
            return nat_cache[key]
        if key in club_cache:
            return club_cache[key]
        t = NationalTeam.query.get(team_id)
        if t:
            nat_cache[key] = t.name
            return t.name
        t = Club.query.get(team_id)
        if t:
            club_cache[key] = t.name
            return t.name
        return "Unknown"

    # Helper: decide if a match is in the past, handling tz-aware vs tz-naive dates
    def is_past(dt):
        if not dt:
            return False
        try:
            if dt.tzinfo is None:
                return dt < datetime.now()
            return dt < datetime.now(dt.tzinfo)
        except Exception:
            return False

    result = []
    for m in matches:
        season = CompetitionSeason.query.get(m.season_id)
        comp = Competition.query.get(season.competition_id) if season else None
        stage = Stage.query.get(m.stage_id) if m.stage_id else None
        group = Group.query.get(m.group_id) if m.group_id else None

        d = m.to_dict()
        d.update({
            "home_team_name": resolve_team_name(m.home_team_id),
            "away_team_name": resolve_team_name(m.away_team_id),
            "competition_id": str(comp.id) if comp else None,
            "competition_name": comp.name if comp else None,
            "competition_type": comp.competition_type if comp else None,
            "participant_type": comp.participant_type if comp else None,
            "season_id": str(season.id) if season else None,
            "season_name": season.season if season else None,
            "stage_id": str(stage.id) if stage else None,
            "stage_name": stage.name if stage else None,
            "group_id": str(group.id) if group else None,
            "group_name": group.name if group else None,
            "is_past": is_past(m.match_date),
            "is_ticketed": bool(m.is_ticketed),
        })
        result.append(d)

    return jsonify(result), 200

# ---------- GET single match (public, for detail pages) ----------
@bp.route('/matches/<match_id>', methods=['GET'])
def get_single_match(match_id):
    m = CompetitionMatch.query.get(match_id)
    if not m:
        abort(404, "Match not found")

    season = CompetitionSeason.query.get(m.season_id) if m.season_id else None
    comp = Competition.query.get(season.competition_id) if season else None
    stage = Stage.query.get(m.stage_id) if m.stage_id else None
    group = Group.query.get(m.group_id) if m.group_id else None

    def resolve(team_id):
        t = NationalTeam.query.get(team_id)
        if t:
            return t.name
        t = Club.query.get(team_id)
        if t:
            return t.name
        return "TBD"

    d = m.to_dict()
    d.update({
        "home_team": resolve(m.home_team_id),
        "away_team": resolve(m.away_team_id),
        "competition": comp.name if comp else None,
        "competition_id": str(comp.id) if comp else None,
        "competition_type": comp.competition_type if comp else None,
        "participant_type": comp.participant_type if comp else None,
        "season_name": season.season if season else None,
        "stage_name": stage.name if stage else None,
        "group_name": group.name if group else None,
    })
    return jsonify(d), 200


# ==================== STANDINGS ====================
@bp.route('/groups/<group_id>/standings', methods=['GET'])
def get_group_standings(group_id):
    group = Group.query.get_or_404(group_id)
    standings = group.standings.order_by(
        Standing.points.desc(),
        (Standing.goals_for - Standing.goals_against).desc(),
        Standing.goals_for.desc()
    ).all()
    return jsonify([s.to_dict() for s in standings]), 200

@bp.route('/seasons/<season_id>/standings', methods=['GET'])
def get_season_standings(season_id):
    season = CompetitionSeason.query.get_or_404(season_id)
    groups = Group.query.join(Stage).filter(Stage.season_id == season_id).all()
    if groups:
        result = {}
        for g in groups:
            standings = Standing.query.filter_by(group_id=g.id)\
                .order_by(Standing.points.desc(),
                          (Standing.goals_for - Standing.goals_against).desc(),
                          Standing.goals_for.desc()).all()
            result[g.name] = [s.to_dict() for s in standings]
        return jsonify(result), 200
    else:
        standings = Standing.query.filter_by(season_id=season_id)\
            .order_by(Standing.points.desc(),
                      (Standing.goals_for - Standing.goals_against).desc(),
                      Standing.goals_for.desc()).all()
        return jsonify([s.to_dict() for s in standings]), 200

# ==================== QUALIFICATION RULES ====================
@bp.route('/qualification-rules', methods=['POST'])
@jwt_required()
@admin_required
def create_qualification_rule():
    data = request.get_json()
    rule = QualificationRule(
        from_stage_id=data['from_stage_id'],
        to_stage_id=data['to_stage_id'],
        rank_condition=data['rank_condition'],
        number_of_teams=data.get('number_of_teams', 1)
    )
    db.session.add(rule)
    db.session.commit()
    return jsonify(rule.to_dict()), 201

@bp.route('/qualification-rules/<rule_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_qualification_rule(rule_id):
    rule = QualificationRule.query.get_or_404(rule_id)
    data = request.get_json()
    for field in ['rank_condition', 'number_of_teams']:
        if field in data:
            setattr(rule, field, data[field])
    db.session.commit()
    return jsonify(rule.to_dict()), 200

@bp.route('/qualification-rules/<rule_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_qualification_rule(rule_id):
    rule = QualificationRule.query.get_or_404(rule_id)
    db.session.delete(rule)
    db.session.commit()
    return jsonify({'message': 'Rule deleted'}), 200

@bp.route('/stages/<stage_id>/qualification-rules', methods=['GET'])
def get_qualification_rules(stage_id):
    rules = QualificationRule.query.filter_by(from_stage_id=stage_id).all()
    return jsonify([r.to_dict() for r in rules]), 200

# ==================== FRIENDLIES ====================
@bp.route('/friendlies', methods=['POST'])
@jwt_required()
@admin_required
def create_friendly():
    data = request.get_json()

    participant_type = data.get('participant_type', 'clubs')

    if participant_type == 'countries':
        home_team = NationalTeam.query.get(data['home_team_id'])
        away_team = NationalTeam.query.get(data['away_team_id'])
    else:
        home_team = Club.query.get(data['home_team_id'])
        away_team = Club.query.get(data['away_team_id'])

    if not home_team or not away_team:
        abort(400, "Team not found")

    competition = None
    if data.get('series_name'):
        series_name = data['series_name']
        competition = Competition.query.filter_by(name=series_name, competition_type='friendly_series').first()
        if not competition:
            competition = Competition(
                name=series_name,
                competition_type='friendly_series',
                gender=data.get('gender', 'mixed'),
                age_group=data.get('age_group'),
                scope='international',
                is_active=True,
                participant_type=participant_type
            )
            db.session.add(competition)
            db.session.flush()

    season = None
    if competition:
        season_name = data.get('season_name', f"Friendly Series {datetime.now().year}")
        season = CompetitionSeason.query.filter_by(competition_id=competition.id, name=season_name).first()
        if not season:
            season = CompetitionSeason(
                competition_id=competition.id,
                season=season_name,
                started_at=datetime.now().date(),
                is_archived=False
            )
            db.session.add(season)
            db.session.flush()

    stage = None
    if season:
        stage = Stage.query.filter_by(season_id=season.id, name='Friendlies').first()
        if not stage:
            stage = Stage(
                season_id=season.id,
                name='Friendlies',
                stage_order=0,
                is_knockout=False,
                is_group_stage=False
            )
            db.session.add(stage)
            db.session.flush()

    match = CompetitionMatch(
        season_id=season.id if season else None,
        stage_id=stage.id if stage else None,
        home_team_id=data['home_team_id'],
        away_team_id=data['away_team_id'],
        match_date=datetime.fromisoformat(data['match_date']),
        venue=data.get('venue'),
        is_ticketed=data.get('is_ticketed', False),
        status='scheduled'
    )
    db.session.add(match)
    db.session.commit()

    return jsonify(match.to_dict()), 201

@bp.route('/friendlies', methods=['GET'])
def get_friendlies():
    matches = CompetitionMatch.query.join(Stage).join(CompetitionSeason).join(Competition).filter(
        Competition.competition_type == 'friendly_series'
    ).order_by(CompetitionMatch.match_date.desc()).all()
    return jsonify([m.to_dict() for m in matches]), 200


@bp.route('/competitions/<competition_id>/champions', methods=['GET'])
def get_competition_champions(competition_id):
    seasons = CompetitionSeason.query.filter_by(competition_id=competition_id).all()
    result = []
    for s in seasons:
        top = Standing.query.filter_by(season_id=s.id)\
            .order_by(Standing.points.desc(),
                      (Standing.goals_for - Standing.goals_against).desc(),
                      Standing.goals_for.desc())\
            .limit(2).all()
        result.append({
            "id": str(s.id),
            "season": s.season,
            "champion_id": str(top[0].team_id) if len(top) > 0 else None,
            "runner_up_id": str(top[1].team_id) if len(top) > 1 else None,
        })
    return jsonify(result), 200