from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from user_models import User
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from dependencies import get_db
from schemas import ForgotPasswordRequest, ResetPasswordRequest


# JWT Configuration
SECRET_KEY = "40353bad3045ceb68414747a2cfeb646a01ef599ec2013be328d8196683e325b"  # Replace with a strong secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
PASSWORD_RESET_TOKEN_EXPIRE_MINUTES = 15

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Router for user-related endpoints
router = APIRouter()

# Utility function to create JWT token
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/signin", response_model=dict, tags=["Authentication"])
async def signin(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Authenticate a user and return a JWT token"""
    # Fetch the user from the database
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Verify the password
    if not pwd_context.verify(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Generate JWT token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


def create_password_reset_token(email: str, expires_delta: timedelta | None = None):
    to_encode = {"sub": email}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=PASSWORD_RESET_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_password_reset_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise JWTError()
        return email
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired reset token",
        )


@router.post("/forgot-password", response_model=dict, tags=["Authentication"])
async def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Generate a password reset token."""
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    reset_token = create_password_reset_token(user.email)
    reset_link = f"http://localhost:8000/auth/reset-password?token={reset_token}"

    return {
        "message": "Password reset token generated.",
        "reset_token": reset_token,
        "reset_link": reset_link,
    }


@router.post("/reset-password", response_model=dict, tags=["Authentication"])
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset a user's password using a valid reset token."""
    email = verify_password_reset_token(request.token)
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user.password = pwd_context.hash(request.new_password)
    db.add(user)
    db.commit()
    return {"message": "Password reset successful."}


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/signin")

@router.get("/protected", tags=["Authentication"])
async def protected_route(token: str = Depends(oauth2_scheme)):
    """A protected route that requires a valid JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
        return {"message": f"Hello, {email}!"}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )