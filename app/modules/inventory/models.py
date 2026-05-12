from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.sql import func
from ...database import Base

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    book_class = Column(String(255), nullable=True)  # Multiple classes stored as CSV (e.g. "Class 1, Class 2")
    book_type = Column(String(20), default="Set")       # Set / Single
    total_qty = Column(Integer, default=0)
    sets_qty = Column(Integer, default=0)
    singles_qty = Column(Integer, default=0)
    cost_price = Column(Float, default=0.0)
    selling_price = Column(Float, default=0.0)
    stock_available = Column(Integer, default=0)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=True)
    vendor_name = Column(String(150), nullable=True)   # denormalised for quick display
    tenant_id = Column(String(50), index=True, nullable=False, default="default")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
