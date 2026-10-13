from database import SessionLocal
from models import Opportunity

db = SessionLocal()
changed = 0
for o in db.query(Opportunity).filter(Opportunity.title.like("Codeforces:%")).all():
    if o.type != "contest":
        o.type = "contest"
        changed += 1
db.commit()
db.close()
print(f"Updated {changed} rows to type 'contest'")