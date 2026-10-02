from sqlalchemy import Column, Integer, String
from database import Base

class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    type = Column(String)
    skills = Column(String)
    deadline = Column(String)