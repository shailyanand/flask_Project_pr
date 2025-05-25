import os
import sys
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from dependencies import get_db, get_medicine_db

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from user_models import User
from user_signin import get_current_user
from user_med.medicine_schemas import MedicineCreate, MedicineResponse
from user_med.medicine_models import Medicine


router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_medicine(
                        medicine: MedicineCreate,
                        user_db: Session = Depends(get_db),
                        medicine_db: Session = Depends(get_medicine_db),
                        current_user: User = Depends(get_current_user)
                        ) -> MedicineResponse:
    """Add a new medicine"""
    # check if the mdeicine exists
    existing_medicine = medicine_db.query(Medicine).filter(Medicine.name == medicine.name).first()
    if existing_medicine:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Medicine already exists",
        )
    ## Create a new medicine instance
    new_medicine = Medicine(
        name=medicine.name,
        description=medicine.description,
        dosage=medicine.dosage,
        user_id=current_user.id  # Associate the medicine with the current user
    )
    
    # Add the medicine to the medicine database
    medicine_db.add(new_medicine)
    medicine_db.commit()
    medicine_db.refresh(new_medicine)


    return new_medicine


