# backend/test_auth.py
from app.auth import verify_password
from app.database import SessionLocal
from app.models import User

db = SessionLocal()
user = db.query(User).filter(User.username == "admin").first()
if user:
    result = verify_password("admin123", user.hashed_password)
    print(f"Verification result for 'admin123': {result}")
else:
    print("User not found")
db.close()