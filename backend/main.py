from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import engine, SessionLocal, Base
from models import Opportunity, Student
from matching import calculate_final_score
from auth import hash_password, verify_password, make_token, read_token, read_unsub_token
from fastapi.responses import HTMLResponse

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def current_student(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Please log in.")
    sid = read_token(authorization[7:])
    student = db.query(Student).filter(Student.id == sid).first() if sid else None
    if not student:
        raise HTTPException(status_code=401, detail="Session expired. Please log in again.")
    return student


def admin_only(student: Student = Depends(current_student)):
    if not student.is_admin:
        raise HTTPException(status_code=403, detail="Admins only.")
    return student


class SignupIn(BaseModel):
    name: str
    email: str
    year: str
    skills: str
    password: str
    email_opt_in: bool = True


class LoginIn(BaseModel):
    email: str
    password: str


@app.get("/")
def read_root():
    return {"message": "Opportunity Radar API is running"}


@app.post("/signup")
def signup(data: SignupIn, db: Session = Depends(get_db)):
    email = data.email.strip().lower()
    skill_list = [skill.strip() for skill in data.skills.split(",") if skill.strip()] 

    if not data.name.strip() or "@" not in email:
        raise HTTPException(status_code=400, detail="Please enter a name and a valid email.")
    if len(skill_list) < 2:
        raise HTTPException(status_code=400, detail="Please enter at least 2 skills, separated by commas.")
    if len(data.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")
    if db.query(Student).filter(Student.email == email).first():
        raise HTTPException(status_code=409, detail="This email is already registered. Please log in.")

    student = Student(
        name=data.name.strip(),
        email=email,
        year=data.year.strip(),
        skills=",".join(skill_list),
        password_hash=hash_password(data.password),
        is_admin=0,
        email_opt_in=1 if data.email_opt_in else 0,
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return {
        "token": make_token(student.id),
        "name": student.name,
        "is_admin": bool(student.is_admin),
    }


@app.post("/login")
def login(data: LoginIn, db: Session = Depends(get_db)):
    s = db.query(Student).filter(Student.email == data.email.strip().lower()).first()
    if not s or not s.password_hash or not verify_password(data.password, s.password_hash):
        raise HTTPException(status_code=401, detail="Wrong email or password.")
    return {"token": make_token(s.id), "name": s.name, "is_admin": bool(s.is_admin)}


class ProfileIn(BaseModel):
    name: str
    year: str
    skills: str
    password: Optional[str] = None  


@app.get("/me")
def get_me(student: Student = Depends(current_student)):
    return {"name": student.name, "email": student.email,
            "year": student.year, "skills": student.skills}


@app.put("/me")
def update_me(data: ProfileIn, student: Student = Depends(current_student),
              db: Session = Depends(get_db)):
    skill_list = [s.strip() for s in data.skills.split(",") if s.strip()]
    if not data.name.strip():
        raise HTTPException(status_code=400, detail="Please enter your name.")
    if len(skill_list) < 2:
        raise HTTPException(status_code=400, detail="Please enter at least 2 skills, separated by commas.")
    if data.password:
        if len(data.password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")
        student.password_hash = hash_password(data.password)

    student.name = data.name.strip()
    student.year = data.year.strip()
    student.skills = ",".join(skill_list)
    db.commit()
    return {"name": student.name, "skills": student.skills}

@app.get("/opportunities")
def get_opportunities(db: Session = Depends(get_db)):
    return db.query(Opportunity).all()


@app.post("/opportunities")
def create_opportunity(title: str, type: str, skills: str, deadline: str, link: str = "",
                       db: Session = Depends(get_db), admin: Student = Depends(admin_only)):
    skill_list = [s.strip() for s in skills.split(",") if s.strip()]
    if len(skill_list) < 2:
        raise HTTPException(status_code=400, detail="Please enter at least 2 skills, separated by commas.")
    link = link.strip()
    if link and not link.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="Link must start with http:// or https://")

    opp = Opportunity(title=title.strip(), type=type.strip().lower(),
                      skills=",".join(skill_list), deadline=deadline, link=link or None)
    db.add(opp)
    db.commit()
    db.refresh(opp)
    return opp


@app.get("/me/matches")
def my_matches(student: Student = Depends(current_student), db: Session = Depends(get_db)):
    results = []
    for opp in db.query(Opportunity).all():
        sc = calculate_final_score(student.skills, opp.skills, opp.deadline)
        results.append({
            "opportunity_id": opp.id, "title": opp.title, "type": opp.type,
            "deadline": opp.deadline, "skills": opp.skills, "link": opp.link,
            "skill_score": sc["skill_score"], "urgency_score": sc["urgency_score"],
            "match_score": sc["final_score"],
        })
    results.sort(key=lambda x: x["match_score"], reverse=True)
    return {"student": student.name, "matches": results}

@app.get("/unsubscribe", response_class=HTMLResponse)
def unsubscribe(t: str, db: Session = Depends(get_db)):
    sid = read_unsub_token(t)
    s = db.query(Student).filter(Student.id == sid).first() if sid else None
    if not s:
        return HTMLResponse("<h3>This unsubscribe link is not valid.</h3>", status_code=400)
    s.email_opt_in = 0
    db.commit()
    return HTMLResponse("<h3>You have been unsubscribed from reminder emails.</h3>"
                        "<p>You can turn them back on from the My Matches page.</p>")


@app.get("/me/email-pref")
def get_pref(student: Student = Depends(current_student)):
    return {"email_opt_in": student.email_opt_in != 0}


@app.put("/me/email-pref")
def set_pref(opt_in: bool, student: Student = Depends(current_student), db: Session = Depends(get_db)):
    student.email_opt_in = 1 if opt_in else 0
    db.commit()
    return {"email_opt_in": opt_in}