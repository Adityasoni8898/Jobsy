from pydantic import BaseModel
from typing import Optional

class StudentCreate(BaseModel):
    name: str
    cgpa: float
    branch : str
    domain_of_interest: Optional[str]
    job_type: str
    preferred_location: Optional[str]
    phone_number: str 
    gender : str
    min_package : int

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        orm_mode = True

class JobSearchRequest(BaseModel):
    company_name: str
    job_type: str
    branch : str
    cgpa : float
    job_description: str

class JobMatchResponse(BaseModel):
    student_name: str
    percentage_match: float