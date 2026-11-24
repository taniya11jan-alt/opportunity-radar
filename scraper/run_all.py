import os
import subprocess
import sys
from datetime import date, datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(HERE, "..", "backend"))
from database import SessionLocal
from models import Opportunity

LOG = os.path.join(HERE, "scrape_log.txt")

JOBS = [
    ("Devpost", ["devpost_scraper.py"]),
    ("Unstop hackathons", ["unstop_scraper.py", "hackathon"]),
    ("Unstop internships", ["unstop_scraper.py", "internship"]),
    ("Codeforces", ["codeforces_scraper.py"]),
]


def log(msg):
    line = f"{datetime.now():%Y-%m-%d %H:%M:%S} | {msg}"
    print(line)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


for name, args in JOBS:
    try:
        r = subprocess.run([sys.executable, os.path.join(HERE, args[0])] + args[1:],
                           capture_output=True, text=True, timeout=300, cwd=HERE)
        last = (r.stdout.strip().splitlines() or ["(no output)"])[-1]
        log(f"{name}: {'OK' if r.returncode == 0 else 'FAILED'} | {last}")
        if r.returncode != 0:
            log(f"   error: {r.stderr.strip()[-300:]}")
    except Exception as e:
        log(f"{name}: crashed | {e}")

# Remove listings that closed more than 3 days ago
db = SessionLocal()
cutoff = (date.today() - timedelta(days=3)).isoformat()
old = db.query(Opportunity).filter(Opportunity.deadline < cutoff).all()
for o in old:
    db.delete(o)
db.commit()
db.close()
log(f"Cleanup: removed {len(old)} expired listings")