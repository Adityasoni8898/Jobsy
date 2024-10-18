from pydantic import BaseModel
from typing import Optional

class StudentCreate(BaseModel):
    name: str
    cgpa: float
    domain_of_interest: Optional[str]
    job_type: str
    preferred_location: Optional[str]
    availability: Optional[str]
    phone_number: str 

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