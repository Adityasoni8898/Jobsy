from .. import models
from sqlalchemy.orm import Session
from .. database import get_db
from fastapi import Form, Depends, APIRouter, HTTPException, requests
from ..models import Student
from .. import schemas, utils
import spacy
from ..oauth2 import get_current_user 

router = APIRouter(
    prefix="/user",
    tags=["Users"]
)




nlp = spacy.load('en_core_web_md')




import pickle
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Load ML model & tokenizer once during startup
with open("app/ml/tokenizer.pkl", "rb") as f:
    tokenizer = pickle.load(f)

model = load_model("app/ml/fraud_detection_model.h5")

# New endpoint for job posting and matching students
@router.post("/job_search/")
async def job_posting(
    company_name: str = Form(...),
    job_title: str = Form(...),
    branch: str = Form(...),
    cgpa: float = Form(...),
    gender: str = Form(...),
    job_description: str = Form(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # **Step 1: ML Fraud Detection**
    job_text = job_title + " " + job_description
    job_seq = tokenizer.texts_to_sequences([job_text])
    job_padded = pad_sequences(job_seq, maxlen=200, padding='post')
    fraud_prob = model.predict(job_padded)[0][0]

    # **If fraud probability > 0.5, reject the job posting**
    if fraud_prob > 0.5:
        raise HTTPException(status_code=400, detail="Job posting detected as fraudulent")

    # **Step 2: Filter students based on CGPA, branch, and gender**
    branch_list = branch.split()
    gender_filter = (Student.gender == gender) if gender != "both" else True

    filtered_students = db.query(Student).filter(
        Student.cgpa >= cgpa,
        Student.branch.in_(branch_list),
        gender_filter
    ).all()

    if not filtered_students:
        raise HTTPException(status_code=404, detail="No students found")

    # **Step 3: Resume Matching**
    job_desc_doc = nlp(job_text)
    results = []

    for student in filtered_students:
        resume_data = student.resume_data
        resume_text = " ".join([
            " ".join(resume_data.get("Skills", [])),
            " ".join(resume_data.get("Projects", [])),
            " ".join(resume_data.get("Achievements", [])),
            " ".join(resume_data.get("Work experience", [])),
            " ".join(resume_data.get("Certifications", []))
        ])

        resume_doc = nlp(resume_text)
        similarity = round(job_desc_doc.similarity(resume_doc) * 100, 1)

        results.append({
            "student_id": student.id,
            "name": student.name,
            "phone_number": student.phone_number,
            "match_percentage": similarity
        })

    return sorted(results, key=lambda x: x['match_percentage'], reverse=True)