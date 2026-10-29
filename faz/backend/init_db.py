from app.database import SessionLocal, engine
from app import models
from app.auth import get_password_hash

print("Creating database tables...")
models.Base.metadata.create_all(bind=engine)

db = SessionLocal()
try:
    # Check if admin already exists
    existing_admin = db.query(models.User).filter(models.User.username == "admin").first()
    if existing_admin:
        print("Admin user already exists. Skipping creation.")
    else:
        # Create admin user with role ADMIN
        hashed_pw = get_password_hash("admin123")
        admin = models.User(
            username="admin",
            email="admin@faz.zm",
            full_name="System Administrator",
            hashed_password=hashed_pw,
            role=models.UserRole.ADMIN,   # Use role instead of is_admin
            is_active=True
        )
        db.add(admin)
        db.commit()
        print("Admin user created successfully! (username: admin, password: admin123)")
except Exception as e:
    print(f"Error: {e}")
    db.rollback()
finally:
    db.close()