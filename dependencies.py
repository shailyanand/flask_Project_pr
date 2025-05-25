from sqlalchemy.orm import Session
from database import SessionLocal
from user_med.med_database import MedicineSessionLocal

# Dependency to get the database session
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency to get the medicine database session
def get_medicine_db():
    db = MedicineSessionLocal()
    try:
        yield db
    finally:
        db.close()        