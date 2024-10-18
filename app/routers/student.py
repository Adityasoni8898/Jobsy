from .. import models
from sqlalchemy.orm import Session
from .. database import get_db
import shutil
import os
from typing import Optional
from fastapi import UploadFile, File, Form, Depends, APIRouter,  HTTPException, status
from ..oauth2 import get_current_user 

router = APIRouter(
    prefix="/user",
    tags=["Users"]
)

@router.post("/students/")
async def create_student(
    name: str = Form(...),
    cgpa: float = Form(...),
    domain_of_interest: Optional[str] = Form(None),
    job_type: str = Form(...),
    preferred_location: Optional[str] = Form(None),
    availability: Optional[str] = Form(None),
    phone_number: str = Form(..., pattern=r'^\+?[1-9]\d{1,12}$'),
    resume: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)  # Require login to access this route
):
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    resume_dir = "resumes"
    if not os.path.exists(resume_dir):
        os.makedirs(resume_dir)

    resume_filename = f"{resume_dir}/{name}_resume_{resume.filename}"
    with open(resume_filename, "wb") as buffer:
        shutil.copyfileobj(resume.file, buffer)

    new_student = models.Student(
        name=name,
        cgpa=cgpa,
        domain_of_interest=domain_of_interest,
        job_type=job_type,
        preferred_location=preferred_location,
        availability=availability,
        phone_number=phone_number, 
        resume_path=resume_filename
    )

    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    return {"message": "Student created successfully", "student_id": new_student.id}