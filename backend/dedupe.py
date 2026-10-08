from database import SessionLocal
from models import Opportunity

db = SessionLocal()
seen = set()
removed = 0

for opp in db.query(Opportunity).order_by(Opportunity.id).all():
    if opp.title in seen:
        db.delete(opp)
        removed += 1
    else:
        seen.add(opp.title)

db.commit()
db.close()
print(f"Removed {removed} duplicate entries")