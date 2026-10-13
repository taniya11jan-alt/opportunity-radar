from database import SessionLocal
from models import Opportunity

db = SessionLocal()
for o in db.query(Opportunity).filter(Opportunity.title == "Techfest").all():
    o.skills = "programming,robotics,web development,python,java"
    print("Updated:", o.id, o.skills)
db.commit()
db.close()