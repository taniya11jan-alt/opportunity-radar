from database import SessionLocal
from models import Opportunity
from skill_map import expand_skills

db = SessionLocal()
changed = 0

for o in db.query(Opportunity).filter(Opportunity.type == "internship").all():
    current = [s.strip() for s in o.skills.split(",") if s.strip()]
    if not current:
        continue
    role = current[0]                      # the role phrase is always stored first
    updated = list(dict.fromkeys(current + expand_skills(role)))
    if updated != current:
        o.skills = ",".join(updated)
        print(f"{o.title}  ->  {o.skills}")
        changed += 1

db.commit()
db.close()
print(f"\nUpdated {changed} internships")