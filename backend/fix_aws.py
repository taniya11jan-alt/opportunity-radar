from database import SessionLocal
from models import Opportunity

db = SessionLocal()
for opp in db.query(Opportunity).all():
    if opp.title.startswith("AWS Communication Developer Services") and "(CDS)" not in opp.title:
        opp.title = "AWS Communication Developer Services (CDS) Agentic AI Partner Hackathon"
        print("Restored:", opp.title)
db.commit()
db.close()