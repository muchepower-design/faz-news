# app/routes/content.py
from flask import Blueprint, request, jsonify, abort
from flask_jwt_extended import jwt_required
from app.database import db
from backend.app.models.content_old import HeroSlide, Partner, GovernanceMember, Page
from app.auth import admin_required


bp = Blueprint('content', __name__)


# ======================================================================
# PUBLIC
# ======================================================================
@bp.route('/hero-slides', methods=['GET'])
def get_hero_slides():
    slides = (
        HeroSlide.query
        .filter_by(is_active=True)
        .order_by(HeroSlide.slide_order.asc(), HeroSlide.created_at.asc())
        .all()
    )
    return jsonify([s.to_dict() for s in slides]), 200


@bp.route('/partners', methods=['GET'])
def get_partners():
    items = (
        Partner.query
        .filter_by(is_active=True)
        .order_by(Partner.partner_order.asc(), Partner.name.asc())
        .all()
    )
    return jsonify([p.to_dict() for p in items]), 200


@bp.route('/governance-members', methods=['GET'])
def get_governance_members():
    category = request.args.get('category')
    q = GovernanceMember.query.filter_by(is_active=True)
    if category:
        q = q.filter_by(category=category)
    members = q.order_by(
        GovernanceMember.member_order.asc(),
        GovernanceMember.name.asc(),
    ).all()
    return jsonify([m.to_dict() for m in members]), 200


@bp.route('/pages/by-path', methods=['GET'])
def get_page_by_path():
    path = (request.args.get('path') or '').strip().strip('/')
    if not path:
        abort(400, "path query parameter is required")

    page = Page.query.filter_by(path=path, is_published=True).first()
    if not page:
        abort(404, "Page not found")
    return jsonify(page.to_dict()), 200


# ======================================================================
# ADMIN — HERO SLIDES
# ======================================================================
@bp.route('/admin/hero-slides', methods=['GET'])
@jwt_required()
@admin_required
def admin_list_hero_slides():
    slides = HeroSlide.query.order_by(HeroSlide.slide_order.asc()).all()
    return jsonify([s.to_dict() for s in slides]), 200


@bp.route('/admin/hero-slides', methods=['POST'])
@jwt_required()
@admin_required
def admin_create_hero_slide():
    data = request.get_json() or {}
    if not data.get('title') or not data.get('image_url'):
        abort(400, "title and image_url are required")
    s = HeroSlide(
        title=data['title'],
        subtitle=data.get('subtitle'),
        image_url=data['image_url'],
        cta_text=data.get('cta_text'),
        cta_link=data.get('cta_link'),
        slide_order=int(data.get('slide_order') or 0),
        is_active=bool(data.get('is_active', True)),
    )
    db.session.add(s)
    db.session.commit()
    return jsonify(s.to_dict()), 201


@bp.route('/admin/hero-slides/<slide_id>', methods=['PUT'])
@jwt_required()
@admin_required
def admin_update_hero_slide(slide_id):
    s = HeroSlide.query.get_or_404(slide_id)
    data = request.get_json() or {}
    for f in ['title', 'subtitle', 'image_url', 'cta_text', 'cta_link']:
        if f in data:
            setattr(s, f, data[f])
    if 'slide_order' in data:
        s.slide_order = int(data['slide_order'] or 0)
    if 'is_active' in data:
        s.is_active = bool(data['is_active'])
    db.session.commit()
    return jsonify(s.to_dict()), 200


@bp.route('/admin/hero-slides/<slide_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def admin_delete_hero_slide(slide_id):
    s = HeroSlide.query.get_or_404(slide_id)
    db.session.delete(s)
    db.session.commit()
    return jsonify({'message': 'Deleted'}), 200


# ======================================================================
# ADMIN — PARTNERS
# ======================================================================
@bp.route('/admin/partners', methods=['GET'])
@jwt_required()
@admin_required
def admin_list_partners():
    items = Partner.query.order_by(Partner.partner_order.asc()).all()
    return jsonify([p.to_dict() for p in items]), 200


@bp.route('/admin/partners', methods=['POST'])
@jwt_required()
@admin_required
def admin_create_partner():
    data = request.get_json() or {}
    if not data.get('name') or not data.get('logo_url'):
        abort(400, "name and logo_url are required")
    p = Partner(
        name=data['name'],
        logo_url=data['logo_url'],
        website_url=data.get('website_url'),
        tier=data.get('tier'),
        partner_order=int(data.get('partner_order') or 0),
        is_active=bool(data.get('is_active', True)),
    )
    db.session.add(p)
    db.session.commit()
    return jsonify(p.to_dict()), 201


@bp.route('/admin/partners/<partner_id>', methods=['PUT'])
@jwt_required()
@admin_required
def admin_update_partner(partner_id):
    p = Partner.query.get_or_404(partner_id)
    data = request.get_json() or {}
    for f in ['name', 'logo_url', 'website_url', 'tier']:
        if f in data:
            setattr(p, f, data[f])
    if 'partner_order' in data:
        p.partner_order = int(data['partner_order'] or 0)
    if 'is_active' in data:
        p.is_active = bool(data['is_active'])
    db.session.commit()
    return jsonify(p.to_dict()), 200


@bp.route('/admin/partners/<partner_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def admin_delete_partner(partner_id):
    p = Partner.query.get_or_404(partner_id)
    db.session.delete(p)
    db.session.commit()
    return jsonify({'message': 'Deleted'}), 200


# ======================================================================
# ADMIN — GOVERNANCE MEMBERS
# ======================================================================
@bp.route('/admin/governance-members', methods=['GET'])
@jwt_required()
@admin_required
def admin_list_governance_members():
    members = GovernanceMember.query.order_by(GovernanceMember.member_order.asc()).all()
    return jsonify([m.to_dict() for m in members]), 200


@bp.route('/admin/governance-members', methods=['POST'])
@jwt_required()
@admin_required
def admin_create_governance_member():
    data = request.get_json() or {}
    if not data.get('name') or not data.get('position'):
        abort(400, "name and position are required")
    category = data.get('category') or 'national'
    if category not in ('national', 'provincial'):
        abort(400, "category must be 'national' or 'provincial'")
    m = GovernanceMember(
        name=data['name'],
        position=data['position'],
        category=category,
        province=data.get('province'),
        image_url=data.get('image_url'),
        bio=data.get('bio'),
        email=data.get('email'),
        term_start=data.get('term_start'),
        term_end=data.get('term_end'),
        member_order=int(data.get('member_order') or 0),
        is_active=bool(data.get('is_active', True)),
    )
    db.session.add(m)
    db.session.commit()
    return jsonify(m.to_dict()), 201


@bp.route('/admin/governance-members/<member_id>', methods=['PUT'])
@jwt_required()
@admin_required
def admin_update_governance_member(member_id):
    m = GovernanceMember.query.get_or_404(member_id)
    data = request.get_json() or {}
    for f in ['name', 'position', 'category', 'province', 'image_url',
              'bio', 'email', 'term_start', 'term_end']:
        if f in data:
            setattr(m, f, data[f])
    if 'member_order' in data:
        m.member_order = int(data['member_order'] or 0)
    if 'is_active' in data:
        m.is_active = bool(data['is_active'])
    db.session.commit()
    return jsonify(m.to_dict()), 200


@bp.route('/admin/governance-members/<member_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def admin_delete_governance_member(member_id):
    m = GovernanceMember.query.get_or_404(member_id)
    db.session.delete(m)
    db.session.commit()
    return jsonify({'message': 'Deleted'}), 200


# ======================================================================
# ADMIN — PAGES
# ======================================================================
@bp.route('/admin/pages', methods=['GET'])
@jwt_required()
@admin_required
def admin_list_pages():
    pages = Page.query.order_by(Page.category.asc(), Page.page_order.asc()).all()
    return jsonify([p.to_dict() for p in pages]), 200


@bp.route('/admin/pages', methods=['POST'])
@jwt_required()
@admin_required
def admin_create_page():
    data = request.get_json() or {}
    if not data.get('path') or not data.get('title'):
        abort(400, "path and title are required")

    clean_path = data['path'].strip().strip('/').lower()
    if Page.query.filter_by(path=clean_path).first():
        abort(409, "A page with that path already exists")

    p = Page(
        path=clean_path,
        title=data['title'],
        subtitle=data.get('subtitle'),
        excerpt=data.get('excerpt'),
        content=data.get('content'),
        hero_image_url=data.get('hero_image_url'),
        category=data.get('category'),
        meta_title=data.get('meta_title'),
        meta_description=data.get('meta_description'),
        is_published=bool(data.get('is_published', True)),
        page_order=int(data.get('page_order') or 0),
    )
    db.session.add(p)
    db.session.commit()
    return jsonify(p.to_dict()), 201


@bp.route('/admin/pages/<page_id>', methods=['PUT'])
@jwt_required()
@admin_required
def admin_update_page(page_id):
    p = Page.query.get_or_404(page_id)
    data = request.get_json() or {}
    for f in ['title', 'subtitle', 'excerpt', 'content', 'hero_image_url',
              'category', 'meta_title', 'meta_description']:
        if f in data:
            setattr(p, f, data[f])
    if 'path' in data:
        clean_path = data['path'].strip().strip('/').lower()
        existing = Page.query.filter(Page.path == clean_path, Page.id != p.id).first()
        if existing:
            abort(409, "Another page already uses that path")
        p.path = clean_path
    if 'page_order' in data:
        p.page_order = int(data['page_order'] or 0)
    if 'is_published' in data:
        p.is_published = bool(data['is_published'])
    db.session.commit()
    return jsonify(p.to_dict()), 200


@bp.route('/admin/pages/<page_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def admin_delete_page(page_id):
    p = Page.query.get_or_404(page_id)
    db.session.delete(p)
    db.session.commit()
    return jsonify({'message': 'Deleted'}), 200