from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from ...database import Base

class StockEntry(Base):
    __tablename__ = "stock"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"))
    book_name = Column(String(150), nullable=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=True)
    vendor_name = Column(String(150), nullable=True)
    quantity = Column(Integer, nullable=False)
    invoice_no = Column(String(100), nullable=True)
    remarks = Column(Text, nullable=True)
    movement_type = Column(String(30), nullable=False, default="stock_in")
    tenant_id = Column(String(50), index=True, nullable=False, default="default")
    date = Column(DateTime(timezone=True), server_default=func.now())
