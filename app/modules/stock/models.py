from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from ...database import Base

class StockEntry(Base):
    __tablename__ = "stock"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"))
    quantity = Column(Integer, nullable=False)
    date = Column(DateTime(timezone=True), server_default=func.now())
