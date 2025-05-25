from pydantic import BaseModel
from pydantic.config import ConfigDict


# Pydantic model for the medicine payload
class MedicineCreate(BaseModel):
    name: str
    description: str
    dosage: float

class MedicineResponse(BaseModel):
    id: int
    name: str
    description: str
    dosage: float
    user_id: int

    model_config = ConfigDict(from_attributes=True)  # Use ConfigDict instead of class-based Config