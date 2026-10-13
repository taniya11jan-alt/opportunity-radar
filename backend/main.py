from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
from models import Opportunity, Student
from matching import calculate_final_score

# Create the database tables (runs once, safe to leave in)
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency: gives each request its own database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Opportunity Radar API is running"}

@app.post("/opportunities")
def create_opportunity(title: str, type: str, skills: str, deadline: str, db: Session = Depends(get_db)):
    skill_list = [s.strip() for s in skills.split(",") if s.strip()]
    if len(skill_list) < 2:
        raise HTTPException(status_code=400, detail="Please enter at least 2 skills, separated by commas.")

    new_opp = Opportunity(
        title=title.strip(),
        type=type.strip().lower(),
        skills=",".join(skill_list),
        deadline=deadline
    )
    db.add(new_opp)
    db.commit()
    db.refresh(new_opp)
    return new_opp

@app.get("/opportunities")
def get_opportunities(db: Session = Depends(get_db)):
    return db.query(Opportunity).all()

@app.post("/students")
def create_student(name: str, email: str, year: str, skills: str, db: Session = Depends(get_db)):
    email_clean = email.strip().lower()
    skill_list = [s.strip() for s in skills.split(",") if s.strip()]

    if not name.strip() or "@" not in email_clean:
        raise HTTPException(status_code=400, detail="Please enter a name and a valid email.")
    if len(skill_list) < 2:
        raise HTTPException(status_code=400, detail="Please enter at least 2 skills, separated by commas.")

    existing = db.query(Student).filter(Student.email == email_clean).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"This email is already registered. Your student ID is {existing.id}."
        )

    new_student = Student(name=name.strip(), email=email_clean,
                          year=year.strip(), skills=",".join(skill_list))
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student

@app.get("/students")
def get_students(db: Session = Depends(get_db)):
    return db.query(Student).all()

@app.get("/students/{student_id}/matches")
def get_matches(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        return {"error": "Student not found"}

    opportunities = db.query(Opportunity).all()

    results = []
    for opp in opportunities:
        scores = calculate_final_score(student.skills, opp.skills, opp.deadline)
        results.append({
            "opportunity_id": opp.id,
            "title": opp.title,
            "type": opp.type,
            "deadline": opp.deadline,
            "skills": opp.skills,
            "skill_score": scores["skill_score"],
            "urgency_score": scores["urgency_score"],
            "match_score": scores["final_score"]
        })

    results.sort(key=lambda x: x["match_score"], reverse=True)

    return {"student": student.name, "matches": results}