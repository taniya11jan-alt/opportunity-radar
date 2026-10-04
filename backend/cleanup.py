from database import SessionLocal
from models import Opportunity, Student

db = SessionLocal()

# Delete the old test entries
db.query(Opportunity).filter(Opportunity.title == "Test Hackathon").delete()
db.query(Student).filter(Student.name == "Test 1").delete()

db.commit()
db.close()

print("Test data cleaned up!")