from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from ...database import Base

class School(Base):
    """School/Tenant model for multi-tenant support"""
    __tablename__ = "schools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    tenant_id = Column(String(50), unique=True, nullable=False, index=True)
    admin_email = Column(String(100), nullable=False)
    admin_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class User(Base):
    """User model with proper password hashing and tenant isolation"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, nullable=True, index=True)
    password = Column(String(255), nullable=False)  # Stores bcrypt hash
    mobile = Column(String(15), nullable=True)
    school_name = Column(String(100), nullable=True)
    tenant_id = Column(String(50), index=True, nullable=False)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
