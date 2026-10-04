from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
from models import Opportunity, Student
from matching import calculate_match_score

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
    new_opp = Opportunity(title=title, type=type, skills=skills, deadline=deadline)
    db.add(new_opp)
    db.commit()
    db.refresh(new_opp)
    return new_opp

@app.get("/opportunities")
def get_opportunities(db: Session = Depends(get_db)):
    return db.query(Opportunity).all()

@app.post("/students")
def create_student(name: str, email: str, year: str, skills: str, db: Session = Depends(get_db)):
    new_student = Student(name=name, email=email, year=year, skills=skills)
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
        score = calculate_match_score(student.skills, opp.skills)
        results.append({
            "opportunity_id": opp.id,
            "title": opp.title,
            "type": opp.type,
            "deadline": opp.deadline,
            "match_score": score
        })

    # Sort by match_score, highest first
    results.sort(key=lambda x: x["match_score"], reverse=True)

    return {
        "student": student.name,
        "matches": results
    }