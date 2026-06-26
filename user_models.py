from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, UniqueConstraint

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    
    # Relationship to medicine records
    medicine_records = relationship("MedicineRecord", back_populates="user", cascade="all, delete-orphan")

    # Add a unique constraint for email
    __table_args__ = (UniqueConstraint("email", name="uq_user_email"),)

