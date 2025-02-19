from fastapi import FastAPI
from .routers import student, job_search, login
from .database import engine
from . import models
from fastapi.middleware.cors import CORSMiddleware

# Create database tables
models.Base.metadata.create_all(bind=engine)

# FastAPI instance
app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],  
)

@app.get("/")
def hello():
    return {"message": "Hello"}

app.include_router(student.router)
app.include_router(job_search.router)
app.include_router(login.router)