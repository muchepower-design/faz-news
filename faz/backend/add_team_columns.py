# backend/add_team_columns.py
from app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text("ALTER TABLE teams ADD COLUMN IF NOT EXISTS gender VARCHAR DEFAULT 'male'"))
    conn.execute(text("ALTER TABLE teams ADD COLUMN IF NOT EXISTS team_type VARCHAR DEFAULT 'club'"))
    conn.execute(text("ALTER TABLE teams ADD COLUMN IF NOT EXISTS current_league_level VARCHAR"))
    conn.execute(text("ALTER TABLE teams ADD COLUMN IF NOT EXISTS league_tier INTEGER DEFAULT 3"))
    conn.commit()
    print("Team columns added successfully.")