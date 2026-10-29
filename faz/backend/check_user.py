# backend/check_user.py
from app.database import SessionLocal
from app.models import User

db = SessionLocal()
user = db.query(User).filter(User.username == "admin").first()
if user:
    print(f"User found: {user.username}, email: {user.email}, is_admin: {user.is_admin}")
    print(f"Password hash: {user.hashed_password[:50]}...")
else:
    print("No admin user found. Run init_db.py again.")
db.close()