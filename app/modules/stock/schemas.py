from pydantic import BaseModel
from datetime import datetime, date as date_type
from typing import Optional, Union

class StockBase(BaseModel):
    book_id: int
    quantity: int
    book_name: Optional[str] = None
    vendor_id: Optional[int] = None
    vendor_name: Optional[str] = None
    invoice_no: Optional[str] = None
    remarks: Optional[str] = None
    movement_type: Optional[str] = "stock_in"
    date: Optional[Union[datetime, date_type]] = None

class StockCreate(StockBase):
    pass

class StockUpdate(StockBase):
    pass

class StockEntry(StockBase):
    id: int
    date: datetime
    book_class: Optional[str] = None
    book_type: Optional[str] = None

    class Config:
        from_attributes = True
