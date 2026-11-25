import os
import smtplib
import sys
from datetime import date, datetime
from email.message import EmailMessage

from dotenv import load_dotenv

from database import SessionLocal, engine, Base
from models import Opportunity, Student, ReminderLog
from matching import calculate_skill_score
from auth import make_unsub_token

Base.metadata.create_all(bind=engine)
load_dotenv()
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")

MIN_SKILL = 0.5            # only strong matches
MAX_DAYS = 7               # deadlines within this many days
MAX_EMAILS_PER_RUN = 100   # Gmail allows roughly 500 a day

# Usage:
#   python reminders.py                         -> preview only
#   python reminders.py --send --to a@b.com     -> send to one address
#   python reminders.py --send --all            -> send to every opted-in student
args = sys.argv[1:]
SEND = "--send" in args
ALL = "--all" in args
TO = args[args.index("--to") + 1].strip().lower() if "--to" in args else None

if SEND and not TO and not ALL:
    raise SystemExit("Refusing to send. Add --to your@email.com or --all.")


def days_left(deadline_str):
    try:
        d = datetime.strptime(deadline_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None
    return (d - date.today()).days


def build_message(student, matches):
    lines = [f"Hi {student.name},", "",
             "These opportunities match your skills and close soon:", ""]
    for opp, skill, days in matches:
        when = "today" if days == 0 else f"in {days} day(s)"
        lines.append(f"- {opp.title} ({opp.type}) closes {when} [{opp.deadline}], skill fit {round(skill * 100)}%")
        if opp.link:
            lines.append(f"  {opp.link}")
    unsub = f"{BASE_URL}/unsubscribe?t={make_unsub_token(student.id)}"
    lines += ["", "Good luck!", "Opportunity Radar", "",
              f"Don't want these emails? Unsubscribe: {unsub}"]

    msg = EmailMessage()
    msg["Subject"] = f"{len(matches)} opportunities closing soon"
    msg["From"] = GMAIL_USER
    msg["To"] = student.email
    msg.set_content("\n".join(lines))
    return msg


db = SessionLocal()
students = db.query(Student).all()
opportunities = db.query(Opportunity).all()
already_sent = {(r.student_id, r.opportunity_id) for r in db.query(ReminderLog).all()}

to_send = []
for s in students:
    if s.email_opt_in == 0:
        continue
    if TO and s.email.strip().lower() != TO:
        continue
    matches = []
    for o in opportunities:
        d = days_left(o.deadline)
        if d is None or d < 0 or d > MAX_DAYS or (s.id, o.id) in already_sent:
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

if not SEND:
    print(f"\nPreview only: {len(to_send)} student(s) would be emailed. Nothing sent.")
elif not GMAIL_USER or not GMAIL_APP_PASSWORD:
    print("Missing GMAIL_USER or GMAIL_APP_PASSWORD in .env")
elif not to_send:
    print("Nothing to send.")
else:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        for s, matches in to_send[:MAX_EMAILS_PER_RUN]:
            server.send_message(build_message(s, matches))
            for o, skill, d in matches:
                db.add(ReminderLog(student_id=s.id, opportunity_id=o.id, sent_on=date.today()))
            db.commit()
            print(f"Sent to {s.email}")
db.close()