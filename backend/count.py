from database import SessionLocal
from models import Opportunity

db = SessionLocal()
total = db.query(Opportunity).count()
print(f"Total opportunities: {total}")
for typ in ["hackathon", "internship"]:
    print(f"\n{typ}: {db.query(Opportunity).filter(Opportunity.type == typ).count()}")
    for opp in db.query(Opportunity).filter(Opportunity.type == typ).order_by(Opportunity.id.desc()).limit(3):
        print("  ", opp.id, opp.title, opp.deadline)
db.close()