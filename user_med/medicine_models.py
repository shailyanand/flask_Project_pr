from sqlalchemy import Column, Integer, String, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from user_models import Base

class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    dosage = Column(Float, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationship with the User model
    user = relationship("User", back_populates="medicines")

    # Ensure uniqueness of medicine name per user
    __table_args__ = (UniqueConstraint("name", "user_id", name="uq_medicine_name_user"),)