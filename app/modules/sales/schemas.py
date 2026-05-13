from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class SaleBase(BaseModel):
    book_id: int = None
    student_name: str
    student_phone: Optional[str] = None
    student_class: str = Field(..., alias="class")
    student_section: Optional[str] = None
    book_name: str
    book_type: str = "Set"
    qty: int = 1
    unit_price: float = 0.0
    total_amount: float
    paid_amount: float = 0.0
    concession: float = 0.0
    remaining_amount: float = 0.0
    payment_method: str = "Cash"
    book_selection: str = "Single"

    class Config:
        populate_by_name = True

class SaleCreate(SaleBase):
    pass

class Sale(SaleBase):
    id: int
    tenant_id: str
    date: datetime

    class Config:
        from_attributes = True
        validate_by_name = True
