import os
import smtplib
from datetime import date, datetime
from email.message import EmailMessage

from dotenv import load_dotenv

from database import SessionLocal
from models import Opportunity, Student
from matching import calculate_skill_score

load_dotenv()
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

# ---------- Settings ----------
DRY_RUN = False        # True = print only, send nothing
MIN_SKILL = 0.5       
MAX_DAYS = 7         
ONLY_EMAIL = "taniya06.yadav@gmail.com"     # for testing, set to your own address to email only that student


def days_left(deadline_str):
    try:
        d = datetime.strptime(deadline_str, "%Y-%m-%d").date()
    except ValueError:
        return None
    return (d - date.today()).days


def build_message(student, matches):
    lines = [f"Hi {student.name},", "", "These opportunities match your skills and close soon:", ""]
    for opp, skill, days in matches:
        when = "today" if days == 0 else f"in {days} day(s)"
        lines.append(f"- {opp.title} ({opp.type}) closes {when} [{opp.deadline}], skill fit {round(skill * 100)}%")
    lines += ["", "Good luck!", "Opportunity Radar"]

    msg = EmailMessage()
    msg["Subject"] = f"{len(matches)} opportunities closing soon"
    msg["From"] = GMAIL_USER
    msg["To"] = student.email
    msg.set_content("\n".join(lines))
    return msg


db = SessionLocal()
seen_emails = set()
students = []
for s in db.query(Student).all():
    key = s.email.strip().lower()
    if key in seen_emails:
        continue
    seen_emails.add(key)
    students.append(s)
opportunities = db.query(Opportunity).all()

to_send = []
for s in students:
    if ONLY_EMAIL and s.email.strip().lower() != ONLY_EMAIL.lower():
        continue
    matches = []
    for o in opportunities:
        d = days_left(o.deadline)
        if d is None or d < 0 or d > MAX_DAYS:
            continue
        skill = calculate_skill_score(s.skills, o.skills)
        if skill >= MIN_SKILL:
            matches.append((o, skill, d))
    if matches:
        matches.sort(key=lambda m: (m[2], -m[1]))   # soonest first
        to_send.append((s, matches))

for s, matches in to_send:
    print(f"{s.name} <{s.email}>: {len(matches)} match(es)")
    for o, skill, d in matches:
        print(f"   {o.title} | {d} day(s) | {round(skill * 100)}%")
if not DRY_RUN and not ONLY_EMAIL:
    raise SystemExit("Refusing to send to all students. Set ONLY_EMAIL for testing.")
if DRY_RUN:
    print(f"\nDRY_RUN is on: {len(to_send)} student(s) would be emailed, nothing sent.")
elif not GMAIL_USER or not GMAIL_APP_PASSWORD:
    print("Missing GMAIL_USER or GMAIL_APP_PASSWORD in .env")
else:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        for s, matches in to_send:
            server.send_message(build_message(s, matches))
            print(f"Sent to {s.email}")

db.close()