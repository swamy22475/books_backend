from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from ...database import Base

class ReturnEntry(Base):
    __tablename__ = "returns"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, index=True, nullable=True)
    student_name = Column(String(100), nullable=False)
    student_class = Column(String(50))
    book_name = Column(String(150), nullable=False)
    qty = Column(Integer, default=1)
    reason = Column(String(255))
    status = Column(String(50), default="Pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
