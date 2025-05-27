import os
import sys
import re
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
    #remove rstring and  from the medicine name
    medicine.name = medicine.name.strip()
    # Ensure the medicine name is not empty
    if not medicine.name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Medicine name cannot be empty",
        )
    # Check for special characters
    if not re.match(r'^[A-Za-z0-9 ]+$', medicine.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Medicine name must not contain special characters",
        )
    # Enforce length constraints
    if len(medicine.name) < 2 or len(medicine.name) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Medicine name must be between 2 and 50 characters",
        )

    # check if the mdeicine exists
    existing_medicine = medicine_db.query(Medicine).filter(Medicine.name == medicine.name, 
                                                           Medicine.user_id == current_user.id).first()
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

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_medicine(
                        medicine_id: int,
                        user_db: Session = Depends(get_db),
                        medicine_db: Session = Depends(get_medicine_db),
                        current_user: User = Depends(get_current_user)
                        ):
    """Delete a medicine by ID"""
    # Fetch the medicine from the database
    medicine = medicine_db.query(Medicine).filter(Medicine.id == medicine_id, 
                                                  Medicine.user_id == current_user.id).first()
    if not medicine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicine not found",
        )
    
    # Delete the medicine
    medicine_db.delete(medicine)
    medicine_db.commit()

@router.get("/", response_model=list[MedicineResponse])
async def get_all_medicines(
                        user_db: Session = Depends(get_db),
                        medicine_db: Session = Depends(get_medicine_db),
                        current_user: User = Depends(get_current_user)
                        ) -> list[MedicineResponse]:
    """Get all medicines for the current user"""
    # Fetch all medicines for the current user
    medicines = medicine_db.query(Medicine).filter(Medicine.user_id == current_user.id).all()
    
    if not medicines:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No medicines found",
        )
    
    return medicines

@router.put("/{medicine_id}", response_model=MedicineResponse)
async def update_medicine(
                        medicine_id: int,
                        medicine: MedicineCreate,
                        user_db: Session = Depends(get_db),
                        medicine_db: Session = Depends(get_medicine_db),
                        current_user: User = Depends(get_current_user)
                        ) -> MedicineResponse:
    """Update a medicine by ID"""
    # Fetch the medicine from the database
    existing_medicine = medicine_db.query(Medicine).filter(Medicine.id == medicine_id, 
                                                           Medicine.user_id == current_user.id).first()
    if not existing_medicine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicine not found",
        )
    
    # Update the medicine details
    existing_medicine.name = medicine.name.strip()
    existing_medicine.description = medicine.description
    existing_medicine.dosage = medicine.dosage
    
    # Commit the changes to the database
    medicine_db.commit()
    medicine_db.refresh(existing_medicine)
    
    return existing_medicine


