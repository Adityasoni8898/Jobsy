from sqlalchemy import Column, String, Float, Integer, JSON
from .database import Base

# SQLAlchemy ORM Model for Database
class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    cgpa = Column(Float, nullable=False)
    branch = Column(String, nullable=False)
    domain_of_interest = Column(String, nullable=True)
    job_type = Column(String, nullable=False)
    preferred_location = Column(String, nullable=True)
    phone_number = Column(String, nullable=False)
    resume_path = Column(String, nullable=False)
    resume_data = Column(JSON, nullable=False)
    gender = Column(String, nullable=False)
    min_package = Column(Integer, nullable=False)


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
