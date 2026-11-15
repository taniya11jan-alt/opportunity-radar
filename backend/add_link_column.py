from sqlalchemy import text
from database import engine

with engine.begin() as conn:
    cols = [row[1] for row in conn.execute(text("PRAGMA table_info(opportunities)"))]
    if "link" in cols:
        print("Column 'link' already exists")
    else:
        conn.execute(text("ALTER TABLE opportunities ADD COLUMN link VARCHAR"))
        print("Added column 'link'")