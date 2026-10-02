from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
from models import Opportunity

# Create the database tables (runs once, safe to leave in)
Base.metadata.create_all(bind=engine)

app = FastAPI()

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