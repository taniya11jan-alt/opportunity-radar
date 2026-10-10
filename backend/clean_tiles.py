import re
from database import SessionLocal
from models import Opportunity

def clean_title(title):
    """Removes bracketed prize text like '($400,000 in prizes!)' only."""
    title = re.sub(r"\([^)]*prize[^)]*\)", "", title, flags=re.IGNORECASE)
    title = re.sub(r"\s*[-–—]\s*$", "", title)   # dangling dash at the end
    title = re.sub(r"\s+", " ", title)           # collapse double spaces
    return title.strip()

db = SessionLocal()
changed = 0

for opp in db.query(Opportunity).all():
    new_title = clean_title(opp.title)
    if new_title and new_title != opp.title:
        print(f"{opp.title}  ->  {new_title}")
        opp.title = new_title
        changed += 1

db.commit()
db.close()
print(f"Cleaned {changed} titles")