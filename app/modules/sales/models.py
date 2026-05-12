from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from ...database import Base

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, index=True, nullable=True)
    student_name = Column(String(100), nullable=False)
    student_phone = Column(String(20), nullable=True)
    student_class = Column("class", String(20))
    book_name = Column(String(100))
    book_type = Column(String(20), default="Set")
    qty = Column(Integer, default=1)
    unit_price = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    paid_amount = Column(Float, default=0.0)
    concession = Column(Float, default=0.0)
    remaining_amount = Column(Float, default=0.0)
    payment_method = Column(String(50), default="Cash")
    book_selection = Column(String(20), default="Single")
    tenant_id = Column(String(50), index=True, nullable=False, default="default")
    date = Column(DateTime(timezone=True), server_default=func.now())
