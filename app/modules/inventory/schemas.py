from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BookBase(BaseModel):
    name: str
    book_class: Optional[str] = None
    book_type: str = "Set"
    total_qty: int = 0
    sets_qty: int = 0
    singles_qty: int = 0
    cost_price: float = 0.0
    selling_price: float = 0.0
    stock_available: int = 0
    vendor_id: Optional[int] = None
    vendor_name: Optional[str] = None

class BookCreate(BookBase):
    pass

class Book(BookBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
