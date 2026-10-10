from database import SessionLocal
from models import Opportunity

db = SessionLocal()
for o in db.query(Opportunity).filter(Opportunity.type.notin_(["hackathon", "internship"])).all():
    print(o.id, o.type, "|", o.title, "|", o.deadline)
db.close()