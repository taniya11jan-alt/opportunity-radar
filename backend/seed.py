from database import SessionLocal, engine, Base
from models import Opportunity, Student

# Make sure tables exist
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Sample opportunities
opportunities_data = [
    {"title": "Smart India Hackathon 2026", "type": "hackathon", "skills": "python,machine learning,web development", "deadline": "2026-10-15"},
    {"title": "Google Summer of Code 2027", "type": "internship", "skills": "python,open source,git", "deadline": "2026-11-01"},
    {"title": "HackerEarth DSA Championship", "type": "competition", "skills": "data structures,algorithms,c++", "deadline": "2026-10-20"},
    {"title": "Flipkart GRID Hackathon", "type": "hackathon", "skills": "java,sql,system design", "deadline": "2026-10-25"},
    {"title": "Microsoft Engage Internship", "type": "internship", "skills": "python,cloud,azure", "deadline": "2026-11-10"},
    {"title": "Amazon ML Summer School", "type": "competition", "skills": "machine learning,python,statistics", "deadline": "2026-10-30"},
    {"title": "Devpost Global Hackathon", "type": "hackathon", "skills": "javascript,react,node.js", "deadline": "2026-11-05"},
    {"title": "TCS CodeVita", "type": "competition", "skills": "java,python,algorithms", "deadline": "2026-10-18"},
    {"title": "Adobe Design Challenge", "type": "competition", "skills": "ui design,figma,html,css", "deadline": "2026-11-15"},
    {"title": "IBM Z Datathon", "type": "hackathon", "skills": "data analysis,python,sql", "deadline": "2026-11-20"},
    {"title": "Walmart Sparkathon", "type": "hackathon", "skills": "java,react,machine learning", "deadline": "2026-10-28"},
    {"title": "Cisco Thingqbator", "type": "competition", "skills": "iot,embedded systems,c", "deadline": "2026-11-08"},
    {"title": "Infosys InStep Internship", "type": "internship", "skills": "python,java,sql", "deadline": "2026-12-01"},
    {"title": "Unstop Code Unnati", "type": "competition", "skills": "python,data structures", "deadline": "2026-10-22"},
    {"title": "Meta Hacker Cup", "type": "competition", "skills": "algorithms,c++,python", "deadline": "2026-11-12"},
]

for opp in opportunities_data:
    db.add(Opportunity(**opp))

# Sample students
students_data = [
    {"name": "Taniya Yadav", "email": "taniya@example.com", "year": "3rd year", "skills": "python,machine learning,sql"},
    {"name": "Rahul Sharma", "email": "rahul@example.com", "year": "2nd year", "skills": "java,react,javascript"},
    {"name": "Priya Singh", "email": "priya@example.com", "year": "4th year", "skills": "python,data structures,algorithms"},
]

for student in students_data:
    db.add(Student(**student))

db.commit()
db.close()

print("Seed data added successfully!")