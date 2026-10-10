import os
import sys
from datetime import datetime, timezone

import requests

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
from database import SessionLocal
from models import Opportunity

DRY_RUN = False

resp = requests.get("https://codeforces.com/api/contest.list", timeout=20)
data = resp.json()
if data.get("status") != "OK":
    raise SystemExit("Codeforces API error")

items = []
for c in data["result"]:
    if c.get("phase") != "BEFORE":        # only upcoming contests
        continue
    start = datetime.fromtimestamp(c["startTimeSeconds"], tz=timezone.utc)
    items.append({
        "title": f"Codeforces: {c['name']}",
        "skills": "algorithms,data structures,competitive programming,c++,python",
        "deadline": start.strftime("%Y-%m-%d"),
    })

for it in items:
    print(it["deadline"], "|", it["title"])

if DRY_RUN:
    print(f"\nDRY_RUN is on: {len(items)} contests found, nothing saved.")
else:
    db = SessionLocal()
    saved = 0
    for it in items:
        if db.query(Opportunity).filter(Opportunity.title == it["title"]).first():
            continue
        db.add(Opportunity(title=it["title"], type="competition",
                           skills=it["skills"], deadline=it["deadline"]))
        saved += 1
    db.commit()
    db.close()
    print(f"\nSaved {saved} new contests.")