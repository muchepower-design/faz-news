from app import create_app
from app.database import db
from app.models import User
from app.auth import get_password_hash
from sqlalchemy import text

app = create_app()

with app.app_context():
    # Create tables only if they don't exist – no data loss
    db.create_all()
    print("✅ Tables created (if missing).")

    # Ensure role column is VARCHAR (if still ENUM, alter it)
    try:
        db.session.execute(text("ALTER TABLE users ALTER COLUMN role TYPE VARCHAR USING role::text;"))
        db.session.commit()
        print("✅ Column role altered to VARCHAR")
    except Exception as e:
        print(f"⚠️ Column role already VARCHAR or error: {e}")

    # Create a default admin user if none exists
    if not User.query.filter_by(email='admin@faz.co.zm').first():
        admin = User(
            email='admin@faz.co.zm',
            username='admin@faz.co.zm',
            full_name='FAZ Administrator',
            role='super_admin',
            is_active=True
        )
        admin.hashed_password = get_password_hash('Admin@123')
        db.session.add(admin)
        db.session.commit()
        print("✅ Default admin created (admin@faz.co.zm / Admin@123)")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)