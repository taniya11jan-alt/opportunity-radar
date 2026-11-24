from sqlalchemy import text
from database import engine

with engine.begin() as conn:
    cols = [r[1] for r in conn.execute(text("PRAGMA table_info(students)"))]
    if "email_opt_in" not in cols:
        conn.execute(text("ALTER TABLE students ADD COLUMN email_opt_in INTEGER DEFAULT 1"))
print("email_opt_in ready")