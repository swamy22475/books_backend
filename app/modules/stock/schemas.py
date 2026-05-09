from pydantic import BaseModel
from datetime import datetime

class StockBase(BaseModel):
    book_id: int
    quantity: int

class StockCreate(StockBase):
    pass

class StockUpdate(StockBase):
    pass

class StockEntry(StockBase):
    id: int
    date: datetime

    class Config:
        from_attributes = True
