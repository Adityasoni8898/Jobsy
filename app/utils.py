from passlib.context import CryptContext
import requests
import os
# import spacy 
from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

affinda_api_key = settings.affinda_api_key

# nlp = spacy.load('en_core_web_sm')

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def parse_resume_with_affinda(resume_file_path: str):
    url = "https://api.affinda.com/v2/resumes"
    headers = {
        "Authorization": f"Bearer {affinda_api_key}"
    }

    with open(resume_file_path, "rb") as resume_file:
        files = {
            'file': resume_file
        }
        
        response = requests.post(url, headers=headers, files=files)

        if response.status_code == 200:
            # Delete the resume file after successful parsing
            os.remove(resume_file_path)
            return response.json()  # Return the parsed resume data
        else:
            print(f"Failed to parse resume. Status code: {response.status_code}")
            print(response.text)
            return None  # Return None if parsing fails
        

def extract_info(data):
    extracted_info = {
        "Skills": [skill['name'] for skill in data['data']['skills']],
        "Work Experience": [],
        "Projects": [],
        "Achievements": [],
        "Certifications": []
    }

    for section in data['data']['sections']:
        if section['sectionType'] == 'WorkExperience':
            extracted_info["Work Experience"].append(section['text'])
        elif section['sectionType'] == 'Projects':
            extracted_info["Projects"].append(section['text'])
        elif section['sectionType'] == 'Achievements':
            extracted_info["Achievements"].append(section['text'])
        elif section['sectionType'] == 'Certifications':
            extracted_info["Certifications"].append(section['text'])

    return extracted_info