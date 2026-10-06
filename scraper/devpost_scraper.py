import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from database import SessionLocal
from models import Opportunity
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time

def parse_deadline(date_range_text):
    try:
        # date_range_text looks like "Aug 31 - Oct 23, 2026"
        end_part = date_range_text.split(" - ")[1]  # "Oct 23, 2026"
        parsed = datetime.strptime(end_part.strip(), "%b %d, %Y")
        return parsed.strftime("%Y-%m-%d")  # "2026-10-23"
    except (IndexError, ValueError):
        return None
    
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

driver.get("https://devpost.com/hackathons")
time.sleep(5)

tiles = driver.find_elements(By.CLASS_NAME, "hackathon-tile")
print(f"Found {len(tiles)} hackathon tiles")

results = []

for tile in tiles:
    try:
        title = tile.find_element(By.TAG_NAME, "h3").text
        link = tile.find_element(By.CLASS_NAME, "tile-anchor").get_attribute("href")

        tag_elements = tile.find_elements(By.CLASS_NAME, "theme-label")
        tags = [tag.text for tag in tag_elements]
        skills = ",".join(tags) if tags else "general"

        date_text = tile.find_element(By.CLASS_NAME, "submission-period").text
        deadline = parse_deadline(date_text)

        results.append({
            "title": title,
            "link": link,
            "skills": skills,
            "deadline": deadline
        })
    except Exception as e:
        print(f"Skipped one tile due to error: {e}")

driver.quit()

# Save to the database
db = SessionLocal()
saved_count = 0

for r in results:
    if r["deadline"] is None:
        continue

    new_opp = Opportunity(
        title=r["title"],
        type="hackathon",
        skills=r["skills"],
        deadline=r["deadline"]
    )
    db.add(new_opp)
    saved_count += 1

db.commit()
db.close()

print(f"\nSaved {saved_count} opportunities to the database!")