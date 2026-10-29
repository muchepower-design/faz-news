# app/routes/content.py
from flask import Blueprint, request, jsonify, abort
from flask_jwt_extended import jwt_required
from app.database import db
import os

from app.models.content import (
    HeroSlide, Partner, GovernanceMember, Page,
    NavItem, FooterSection, FooterLink,
)
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



# ======================================================================
# PUBLIC — NAV & FOOTER
# ======================================================================
@bp.route('/nav-tree', methods=['GET'])
def get_nav_tree():
    roots = (
        NavItem.query
        .filter_by(parent_id=None, is_active=True)
        .order_by(NavItem.item_order.asc())
        .all()
    )
    return jsonify([n.to_dict(admin=False) for n in roots]), 200


@bp.route('/footer', methods=['GET'])
def get_footer_sections():
    sections = (
        FooterSection.query
        .filter_by(is_active=True)
        .order_by(FooterSection.section_order.asc())
        .all()
    )
    return jsonify([s.to_dict(admin=False) for s in sections]), 200


# ======================================================================
# ADMIN — NAV ITEMS
# ======================================================================
def _would_create_nav_cycle(item, new_parent_id):
    """Prevent setting a parent that is the item itself or a descendant."""
    if not new_parent_id:
        return False
    current = new_parent_id
    seen = set()
    while current:
        if str(current) == str(item.id):
            return True
        if str(current) in seen:
            return True
        seen.add(str(current))
        parent = NavItem.query.get(current)
        if not parent:
            break
        current = parent.parent_id
    return False


@bp.route('/admin/nav-items', methods=['GET'])
@jwt_required()
@admin_required
def admin_list_nav_items():
    roots = (
        NavItem.query
        .filter_by(parent_id=None)
        .order_by(NavItem.item_order.asc())
        .all()
    )
    return jsonify([n.to_dict(admin=True) for n in roots]), 200


@bp.route('/admin/nav-items', methods=['POST'])
@jwt_required()
@admin_required
def admin_create_nav_item():
    data = request.get_json() or {}
    if not data.get('label'):
        abort(400, "label is required")
    parent_id = data.get('parent_id') or None
    if parent_id and not NavItem.query.get(parent_id):
        abort(404, "Parent not found")

    item = NavItem(
        label=data['label'],
        path=(data.get('path') or None),
        parent_id=parent_id,
        item_order=int(data.get('item_order') or 0),
        is_active=bool(data.get('is_active', True)),
        is_external=bool(data.get('is_external', False)),
    )
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict(admin=True)), 201


@bp.route('/admin/nav-items/<item_id>', methods=['PUT'])
@jwt_required()
@admin_required
def admin_update_nav_item(item_id):
    item = NavItem.query.get_or_404(item_id)
    data = request.get_json() or {}

    if 'parent_id' in data:
        pid = data['parent_id'] or None
        if _would_create_nav_cycle(item, pid):
            abort(400, "Cannot set a descendant as parent")
        if pid and not NavItem.query.get(pid):
            abort(404, "Parent not found")
        item.parent_id = pid

    if 'label' in data:     item.label = data['label']
    if 'path' in data:      item.path = data['path'] or None
    if 'is_external' in data: item.is_external = bool(data['is_external'])
    if 'item_order' in data:  item.item_order = int(data['item_order'] or 0)
    if 'is_active' in data:   item.is_active = bool(data['is_active'])

    db.session.commit()
    return jsonify(item.to_dict(admin=True)), 200


@bp.route('/admin/nav-items/<item_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def admin_delete_nav_item(item_id):
    item = NavItem.query.get_or_404(item_id)
    db.session.delete(item)   # cascades to children
    db.session.commit()
    return jsonify({'message': 'Deleted'}), 200


# ======================================================================
# ADMIN — FOOTER SECTIONS & LINKS
# ======================================================================
@bp.route('/admin/footer-sections', methods=['GET'])
@jwt_required()
@admin_required
def admin_list_footer_sections():
    sections = FooterSection.query.order_by(FooterSection.section_order.asc()).all()
    return jsonify([s.to_dict(admin=True) for s in sections]), 200


@bp.route('/admin/footer-sections', methods=['POST'])
@jwt_required()
@admin_required
def admin_create_footer_section():
    data = request.get_json() or {}
    if not data.get('title'):
        abort(400, "title is required")
    s = FooterSection(
        title=data['title'],
        section_order=int(data.get('section_order') or 0),
        is_active=bool(data.get('is_active', True)),
    )
    db.session.add(s); db.session.commit()
    return jsonify(s.to_dict(admin=True)), 201


@bp.route('/admin/footer-sections/<section_id>', methods=['PUT'])
@jwt_required()
@admin_required
def admin_update_footer_section(section_id):
    s = FooterSection.query.get_or_404(section_id)
    data = request.get_json() or {}
    if 'title' in data: s.title = data['title']
    if 'section_order' in data: s.section_order = int(data['section_order'] or 0)
    if 'is_active' in data: s.is_active = bool(data['is_active'])
    db.session.commit()
    return jsonify(s.to_dict(admin=True)), 200


@bp.route('/admin/footer-sections/<section_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def admin_delete_footer_section(section_id):
    s = FooterSection.query.get_or_404(section_id)
    db.session.delete(s); db.session.commit()
    return jsonify({'message': 'Deleted'}), 200


@bp.route('/admin/footer-links', methods=['POST'])
@jwt_required()
@admin_required
def admin_create_footer_link():
    data = request.get_json() or {}
    if not data.get('section_id') or not data.get('label'):
        abort(400, "section_id and label are required")
    if not FooterSection.query.get(data['section_id']):
        abort(404, "Section not found")
    link = FooterLink(
        section_id=data['section_id'],
        label=data['label'],
        path=(data.get('path') or None),
        is_external=bool(data.get('is_external', False)),
        link_order=int(data.get('link_order') or 0),
        is_active=bool(data.get('is_active', True)),
    )
    db.session.add(link); db.session.commit()
    return jsonify(link.to_dict()), 201


@bp.route('/admin/footer-links/<link_id>', methods=['PUT'])
@jwt_required()
@admin_required
def admin_update_footer_link(link_id):
    link = FooterLink.query.get_or_404(link_id)
    data = request.get_json() or {}
    if 'label' in data: link.label = data['label']
    if 'path' in data: link.path = data['path'] or None
    if 'is_external' in data: link.is_external = bool(data['is_external'])
    if 'link_order' in data: link.link_order = int(data['link_order'] or 0)
    if 'is_active' in data: link.is_active = bool(data['is_active'])
    if 'section_id' in data and data['section_id']:
        if not FooterSection.query.get(data['section_id']):
            abort(404, "Section not found")
        link.section_id = data['section_id']
    db.session.commit()
    return jsonify(link.to_dict()), 200


@bp.route('/admin/footer-links/<link_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def admin_delete_footer_link(link_id):
    link = FooterLink.query.get_or_404(link_id)
    db.session.delete(link); db.session.commit()
    return jsonify({'message': 'Deleted'}), 200


# ======================================================================
# ADMIN — SEED DEFAULTS (one-time migration of current hardcoded links)
# ======================================================================
def _tickets_base():
    return os.environ.get('FRONTEND_TICKETS_URL', 'http://localhost:5174').rstrip('/')


def _default_nav_payload():
    t = _tickets_base()
    return [
        {"name": "Competitions", "path": "/competitions", "children": [
            {"name": "Men’s Football", "children": [
                {"name": "Super League (MTN Super League)", "path": "/competitions/super-league"},
                {"name": "ABSA Cup", "path": "/competitions/absa-cup"},
                {"name": "Charity Shield", "path": "/competitions/charity-shield"},
                {"name": "Division 1", "path": "/competitions/division-1"},
                {"name": "Division 2", "path": "/competitions/division-2"},
            ]},
            {"name": "Women’s Football", "children": [
                {"name": "Women’s Super League", "path": "/competitions/womens-super-league"},
                {"name": "Women’s Division 1", "path": "/competitions/womens-division-1"},
            ]},
            {"name": "Youth Football", "children": [
                {"name": "U-20 League", "path": "/competitions/u20-league"},
                {"name": "U-17 League", "path": "/competitions/u17-league"},
                {"name": "U-15 League", "path": "/competitions/u15-league"},
            ]},
            {"name": "Futsal League", "path": "/competitions/futsal-league"},
            {"name": "COSAFA (Club)", "path": "/competitions/cosafa-club"},
        ]},
        {"name": "National Teams", "path": "/national-teams", "children": [
            {"name": "Men", "children": [
                {"name": "Senior (Chipolopolo)", "path": "/national-teams/men/senior"},
                {"name": "U-23 (Olympic)", "path": "/national-teams/men/u23"},
                {"name": "U-20", "path": "/national-teams/men/u20"},
                {"name": "U-17", "path": "/national-teams/men/u17"},
                {"name": "U-15", "path": "/national-teams/men/u15"},
            ]},
            {"name": "Women", "children": [
                {"name": "Senior (Copper Queens)", "path": "/national-teams/women/senior"},
                {"name": "U-20", "path": "/national-teams/women/u20"},
                {"name": "U-17", "path": "/national-teams/women/u17"},
                {"name": "U-15", "path": "/national-teams/women/u15"},
            ]},
            {"name": "Competitions", "children": [
                {"name": "World Cup Qualifiers", "path": "/national-teams/competitions/world-cup"},
                {"name": "AFCON Qualifiers", "path": "/national-teams/competitions/afcon"},
                {"name": "CHAN (Men only)", "path": "/national-teams/competitions/chan"},
                {"name": "COSAFA Cup", "path": "/national-teams/competitions/cosafa"},
            ]},
        ]},
        {"name": "Futsal", "path": "/futsal", "children": [
            {"name": "Futsal Super League", "path": "/futsal/super-league"},
            {"name": "Futsal National Team (Men)", "path": "/futsal/men"},
            {"name": "Futsal National Team (Women)", "path": "/futsal/women"},
            {"name": "Futsal Competitions", "path": "/futsal/competitions"},
        ]},
        {"name": "Shop", "path": "/shop", "children": [
            {"name": "All Products", "path": "/shop"},
            {"name": "Buy Match Tickets", "path": f"{t}/matches", "is_external": True},
            {"name": "Official Replicas", "path": "/shop/replicas"},
            {"name": "Legends Collection", "path": "/shop/legends"},
            {"name": "Training Wear", "path": "/shop/training"},
            {"name": "Accessories", "path": "/shop/accessories"},
            {"name": "My Cart", "path": "/cart"},
            {"name": "Physical Store Locations", "path": "/shop/locations"},
        ]},
        {"name": "About FAZ", "path": "/about", "children": [
            {"name": "History", "path": "/about/history"},
            {"name": "Mission & Vision", "path": "/about/mission"},
            {"name": "FAZ Staff", "path": "/staff"},
            {"name": "Committees", "path": "/committees"},
            {"name": "Partners", "path": "/partners"},
        ]},
        {"name": "Governance", "path": "/governance", "children": [
            {"name": "Executive Committee", "path": "/governance/excom"},
            {"name": "General Assembly", "path": "/governance/assembly"},
            {"name": "Statutes & Regulations", "path": "/documents"},
            {"name": "Disciplinary Code", "path": "/documents/disciplinary"},
        ]},
        {"name": "Media", "path": "/media", "children": [
            {"name": "News", "path": "/news"},
            {"name": "Videos", "path": "/media/videos"},
            {"name": "Galleries", "path": "/media/galleries"},
            {"name": "Media Accreditation", "path": "/media/accreditation"},
        ]},
        {"name": "Development", "path": "/development", "children": [
            {"name": "Grassroots", "path": "/development/grassroots"},
            {"name": "Coach Education", "path": "/development/coaches"},
            {"name": "Referee Development", "path": "/development/referees"},
            {"name": "Women in Football", "path": "/development/women"},
        ]},
        {"name": "Leagues", "path": "/leagues", "children": [
            {"name": "All Leagues", "path": "/leagues"},
            {"name": "Men's Super League", "path": "/leagues/1"},
            {"name": "Women's Super League", "path": "/leagues/3"},
        ]},
    ]


def _default_footer_payload():
    t = _tickets_base()
    return [
        {"title": "Quick Links", "links": [
            {"label": "Buy Match Tickets", "path": f"{t}/matches", "is_external": True},
            {"label": "About FAZ", "path": "/about"},
            {"label": "Governance", "path": "/governance"},
            {"label": "News", "path": "/news"},
            {"label": "Matches", "path": "/matches"},
            {"label": "Clubs", "path": "/clubs"},
            {"label": "National Teams", "path": "/national-teams"},
            {"label": "Competitions", "path": "/competitions"},
            {"label": "Contact", "path": "/contact"},
            {"label": "Players", "path": "/players"},
        ]},
    ]


def _insert_nav_tree(items, parent_id=None):
    for i, item in enumerate(items):
        node = NavItem(
            label=item["name"],
            path=item.get("path"),
            parent_id=parent_id,
            item_order=i,
            is_active=True,
            is_external=item.get("is_external", False),
        )
        db.session.add(node)
        db.session.flush()  # get id for children
        if item.get("children"):
            _insert_nav_tree(item["children"], node.id)


@bp.route('/admin/seed-nav-defaults', methods=['POST'])
@jwt_required()
@admin_required
def admin_seed_nav_defaults():
    if NavItem.query.count() > 0:
        abort(409, "Nav items already exist. Delete them first if you want to reseed.")
    _insert_nav_tree(_default_nav_payload())
    db.session.commit()
    return jsonify({"message": "Default navigation seeded"}), 201


@bp.route('/admin/seed-footer-defaults', methods=['POST'])
@jwt_required()
@admin_required
def admin_seed_footer_defaults():
    if FooterSection.query.count() > 0:
        abort(409, "Footer sections already exist. Delete them first if you want to reseed.")
    for i, sec in enumerate(_default_footer_payload()):
        section = FooterSection(title=sec["title"], section_order=i, is_active=True)
        db.session.add(section); db.session.flush()
        for j, link in enumerate(sec["links"]):
            db.session.add(FooterLink(
                section_id=section.id,
                label=link["label"],
                path=link.get("path"),
                is_external=link.get("is_external", False),
                link_order=j,
                is_active=True,
            ))
    db.session.commit()
    return jsonify({"message": "Default footer seeded"}), 201