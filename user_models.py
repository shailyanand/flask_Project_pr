from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, UniqueConstraint

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

    medicines = relationship("Medicine", back_populates="user")

    # Add a unique constraint for email
    __table_args__ = (UniqueConstraint("email", name="uq_user_email"),)

