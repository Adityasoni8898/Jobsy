from .. import models, utils
from sqlalchemy.orm import Session
from .. database import get_db
import shutil
import os
from typing import Optional
from fastapi import UploadFile, File, Form, Depends, APIRouter,  HTTPException, status
from ..oauth2 import get_current_user 

api_key = "aff_affc7a852045b8f9b6d570a5379cd0aca30a5384"

router = APIRouter(
    prefix="/user",
    tags=["Users"]
)

@router.post("/students/")
async def create_student(
    name: str = Form(...),
    cgpa: float = Form(...),
    branch : str = Form(...),
    domain_of_interest: Optional[str] = Form(None),
    job_type: str = Form(...),
    preferred_location: Optional[str] = Form(None),
    phone_number: str = Form(..., pattern=r'^\+?[1-9]\d{1,12}$'),
    resume: UploadFile = File(...),
    min_package: int = Form(...),
    gender: str = Form(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)  # Require login to access this route
):
    
    resume_dir = "resumes"
    if not os.path.exists(resume_dir):
        os.makedirs(resume_dir)

    # Save the resume file
    resume_filename = f"{resume_dir}/{name}_resume_{resume.filename}"
    with open(resume_filename, "wb") as buffer:
        shutil.copyfileobj(resume.file, buffer)

    # Send the resume file to Affinda API for parsing
    resume_data = utils.parse_resume_with_affinda(resume_filename)
    
    if not resume_data:
        return {"message": "Failed to parse resume"}
    
    info = utils.extract_info(resume_data)

    new_student = models.Student(
        name=name,
        cgpa=cgpa,
        branch = branch,
        domain_of_interest=domain_of_interest,
        job_type=job_type,
        preferred_location=preferred_location,
        phone_number=phone_number, 
        resume_path=resume_filename,
        resume_data = info,
        min_package = min_package,
        gender = gender
    )

    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    return {"message": "Student created successfully", "student_id": new_student.id}