from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
Base = declarative_base()

engine = None
SessionLocal = None

def init_db():
    global engine, SessionLocal
    
    if not DATABASE_URL:
        logger.error("DATABASE_URL not found in environment!")
        return False

    try:
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True
        )

        SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )

        logger.info("SUCCESS: Database engine initialized.")
        return True

    except Exception as e:
        logger.error(f"Database init failed: {str(e)}")
        return False

def get_db():
    if SessionLocal is None:
        init_db()
        
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()