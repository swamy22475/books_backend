from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ...core.database import get_db
from ..sales.models import Sale
from ..inventory.models import Book

router = APIRouter()

@router.get("/sales-summary")
async def get_sales_summary(db: Session = Depends(get_db)):
    total_sales = db.query(func.sum(Sale.total_amount)).scalar() or 0
    count_sales = db.query(func.count(Sale.id)).scalar() or 0
    return {
        "total_revenue": total_sales,
        "total_sales_count": count_sales
    }

@router.get("/stock-summary")
async def get_stock_summary(db: Session = Depends(get_db)):
    total_stock = db.query(func.sum(Book.stock_qty)).scalar() or 0
    low_stock_count = db.query(func.count(Book.id)).filter(Book.stock_qty < 10).scalar() or 0
    return {
        "total_stock_quantity": total_stock,
        "low_stock_items": low_stock_count
    }
