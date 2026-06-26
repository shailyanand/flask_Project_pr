from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from user_models import Base

BASE_DIR = Path(__file__).resolve().parent
DATABASE_DIR = BASE_DIR / "userData"
DATABASE_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_URL = f"sqlite:///{DATABASE_DIR / 'user.db'}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)