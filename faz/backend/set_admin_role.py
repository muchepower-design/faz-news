from app.database import SessionLocal
from app.models import User, UserRole

db = SessionLocal()
admin = db.query(User).filter(User.username == "admin").first()
if admin:
    admin.role = UserRole.ADMIN
    db.commit()
    print("Admin role updated to ADMIN")
else:
    print("Admin not found, run init_db.py first")
db.close()