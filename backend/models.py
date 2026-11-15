from sqlalchemy import Column, Integer, String, Date
from database import Base


class Opportunity(Base):
    __tablename__ = "opportunities"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    type = Column(String)
    skills = Column(String)
    deadline = Column(String)
    link = Column(String, nullable=True)


class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    year = Column(String)
    skills = Column(String)


class ReminderLog(Base):
    __tablename__ = "reminder_log"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, index=True)
    opportunity_id = Column(Integer, index=True)
    sent_on = Column(Date)