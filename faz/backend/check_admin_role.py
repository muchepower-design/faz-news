from app.database import SessionLocal
from app.models import User

db = SessionLocal()
admin = db.query(User).filter(User.username == "admin").first()
if admin:
    print(f"Admin role: {admin.role} (type: {type(admin.role)})")
else:
    print("Admin not found")
db.close()