from database import SessionLocal
from models import Opportunity

db = SessionLocal()

# 1. Make every type lowercase
for o in db.query(Opportunity).all():
    if o.type != o.type.lower():
        print(f"{o.id}: '{o.type}' -> '{o.type.lower()}'")
        o.type = o.type.lower()

# 2. Delete ID 17 if it duplicates the seeded Smart India Hackathon
dup = db.query(Opportunity).filter(Opportunity.id == 17).first()
if dup and dup.title == "Smart India Hackathon":
    print("Deleting duplicate:", dup.id, dup.title)
    db.delete(dup)

db.commit()
db.close()