from database import SessionLocal
from models import Opportunity

db = SessionLocal()
total = db.query(Opportunity).count()
print(f"Total opportunities: {total}")
for opp in db.query(Opportunity).filter(Opportunity.type == "hackathon").order_by(Opportunity.id.desc()).limit(5):
    print(opp.id, opp.title, opp.deadline)
db.close()