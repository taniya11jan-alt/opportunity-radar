from sqlalchemy import text
from database import engine

with engine.begin() as conn:
    cols = [r[1] for r in conn.execute(text("PRAGMA table_info(students)"))]
    if "password_hash" not in cols:
        conn.execute(text("ALTER TABLE students ADD COLUMN password_hash VARCHAR"))
    if "is_admin" not in cols:
        conn.execute(text("ALTER TABLE students ADD COLUMN is_admin INTEGER DEFAULT 0"))
print("Auth columns ready")