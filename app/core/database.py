from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base
from fastapi import Header, HTTPException, status
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

def ensure_optional_columns():
    if engine is None:
        return

    try:
        inspector = inspect(engine)
        if "sales" not in inspector.get_table_names():
            return

        sales_columns = {column["name"] for column in inspector.get_columns("sales")}
        if "student_phone" not in sales_columns:
            with engine.begin() as connection:
                connection.execute(text("ALTER TABLE sales ADD COLUMN student_phone VARCHAR(20) NULL"))
            logger.info("Added missing sales.student_phone column.")
    except Exception as e:
        logger.error(f"Optional column migration failed: {str(e)}")

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

        # Create all tables from Base.metadata
        Base.metadata.create_all(bind=engine)
        ensure_optional_columns()
        
        logger.info("SUCCESS: Database engine initialized and tables created.")
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

def get_tenant_id(x_tenant_id: str = Header(None)):
    """
    Dependency to extract and validate tenant ID from request headers.
    Enforces strict multi-tenancy - all data access must have a valid tenant.
    
    For public endpoints (auth/register, auth/login), use optional tenant check.
    For protected endpoints, this dependency ensures tenant_id is present.
    """
    if not x_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-Tenant-ID header is required for this endpoint"
        )
    
    # Normalize tenant ID to match DB patterns (lowercase, underscores)
    normalized_id = x_tenant_id.lower().replace("-", "_").replace(" ", "_")
    logger.info(f"Request from Tenant: {normalized_id}")
    return normalized_id

def get_optional_tenant_id(x_tenant_id: str = Header(None)):
    """
    Optional tenant ID extraction for public endpoints like auth/register and auth/login
    """
    if not x_tenant_id:
        return "default"
    
    normalized_id = x_tenant_id.lower().replace("-", "_").replace(" ", "_")
    return normalized_id
