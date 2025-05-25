from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import sessionmaker, Session
from user_models import User
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy.exc import IntegrityError
from schemas import UserCreate, UserResponse
from user_signin import router as user_router
from user_med.medicine_crud import router as medicine_router
from dependencies import get_db


app = FastAPI()

# Include the user router
app.include_router(user_router, prefix="/auth", tags=["Authentication"])
app.include_router(medicine_router, prefix="/medicines", tags=["Medicines"])


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/users", response_model=UserResponse, tags=["Admin"])
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

@app.delete("/users/{user_id}", response_model=UserResponse, tags=["Admin"])
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    '''delete a user'''
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return user


@app.get("/users/{user_id}", response_model=UserResponse, tags=["Admin"])
def get_user(user_id: int, db: Session = Depends(get_db)):  
    '''get a user by id'''
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get('/get_all_users', response_model=list[UserResponse], tags=["Admin"])
def get_all_users(db: Session = Depends(get_db)):
    '''get all users'''
    users = db.query(User).all()
    #in json format
    if not users:
        raise HTTPException(status_code=404, detail="No users found")
    # Convert to list of dictionaries
    users = [user.__dict__ for user in users]
    return users



