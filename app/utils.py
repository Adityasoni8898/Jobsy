from passlib.context import CryptContext
import requests
# import spacy 

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

AFFINDA_API_KEY = "aff_affc7a852045b8f9b6d570a5379cd0aca30a5384"

# nlp = spacy.load('en_core_web_sm')

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def parse_resume_with_affinda(resume_file_path: str):
    url = "https://api.affinda.com/v2/resumes"
    headers = {
        "Authorization": f"Bearer {AFFINDA_API_KEY}"
    }

    with open(resume_file_path, "rb") as resume_file:
        files = {
            'file': resume_file
        }
        
        response = requests.post(url, headers=headers, files=files)

        if response.status_code == 200:
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


# def calculate_percentage_match(job_type, job_description, student_data):
#     """
#     This function will calculate the percentage match of a student based on:
#     - job_type
#     - job_description skills
#     - student's data: resume_data, domain_of_interest, etc.
#     """
#     total_score = 0
#     max_score = 100

#     # Match job type (e.g., full time, internship)
#     if job_type == student_data.job_type:
#         total_score += 20

#     # Parse job description to extract key skills
#     job_description_doc = nlp(job_description)
#     job_keywords = [token.text.lower() for token in job_description_doc if token.is_alpha]
#     # print(job_keywords)

#     # Check for skill matches in the student's resume data (skills section)
#     student_skills = [skill.lower() for skill in student_data.resume_data.get('Skills', [])]
#     matched_skills = set(job_keywords).intersection(set(student_skills))
#     print(matched_skills)

#     if matched_skills:
#         total_score += 50 * (len(matched_skills) / len(job_keywords))  # Give weight to skill match

#     total_score += min((student_data.cgpa / 10) * 20, 20)  # Scaled to a max of 20%

#     # Optional matches for domain_of_interest, preferred_location, and availability
#     if student_data.domain_of_interest:
#         total_score += 5  # Add bonus if domain of interest is filled


#     return total_score