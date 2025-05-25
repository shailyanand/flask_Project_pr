import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from user_models import Base
from user_med.medicine_models import Medicine  # Import the Medicine model

DATABASE_URL = "sqlite:///./user_med/medicine.db"  # New database for medicines

medicine_engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
MedicineSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=medicine_engine)

# Create the database tables
Base.metadata.create_all(bind=medicine_engine)