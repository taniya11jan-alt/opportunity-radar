import re
from database import SessionLocal
from models import Opportunity

db = SessionLocal()
changed = 0
for o in db.query(Opportunity).all():
    parts = [s.strip() for s in (o.skills or "").split(",")]
    # drop prize text and the number fragments left over from splitting "3,00,000"
    kept = [s for s in parts
            if s and not re.search(r"prize|worth", s, re.IGNORECASE)
            and not re.fullmatch(r"[\d\s]+", s)]
    new = ",".join(kept) if kept else "general"
    if new != o.skills:
        print(o.title, "->", new)
        o.skills = new
        changed += 1
db.commit()
db.close()
print("Updated", changed)