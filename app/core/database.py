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
        table_names = inspector.get_table_names()
        if "sales" not in table_names:
            return

        sales_columns = {column["name"] for column in inspector.get_columns("sales")}
        if "student_phone" not in sales_columns:
            with engine.begin() as connection:
                connection.execute(text("ALTER TABLE sales ADD COLUMN student_phone VARCHAR(20) NULL"))
            logger.info("Added missing sales.student_phone column.")

        if "student_section" not in sales_columns:
            with engine.begin() as connection:
                connection.execute(text("ALTER TABLE sales ADD COLUMN student_section VARCHAR(50) NULL"))
            logger.info("Added missing sales.student_section column.")

        if "stock" in table_names:
            stock_columns = {column["name"] for column in inspector.get_columns("stock")}
            stock_optional_columns = {
                "book_name": "VARCHAR(150) NULL",
                "vendor_id": "INT NULL",
                "vendor_name": "VARCHAR(150) NULL",
                "invoice_no": "VARCHAR(100) NULL",
                "remarks": "TEXT NULL",
                "movement_type": "VARCHAR(30) NOT NULL DEFAULT 'stock_in'",
            }
            with engine.begin() as connection:
                for column_name, column_type in stock_optional_columns.items():
                    if column_name not in stock_columns:
                        connection.execute(text(f"ALTER TABLE stock ADD COLUMN {column_name} {column_type}"))
                        logger.info(f"Added missing stock.{column_name} column.")

        if "returns" in table_names:
            return_columns = {column["name"] for column in inspector.get_columns("returns")}
            return_optional_columns = {
                "sale_id": "INT NULL",
                "unit_price": "FLOAT NOT NULL DEFAULT 0",
                "total_amount": "FLOAT NOT NULL DEFAULT 0",
            }
            with engine.begin() as connection:
                for column_name, column_type in return_optional_columns.items():
                    if column_name not in return_columns:
                        connection.execute(text(f"ALTER TABLE returns ADD COLUMN {column_name} {column_type}"))
                        logger.info(f"Added missing returns.{column_name} column.")
    except Exception as e:
        logger.error(f"Optional column migration failed: {str(e)}")

def init_db():
    global engine, SessionLocal
    
    if engine is not None:
        return True
    
    if not DATABASE_URL:
        logger.error("DATABASE_URL not found in environment!")
        return False

    try:
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=3600,
            pool_size=10,
            max_overflow=20
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
