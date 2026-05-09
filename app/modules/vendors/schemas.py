from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class VendorBase(BaseModel):
    name: str
    vendor_type: Optional[str] = "Wholesaler"
    contact: Optional[str] = None
    address: Optional[str] = None
    payment_method: Optional[str] = "Cash"
    books_supplied: Optional[int] = 0
    total_amount: Optional[float] = 0.0
    paid_amount: Optional[float] = 0.0
    remaining_amount: Optional[float] = 0.0
    bill_no: Optional[str] = None
    status: Optional[str] = "Active"

class VendorCreate(VendorBase):
    pass

class Vendor(VendorBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
