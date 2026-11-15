from database import SessionLocal
from models import Opportunity

DRY_RUN = False    

db = SessionLocal()
rows = db.query(Opportunity).filter(
    (Opportunity.link == None) | (Opportunity.link == "")
).all()

for o in rows:
    print(o.id, o.type, "|", o.title)

if DRY_RUN:
    print(f"\nDRY_RUN: {len(rows)} rows would be deleted. Nothing changed.")
else:
    for o in rows:
        db.delete(o)
    db.commit()
    print(f"\nDeleted {len(rows)} rows.")
db.close()