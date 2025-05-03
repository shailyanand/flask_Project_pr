from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from user_models import Base, User
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr
from sqlalchemy.exc import IntegrityError
from schemas import UserCreate, UserResponse

DATABASE_URL = "sqlite:///./user.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    '''create a new user'''
    # Check if the user already exists
    # Hash the password
    hashed_password = CryptContext(schemes=["bcrypt"], deprecated="auto").hash(user.password)
    new_user = User(name=user.name, email=user.email, password=hashed_password) # Create a new user instance

    try:
        db.add(new_user)  # Add the new user to the session
        db.commit()  # Commit the transaction to save the user in the database
        db.refresh(new_user)  # Refresh the instance to get the updated data from the database
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    return new_user

@app.delete("/users/{user_id}", response_model=UserResponse)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    '''delete a user'''
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return user


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):  
    '''get a user by id'''
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get('/get_all_users', response_model=list[UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    '''get all users'''
    users = db.query(User).all()
    #in json format
    if not users:
        raise HTTPException(status_code=404, detail="No users found")
    # Convert to list of dictionaries
    users = [user.__dict__ for user in users]
    return users



