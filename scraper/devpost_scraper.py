import sys
import os
import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Reuse the database setup from the backend folder
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
from database import SessionLocal
from models import Opportunity

# Set to False if the script finds 0 tiles (shows the Chrome window)
HEADLESS = True


def parse_deadline(date_range_text):
    """Handles 'Aug 31 - Oct 23, 2026' and 'Oct 01 - 10, 2026'."""
    try:
        start_part, end_part = [p.strip() for p in date_range_text.split(" - ")]

        # If the end part starts with a digit, it has no month: borrow it from the start
        if end_part[0].isdigit():
            month = start_part.split()[0]          # "Oct"
            end_part = f"{month} {end_part}"       # "Oct 10, 2026"

        parsed = datetime.strptime(end_part, "%b %d, %Y")
        return parsed.strftime("%Y-%m-%d")
    except (IndexError, ValueError):
        print(f"Could not parse date: '{date_range_text}'")
        return None


start = time.time()

# Browser setup
options = Options()
if HEADLESS:
    options.add_argument("--headless=new")
options.add_argument("--window-size=1920,1080")
options.add_argument(
    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
driver = webdriver.Chrome(options=options)
print(f"Browser launched: {time.time() - start:.1f}s")

driver.get("https://devpost.com/hackathons")

# Wait until hackathon tiles appear (up to 20 seconds)
try:
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, "hackathon-tile"))
    )
except Exception:
    print("Tiles never appeared. Page title:", driver.title)

# Scroll down to load more hackathons
for i in range(3):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
print(f"Page ready: {time.time() - start:.1f}s")

# Extract everything in ONE call to the browser (much faster)
raw_tiles = driver.execute_script("""
    return Array.from(document.querySelectorAll('.hackathon-tile')).map(t => ({
        title: (t.querySelector('h3') || {}).innerText || '',
        link: (t.querySelector('a.tile-anchor') || {}).href || '',
        tags: Array.from(t.querySelectorAll('.theme-label')).map(
            x => x.getAttribute('title') || x.textContent.trim()
        ),
        date: (t.querySelector('.submission-period') || {}).innerText || ''
    }));
""")
driver.quit()
print(f"Found {len(raw_tiles)} hackathon tiles. Extraction done: {time.time() - start:.1f}s")

# Save to the database
db = SessionLocal()
saved_count = 0

for t in raw_tiles:
    deadline = parse_deadline(t["date"])
    if not t["title"] or deadline is None:
        continue

    # Skip hackathons that are already stored
    if db.query(Opportunity).filter(Opportunity.title == t["title"]).first():
        continue

    skills = ",".join(t["tags"]) if t["tags"] else "general"
    db.add(Opportunity(
        title=t["title"],
        type="hackathon",
        skills=skills,
        deadline=deadline
    ))
    saved_count += 1

db.commit()
db.close()
print(f"Saved {saved_count} new opportunities. Total time: {time.time() - start:.1f}s")