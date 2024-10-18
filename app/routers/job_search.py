from .. import models
from sqlalchemy.orm import Session
from .. database import get_db
from fastapi import Form, Depends, APIRouter

router = APIRouter(
    prefix="/user",
    tags=["Users"]
)

# New endpoint for job posting and matching students
@router.post("/job/")
async def job_posting(
    company_name: str = Form(...),
    job_type: str = Form(...),  # e.g. Full-time, Part-time, etc.
    job_description: str = Form(...),
    db: Session = Depends(get_db)
):
    # Fetch all students from the database
    students = db.query(models.Student).all()

    # Calculate percentage match for each student
    matched_students = []
    for student in students:
    #     # Basic matching logic based on job type and domain of interest
    #     match_percentage = 0
    #     if student.job_type == job_type:
    #         match_percentage += 50  # 50% match if job types are the same
    #     if student.domain_of_interest.lower() in job_description.lower():
    #         match_percentage += 50  # 50% match if domain matches

        # if match_percentage > 0:
            matched_students.append({
                "name": student.name,
                # "cgpa": student.cgpa,
                "domain_of_interest": student.domain_of_interest,
                # "job_type": student.job_type,
                # "preferred_location": student.preferred_location,
                "availability": student.availability,
                "contact_details" : student.phone_number,
                "resume_path": student.resume_path
                # "match_percentage": match_percentage
            })

    return {"company_name": company_name, "job_type": job_type, "job_description": job_description, "matched_students": matched_students}