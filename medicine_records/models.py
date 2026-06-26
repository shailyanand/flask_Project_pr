from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from datetime import datetime
from user_models import Base


class MedicineRecord(Base):
    __tablename__ = "medicine_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    medicine_name = Column(String, index=True)
    dosage = Column(String)  # e.g., "500mg"
    frequency = Column(String)  # e.g., "twice daily"
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship back to user
    user = relationship("User", back_populates="medicine_records")
