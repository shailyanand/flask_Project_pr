from pydantic import BaseModel, EmailStr
from pydantic.config import ConfigDict

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

    model_config = ConfigDict(from_attributes=True)  # Use ConfigDict instead of class-based Config