from pydantic import BaseModel
from datetime import datetime

class ReturnBase(BaseModel):
    sale_id: int | None = None
    book_id: int | None = None
    student_name: str
    student_class: str | None = None
    book_name: str
    qty: int
    unit_price: float = 0.0
    total_amount: float = 0.0
    reason: str | None = None
    status: str = "Pending"

class ReturnCreate(ReturnBase):
    pass

class ReturnUpdate(BaseModel):
    status: str

class ReturnEntry(ReturnBase):
    id: int
    tenant_id: str
    created_at: datetime

    class Config:
        from_attributes = True
