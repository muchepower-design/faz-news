# app/__init__.py
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from app.database import db
import os
from dotenv import load_dotenv

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.url_map.strict_slashes = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret')
    app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-jwt-secret')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB

    db.init_app(app)
    Migrate(app, db)

    CORS(app)
    JWTManager(app)

    # ---- Blueprint imports ----
    from app.routes import (
        admin, assets, bulk_import, competitions, countries, cups, leagues,
        match_events, matches, media, national_teams, clubs, news,
        players, reports, shop, tables, teams, users, content, uploads
                )
    from app.ticketing import api as ticket_api
    from app.ticketing import auth as ticket_auth
    from app.ticketing import admin as ticket_admin
    from app.ticketing import club as ticket_club
    from app.ticketing import payment as ticket_payment
    from app.routes import competitions_management

    # ---- Static assets: served at the root, NOT under /api ----
    app.register_blueprint(assets.bp, url_prefix='/assets')

    # ---- Everything else under /api ----
    app.register_blueprint(admin.bp, url_prefix='/api/admin')
    app.register_blueprint(bulk_import.bp, url_prefix='/api/bulk-import')
    app.register_blueprint(competitions.bp, url_prefix='/api/competitions')
    app.register_blueprint(competitions_management.bp, url_prefix='/api/competitions-management')
    app.register_blueprint(countries.bp, url_prefix='/api/countries')
    app.register_blueprint(cups.bp, url_prefix='/api/cups')
    app.register_blueprint(leagues.bp, url_prefix='/api/leagues')
    app.register_blueprint(match_events.bp, url_prefix='/api/match-events')
    app.register_blueprint(matches.bp, url_prefix='/api/matches')
    app.register_blueprint(media.bp, url_prefix='/api/media')
    app.register_blueprint(national_teams.bp, url_prefix='/api/national-teams')
    app.register_blueprint(clubs.bp, url_prefix='/api/clubs')
    app.register_blueprint(news.bp, url_prefix='/api/news')
    app.register_blueprint(players.bp, url_prefix='/api/players')
    app.register_blueprint(reports.bp, url_prefix='/api/reports')
    app.register_blueprint(shop.bp, url_prefix='/api/shop')
    app.register_blueprint(tables.bp, url_prefix='/api/league-table')
    app.register_blueprint(teams.bp, url_prefix='/api/teams')
    app.register_blueprint(users.bp, url_prefix='/api/users')
    app.register_blueprint(ticket_api.bp, url_prefix='/api/ticketing')
    app.register_blueprint(ticket_auth.bp, url_prefix='/api/ticketing/auth')
    app.register_blueprint(ticket_admin.bp, url_prefix='/api/ticketing/admin')
    app.register_blueprint(ticket_club.bp, url_prefix='/api/ticketing/club')
    app.register_blueprint(ticket_payment.bp, url_prefix='/api/ticketing/payment')
    app.register_blueprint(content.bp, url_prefix='/api/content')
    app.register_blueprint(uploads.bp, url_prefix='/api/uploads')

    # ------------------------------------------------------------------
    # Seed default roles + backfill legacy users
    # Runs on every startup — cheap no-op when data already exists.
    # ------------------------------------------------------------------
    with app.app_context():
        try:
            from app.models import Role, User

            DEFAULT_ROLES = [
                ('super_admin', 'Super Administrator — full system access'),
                ('faz_admin', 'FAZ Administrator — national teams, clubs, competitions'),
                ('club_admin', 'Club Administrator — manage club operations'),
                ('club_officer', 'Club Officer — manage matches and ticket sales'),
                ('scanner', 'Ticket Scanner — verify tickets at gates'),
                ('customer', 'Customer — browse and buy tickets'),
            ]

            # 1. Ensure every default role exists
            created_any = False
            for name, description in DEFAULT_ROLES:
                if not Role.query.filter_by(name=name).first():
                    db.session.add(Role(name=name, description=description))
                    created_any = True
            if created_any:
                db.session.commit()
                print("[startup] seeded default roles")

            # 2. Backfill users who have a legacy `role` string but no M2M rows
            backfilled = 0
            for user in User.query.all():
                if user.roles:
                    continue
                if user.role:
                    role = Role.query.filter_by(name=user.role).first()
                    if role:
                        user.roles.append(role)
                        backfilled += 1
            if backfilled:
                db.session.commit()
                print(f"[startup] backfilled roles for {backfilled} user(s)")

        except Exception as e:
            db.session.rollback()
            print(f"[startup] role seed failed: {e}")

        try:
            from backend.app.models.content_old import HeroSlide, Partner, GovernanceMember, Page

            # Seed hero slides if empty
            if HeroSlide.query.count() == 0:
                db.session.add_all([
                    HeroSlide(title='Chipolopolo Rising', subtitle='Pride of Zambia',
                              image_url='https://images.unsplash.com/photo-1522778119026-d647f0596c67?w=1600',
                              cta_text='Support the Team', cta_link='/national-teams', slide_order=1),
                    HeroSlide(title='FAZ Super League', subtitle='The best of Zambian football',
                              image_url='https://images.unsplash.com/photo-1459865264687-674d540dc3f7?w=1600',
                              cta_text='View Fixtures', cta_link='/matches', slide_order=2),
                    HeroSlide(title='Grassroots Development', subtitle="Building tomorrow's stars today",
                              image_url='https://images.unsplash.com/photo-1517466787929-bc90951d0974?w=1600',
                              cta_text='Get Involved', cta_link='/about', slide_order=3),
                ])
                db.session.commit()

            # Seed partners if empty
            if Partner.query.count() == 0:
                base = '/assets/partners'
                db.session.add_all([
                    Partner(name='ABSA Zambia', logo_url=f'{base}/partner_absa_zambia.png', partner_order=1),
                    Partner(name='Eden University', logo_url=f'{base}/partner_eden_university.png', partner_order=2),
                    Partner(name='MTN Zambia', logo_url=f'{base}/partner_mtn_zambia.png', partner_order=3),
                    Partner(name='Zambian Breweries', logo_url=f'{base}/partner_zambian_breweries.jpg', partner_order=4),
                    Partner(name='Trade Kings Zambia', logo_url=f'{base}/partner_trade_kings_zambia.jpg', partner_order=5),
                ])
                db.session.commit()

            # Seed default pages if empty
            if Page.query.count() == 0:
                db.session.add_all([
                    Page(path='about/history',          title='Our History',
                         category='about',      content='', is_published=True, page_order=1),
                    Page(path='about/mission',          title='Mission & Vision',
                         category='about',      content='', is_published=True, page_order=2),
                    Page(path='committees',             title='Committees',
                         category='about',      content='', is_published=True, page_order=3),
                    Page(path='partners',               title='Our Partners',
                         category='about',      content='', is_published=True, page_order=4),
                    Page(path='governance/excom',       title='Executive Committee',
                         category='governance', content='', is_published=True, page_order=1),
                    Page(path='documents',              title='Documents',
                         category='documents',  content='', is_published=True, page_order=1),
                    Page(path='documents/disciplinary', title='Disciplinary Code',
                         category='documents',  content='', is_published=True, page_order=2),
                ])
                db.session.commit()
                print("[startup] seeded default pages")
                        # Seed governance members if empty
            if GovernanceMember.query.count() == 0:
                base = '/assets/excom'

                # --- National Executive Committee ---
                national = [
                    ('Keith Mweemba',       'President',                'faz_president.jpg',                 1),
                    ('Mutale Ng’andu',      'Vice President',           'faz_vice_president.jpg',            2),
                    ('Machacha Shepande',   'General Secretary',        'faz_general_secretary.jpg',         3),
                    ('Col. Priscilla Katoba','Women’s Representative',  'faz_womens_representative.jpg',     4),
                ]
                for order, (name, position, filename, _) in enumerate(
                    [(n, p, f, o) for n, p, f, o in national], start=0
                ):
                    pass  # (placeholder — real loop below)

                for name, position, filename, member_order in national:
                    db.session.add(GovernanceMember(
                        name=name,
                        position=position,
                        category='national',
                        image_url=f'{base}/{filename}',
                        term_start='2025',
                        term_end='2029',
                        member_order=member_order,
                        is_active=True,
                    ))

                # --- Provincial Representatives ---
                provincial = [
                    ('Lusaka',         'Jordan Maliti',       'faz_lusaka_province_representative.jpg'),
                    ('Central',        'Chisanga Pule',       'faz_central_province_representative.jpg'),
                    ('Copperbelt',     'Patrick Ndhlovu',     'faz_copperbelt_province_representative.jpg'),
                    ('Luapula',        'Mweemba Mujala',      'faz_luapula_province_representative.jpg'),
                    ('Southern',       'Nicholas Moomba',     'faz_southern_province_representative.jpg'),
                    ('Northern',       'Chikonde Mbalazi',    'faz_northern_province_representative.jpg'),
                    ('Muchinga',       'Samuel Mwape',        'faz_muchinga_province_representative.jpg'),
                    ('North‑Western',  'Brian Sakulen’ga',    'faz_north_western_province_representative.jpg'),
                    ('Western',        'David Simwinga',      'faz_western_province_representative.jpg'),
                    ('Eastern',        'Patrick Nyirenda',    'faz_eastern_province_representative.jpg'),
                ]
                for member_order, (province, name, filename) in enumerate(provincial, start=1):
                    db.session.add(GovernanceMember(
                        name=name,
                        position='Provincial Representative',
                        category='provincial',
                        province=province,
                        image_url=f'{base}/{filename}',
                        term_start='2025',
                        term_end='2029',
                        member_order=member_order,
                        is_active=True,
                    ))

                db.session.commit()
                print("[startup] seeded governance members")

        except Exception as e:
            db.session.rollback()
            print(f"[startup] content seed failed: {e}")

    @app.route('/api/health')
    def health_check():
        return {"status": "healthy", "message": "FAZ API is running"}

    @app.route('/api')
    def root():
        return {"message": "Welcome to Football Association of Zambia API"}

    return app