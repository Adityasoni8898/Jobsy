from pydantic import BaseModel, EmailStr
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

class UserBase(BaseModel):
    user_name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    
    class Config:
        from_attributes = True

class UserOut(BaseModel):
    id: int
    user_name: str
    email: str

    class Config:
        from_attributes = True

class JobSearchRequest(BaseModel):
    company_name: str
    job_type: str
    branch : str
    cgpa : float
    job_description: str

class JobMatchResponse(BaseModel):
    student_name: str
    percentage_match: float