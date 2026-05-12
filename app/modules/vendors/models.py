from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.sql import func
from ...database import Base

class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    vendor_type = Column(String(50)) # Wholesaler, Publisher, etc.
    contact = Column(String(20))     # Phone
    address = Column(String(255))
    payment_method = Column(String(50))
    books_supplied = Column(Integer, default=0)
    total_amount = Column(Float, default=0.0)
    paid_amount = Column(Float, default=0.0)
    remaining_amount = Column(Float, default=0.0)
    bill_no = Column(String(100), nullable=True)
    status = Column(String(20), default="Active")
    tenant_id = Column(String(50), index=True, nullable=False, default="default")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
