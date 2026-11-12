import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.config import DATABASE_URL
from backend.utils.logger import logger

# Configuration for SQLite to allow multiple threads (FastAPI uses threads)
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False
    # If SQLite file path, ensure parent directory exists
    db_file = DATABASE_URL.replace("sqlite:///", "")
    if db_file and not db_file.startswith(":memory:"):
        db_dir = os.path.dirname(os.path.abspath(db_file))
        os.makedirs(db_dir, exist_ok=True)

try:
    engine = create_engine(DATABASE_URL, connect_args=connect_args)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    # Mask password in log if present
    safe_db_url = DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else DATABASE_URL
    logger.info(f"Database engine initialized (target: {safe_db_url})")
except Exception as e:
    logger.error(f"Failed to initialize database engine: {e}")
    raise e

def get_db():
    """FastAPI dependency for database session lifecycle management."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
