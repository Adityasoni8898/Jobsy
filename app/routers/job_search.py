from .. import models
from sqlalchemy.orm import Session
from .. database import get_db
from fastapi import Form, Depends, APIRouter, HTTPException, requests
from ..models import Student
from .. import schemas, utils
import spacy, json

router = APIRouter(
    prefix="/user",
    tags=["Users"]
)


nlp = spacy.load('en_core_web_md')

# New endpoint for job posting and matching students
@router.post("/job_search/")
async def job_posting(
    company_name: str = Form(...),
    job_type: str = Form(...),
    branch : str = Form(...),
    cgpa : float = Form(...),
    gender : str = Form(...),
    job_description: str = Form(...),
    db: Session = Depends(get_db)
):

    # 1. Filter students based on CGPA, branch, and gender
    branch_list = branch.split()
    print(branch_list)
    
    # Create a filter for gender based on the input
    gender_filter = (Student.gender == gender) if gender != "both" else True

    # Query filtered students based on inputs
    filtered_students = db.query(Student).filter(
        Student.cgpa >= cgpa,
        Student.branch.in_(branch_list),  # Check if any word matches the student's branch
        gender_filter
    ).all()
    
    if not filtered_students:
        raise HTTPException(status_code=404, detail="No students found")


    # 2. Use Spacy to calculate text similarity between job description and resume data
    job_desc_doc = nlp(job_description)
    
    results = []
    
    for student in filtered_students:
        # No need to parse resume_data as it's already a dictionary
        resume_data = student.resume_data
        
        # Join the content of resume_data into a single string
        resume_text = " ".join([
            " ".join(resume_data.get("Skills", [])),
            " ".join(resume_data.get("Projects", [])),
            " ".join(resume_data.get("Achievements", [])),
            " ".join(resume_data.get("Work experience", [])),
            " ".join(resume_data.get("Certifications", []))
        ])
        
        # Calculate similarity between job description and resume text
        job_desc_doc = nlp(job_description)
        resume_doc = nlp(resume_text)
        
        # Calculate percentage match
        similarity = job_desc_doc.similarity(resume_doc) * 100
        
        # Store the student and their match percentage
        results.append({
            "student_id": student.id,
            "name": student.name,  
            "phone_number" : student.phone_number,
            "match_percentage": similarity
        })

    return results