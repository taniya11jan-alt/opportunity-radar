import sys
from database import SessionLocal
from models import Student

email = sys.argv[1].strip().lower()
db = SessionLocal()
s = db.query(Student).filter(Student.email == email).first()
if s:
    s.is_admin = 1
    db.commit()
    print("Admin set for", s.email)
else:
    print("No student with that email. Sign up first, then run this.")
db.close()