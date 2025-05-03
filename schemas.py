from pydantic import BaseModel, EmailStr

# Pydantic model for user creation
class UserCreate(BaseModel):
    name: str
    email: EmailStr  # Validate email format
    password: str

# Pydantic model for user response
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True  # Enable ORM mode to work with SQLAlchemy models