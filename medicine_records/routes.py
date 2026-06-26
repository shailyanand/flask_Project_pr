from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from user_models import User
from medicine_records.models import MedicineRecord
from medicine_records.schemas import MedicineRecordCreate, MedicineRecordResponse, UserWithMedicinesResponse
from dependencies import get_db
from typing import List
from datetime import datetime
from sqlalchemy import and_, or_

router = APIRouter()


@router.post("/users/{user_id}/medicines", response_model=MedicineRecordResponse, tags=["Medicine"])
async def create_medicine_record(
    user_id: int, 
    medicine: MedicineRecordCreate, 
    db: Session = Depends(get_db)
):
    """
    Add a new medicine record for a user.
    
    - **user_id**: User ID
    - **medicine**: Medicine details (name, dosage, frequency, etc.)
    """
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create new medicine record
    new_medicine = MedicineRecord(
        user_id=user_id,
        medicine_name=medicine.medicine_name,
        dosage=medicine.dosage,
        frequency=medicine.frequency,
        start_date=medicine.start_date or datetime.utcnow(),
        end_date=medicine.end_date,
        notes=medicine.notes
    )
    
    try:
        db.add(new_medicine)
        db.commit()
        db.refresh(new_medicine)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400, 
            detail=f"Failed to create medicine record: {str(e)}"
        )
    
    return new_medicine


@router.get("/users/{user_id}/medicines", response_model=List[MedicineRecordResponse], tags=["Medicine"])
async def get_user_medicines(
    user_id: int, 
    db: Session = Depends(get_db)
):
    """
    Get all medicine records for a specific user.
    
    - **user_id**: User ID
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    medicines = db.query(MedicineRecord).filter(
        MedicineRecord.user_id == user_id
    ).all()
    
    return medicines


@router.get("/users/{user_id}/medicines/active", response_model=List[MedicineRecordResponse], tags=["Medicine"])
async def get_active_medicines(
    user_id: int, 
    db: Session = Depends(get_db)
):
    """
    Get active medicine records (end_date is null or in future) for a user.
    
    - **user_id**: User ID
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get active medicines (no end date or end date in future)
    medicines = db.query(MedicineRecord).filter(
        and_(
            MedicineRecord.user_id == user_id,
            or_(
                MedicineRecord.end_date.is_(None),
                MedicineRecord.end_date >= datetime.utcnow()
            )
        )
    ).all()
    
    return medicines


@router.get("/medicines/{medicine_id}", response_model=MedicineRecordResponse, tags=["Medicine"])
async def get_medicine_record(
    medicine_id: int, 
    db: Session = Depends(get_db)
):
    """
    Get a specific medicine record by ID.
    
    - **medicine_id**: Medicine record ID
    """
    medicine = db.query(MedicineRecord).filter(
        MedicineRecord.id == medicine_id
    ).first()
    
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine record not found")
    
    return medicine


@router.put("/medicines/{medicine_id}", response_model=MedicineRecordResponse, tags=["Medicine"])
async def update_medicine_record(
    medicine_id: int, 
    medicine_update: MedicineRecordCreate, 
    db: Session = Depends(get_db)
):
    """
    Update a medicine record.
    
    - **medicine_id**: Medicine record ID
    - **medicine_update**: Updated medicine details
    """
    medicine = db.query(MedicineRecord).filter(
        MedicineRecord.id == medicine_id
    ).first()
    
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine record not found")
    
    # Update fields
    medicine.medicine_name = medicine_update.medicine_name
    medicine.dosage = medicine_update.dosage
    medicine.frequency = medicine_update.frequency
    
    if medicine_update.start_date:
        medicine.start_date = medicine_update.start_date
    if medicine_update.end_date is not None:
        medicine.end_date = medicine_update.end_date
    if medicine_update.notes is not None:
        medicine.notes = medicine_update.notes
    
    medicine.updated_at = datetime.utcnow()
    
    try:
        db.commit()
        db.refresh(medicine)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400, 
            detail=f"Failed to update medicine record: {str(e)}"
        )
    
    return medicine


@router.delete("/medicines/{medicine_id}", response_model=MedicineRecordResponse, tags=["Medicine"])
async def delete_medicine_record(
    medicine_id: int, 
    db: Session = Depends(get_db)
):
    """
    Delete a medicine record.
    
    - **medicine_id**: Medicine record ID
    """
    medicine = db.query(MedicineRecord).filter(
        MedicineRecord.id == medicine_id
    ).first()
    
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine record not found")
    
    db.delete(medicine)
    db.commit()
    
    return medicine


@router.get("/users/{user_id}/medicines/summary", response_model=UserWithMedicinesResponse, tags=["Medicine"])
async def get_user_with_medicines(
    user_id: int, 
    db: Session = Depends(get_db)
):
    """
    Get user info with all their medicine records.
    
    - **user_id**: User ID
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


@router.post("/medicines/bulk", response_model=List[MedicineRecordResponse], tags=["Medicine"])
async def add_multiple_medicines(
    user_id: int, 
    medicines: List[MedicineRecordCreate],
    db: Session = Depends(get_db)
):
    """
    Add multiple medicine records for a user at once.
    
    - **user_id**: User ID
    - **medicines**: List of medicine details
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    created_medicines = []
    
    try:
        for medicine in medicines:
            new_medicine = MedicineRecord(
                user_id=user_id,
                medicine_name=medicine.medicine_name,
                dosage=medicine.dosage,
                frequency=medicine.frequency,
                start_date=medicine.start_date or datetime.utcnow(),
                end_date=medicine.end_date,
                notes=medicine.notes
            )
            db.add(new_medicine)
            created_medicines.append(new_medicine)
        
        db.commit()
        
        # Refresh all records
        for medicine in created_medicines:
            db.refresh(medicine)
            
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create medicine records: {str(e)}"
        )
    
    return created_medicines
