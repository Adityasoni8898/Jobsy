from .. import models, oauth2
from sqlalchemy.orm import Session
from .. database import get_db
from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext


router = APIRouter(
    tags=["Users"]
)

# OAuth2 scheme for login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Utility functions for password
def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# SIGNUP: Create new user
@router.post("/signup")
def signup(username: str, email: str, password: str, db: Session = Depends(get_db)):
    # Check if user already exists
    user = db.query(models.User).filter(models.User.user_name == username).first()
    if user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = get_password_hash(password)
    print(hashed_password)
    new_user = models.User(
        user_name=username, 
        email=email, 
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}


@router.post("/login")
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        models.User.user_name == user_credentials.username
    ).first()
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = oauth2.create_access_token(data={"sub": user.user_name})
    return {"access_token": access_token, "token_type": "bearer"}