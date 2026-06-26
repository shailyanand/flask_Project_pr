from pydantic import BaseModel, EmailStr
from pydantic.config import ConfigDict
from datetime import datetime
from typing import Optional, List


class MedicineRecordCreate(BaseModel):
    medicine_name: str
    dosage: str
    frequency: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    notes: Optional[str] = None


class MedicineRecordResponse(BaseModel):
    id: int
    user_id: int
    medicine_name: str
    dosage: str
    frequency: str
    start_date: datetime
    end_date: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserWithMedicinesResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    medicine_records: List[MedicineRecordResponse] = []

    model_config = ConfigDict(from_attributes=True)
