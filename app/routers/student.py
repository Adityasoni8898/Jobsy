from .. import models, utils
from sqlalchemy.orm import Session
from .. database import get_db
import shutil
import os
from typing import List, Optional
from fastapi import UploadFile, File, Form, Depends, APIRouter,  HTTPException, status
from ..oauth2 import get_current_user 
from ..config import settings

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


@router.get("/students", response_model=None)
async def get_students(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)  # Require login to access this route
):
    students = db.query(models.Student).all()
    return students

# Delete a student by ID
@router.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)  # Require login to access this route
):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    
    db.delete(student)
    db.commit()

    return {"message": "Student deleted successfully"}

# Update a student by ID
@router.put("/students/{student_id}")
async def update_student(
    student_id: int,
    name: Optional[str] = Form(None),
    cgpa: Optional[float] = Form(None),
    branch: Optional[str] = Form(None),
    domain_of_interest: Optional[str] = Form(None),
    job_type: Optional[str] = Form(None),
    preferred_location: Optional[str] = Form(None),
    phone_number: Optional[str] = Form(None, pattern=r'^\+?[1-9]\d{1,12}$'),
    min_package: Optional[int] = Form(None),
    gender: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)  # Require login to access this route
):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    
    # Update only the fields provided
    if name: student.name = name
    if cgpa: student.cgpa = cgpa
    if branch: student.branch = branch
    if domain_of_interest: student.domain_of_interest = domain_of_interest
    if job_type: student.job_type = job_type
    if preferred_location: student.preferred_location = preferred_location
    if phone_number: student.phone_number = phone_number
    if min_package: student.min_package = min_package
    if gender: student.gender = gender

    db.commit()
    db.refresh(student)

    return {"message": "Student updated successfully", "student": student}