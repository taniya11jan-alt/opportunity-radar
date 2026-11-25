# Opportunity Radar

A web app that matches students to hackathons, internships and coding contests based on their skills and deadlines, instead of making them search across many separate sites.

## The problem

Opportunities are scattered across platforms such as Devpost, Unstop and Codeforces. Students miss ones that suit them, usually because they find out too late, and general listing sites show the same list to everyone.

## How it works

1. Scrapers collect live listings from three sources and store them in one database.
2. Students create an account, list their skills, and can edit them later on the profile page.
3. Every opportunity gets a score: **70% skill fit + 30% deadline urgency**.
4. Skill fit compares the student's skills with the opportunity's skills using substring matching, so "machine learning" matches "Machine Learning/AI".
5. Results are ranked and each card shows its skill and urgency breakdown, so no ranking is a black box.
6. A daily job emails opted-in students about strong matches closing within 7 days.

## Features

- Sign up and log in (salted PBKDF2 password hashes, signed expiring tokens)
- Personalised, ranked matches with type filters and direct "View & apply" links
- Profile page where students update their name, year, skills and password, and switch email reminders on or off
- Live scrapers for Devpost and Unstop (Selenium) and Codeforces (official API)
- Duplicate detection, title and skill cleaning, and removal of expired listings
- Admin page, restricted on the server to admin accounts, for adding listings the scrapers miss
- Email reminders with a log that prevents repeats, an unsubscribe link and a per-run send cap
- Daily automation through Windows Task Scheduler

## Tech stack

- **Backend:** Python, FastAPI, SQLAlchemy, SQLite
- **Frontend:** HTML, CSS, JavaScript, Bootstrap 5 (dark theme)
- **Scraping:** Selenium (Devpost, Unstop), `requests` (Codeforces API)
- **Email:** Gmail SMTP
- **Scheduling:** Windows Task Scheduler

## Project structure

```
opportunity-radar/
├── backend/
│   ├── main.py            API endpoints (signup, login, profile, matches, unsubscribe)
│   ├── models.py          Opportunity, Student, ReminderLog tables
│   ├── database.py        Database connection
│   ├── matching.py        Skill and urgency scoring
│   ├── auth.py            Password hashing and tokens
│   ├── skill_map.py       Role-to-skills mapping for internships
│   ├── reminders.py       Email reminders
│   ├── make_admin.py      Make an account an admin
│   └── requirements.txt
├── scraper/
│   ├── devpost_scraper.py
│   ├── unstop_scraper.py
│   ├── codeforces_scraper.py
│   ├── run_all.py         Runs all scrapers, then reminders, then cleanup
│   └── run_scrape.bat     Launcher used by Task Scheduler
└── frontend/
    ├── index.html  login.html  signup.html  matches.html  profile.html  admin.html
    ├── auth.js     style.css
```

## Setup

Requires Python 3.10+ and Google Chrome.

```bash
git clone https://github.com/taniya11jan-alt/opportunity-radar.git
cd opportunity-radar
python -m venv venv
venv\Scripts\activate
pip install -r backend/requirements.txt
```

Create `backend/.env` (never commit this file):

```
SECRET_KEY=a-long-random-string
GMAIL_USER=your-email@gmail.com
GMAIL_APP_PASSWORD=your-16-character-app-password
BASE_URL=http://127.0.0.1:8000
```

The Gmail app password is created at myaccount.google.com/apppasswords and needs 2-Step Verification.

## Running

**Backend** (from `backend`):

```bash
uvicorn main:app --reload
```

**Frontend:** serve the `frontend` folder (for example with the VS Code Live Server extension) and open `index.html`.

**Create the first admin:** sign up on the site, then run:

```bash
python make_admin.py your-email@example.com
```

**Scrapers and reminders** (from `scraper`):

```bash
python run_all.py
```

Reminders can also be run on their own from `backend`:

```bash
python reminders.py                        # preview only
python reminders.py --send --to me@x.com   # send to one address
python reminders.py --send --all           # send to all opted-in students
```

**Daily automation:** create a Task Scheduler task that runs `scraper/run_scrape.bat` every morning. Results are written to `scraper/scrape_log.txt`.

## Limitations

- Unstop shows "days left" instead of a date, so its deadlines are approximate (today plus days left at scrape time).
- Internship skills come from titles plus a hand-written mapping, which is a heuristic.
- Substring matching has false positives (for example `java` inside `javascript`) and cannot link related terms such as "ML" and "machine learning".
- Scrapers fetch one listing page per source per run and depend on each site's page layout, which can change.
- Unsubscribe links point to `127.0.0.1` until the backend is deployed and `BASE_URL` is set.
- Gmail limits sending to roughly 500 emails a day.

## Future work

- Semantic skill matching with embeddings (`sentence-transformers`)
- Deployment of the API and frontend, with scraping kept on a local machine
- Password reset and more data sources

## Author

Taniya Yadav
