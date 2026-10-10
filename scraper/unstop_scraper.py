import os
import re
import sys
import time
from datetime import date, timedelta

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
from database import SessionLocal
from models import Opportunity

URL = "https://unstop.com/internship?oppstatus=open"
HEADLESS = False
DRY_RUN = False   # set to False to actually save to the database

NOT_SKILLS = {"fresher", "management", "postgraduate", "undergraduate",
              "graduate", "experienced"}


def parse_days_left(text):
    m = re.search(r"(\d+)\s+day", text, flags=re.IGNORECASE)
    if m:
        return int(m.group(1))
    if re.search(r"hour|today|minute", text, flags=re.IGNORECASE):
        return 0
    return None


def is_salary(text):
    """Matches things like '12 K -', '15 K/Month', '30K/Month'."""
    return bool(re.search(r"\d\s*K\b|/\s*month", text, flags=re.IGNORECASE))


def title_to_skill(title):
    """'Python Internship' -> 'python'."""
    t = re.sub(r"\binternship\b", "", title, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", t).strip().lower()


start = time.time()
options = Options()
if HEADLESS:
    options.add_argument("--headless=new")
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(options=options)

driver.get(URL)
try:
    WebDriverWait(driver, 25).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "app-competition-listing a.item"))
    )
except Exception:
    print("Cards never appeared. Page title:", driver.title)

for _ in range(3):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

raw = driver.execute_script("""
    return Array.from(document.querySelectorAll('app-competition-listing a.item')).map(a => ({
        title: (a.querySelector('h3') || {}).innerText || '',
        company: (a.querySelector('p.single-wrap') || {}).innerText || '',
        skills: (a.querySelector('.skill_list') || {}).innerText || '',
        dates: (a.querySelector('.dates-fields') || {}).innerText || ''
    }));
""")
driver.quit()
print(f"Found {len(raw)} cards in {time.time() - start:.1f}s\n")

items = []
for r in raw:
    days = parse_days_left(r["dates"])
    if days is None or not r["title"].strip():
        continue

    tags = [s.strip() for s in r["skills"].split("\n") if s.strip()]
    tags = [s for s in tags if s.lower() not in NOT_SKILLS
            and not is_salary(s) and not re.fullmatch(r"\+\d+", s)]

    skills = [title_to_skill(r["title"])] + [t.lower() for t in tags]
    skills = list(dict.fromkeys(s for s in skills if s))   # de-duplicate, keep order

    title = r["title"].strip()
    company = r["company"].strip()
    full_title = f"{title} - {company}" if company else title

    items.append({
        "title": full_title,
        "skills": ",".join(skills) if skills else "general",
        "deadline": (date.today() + timedelta(days=days)).isoformat(),
    })

for it in items:
    print(it["deadline"], "|", it["title"], "|", it["skills"])

if DRY_RUN:
    print("\nDRY_RUN is on: nothing was saved.")
else:
    db = SessionLocal()
    saved = 0
    for it in items:
        if db.query(Opportunity).filter(Opportunity.title == it["title"]).first():
            continue
        db.add(Opportunity(title=it["title"], type="internship",
                           skills=it["skills"], deadline=it["deadline"]))
        saved += 1
    db.commit()
    db.close()
    print(f"\nSaved {saved} new internships.")