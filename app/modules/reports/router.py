from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ...core.database import get_db, get_tenant_id
from ..sales.models import Sale
from ..inventory.models import Book

router = APIRouter()

@router.get("/sales-summary")
async def get_sales_summary(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    if not tenant_id or tenant_id == "default":
        return {"total_revenue": 0, "total_sales_count": 0}
    total_sales = db.query(func.sum(Sale.total_amount)).filter(Sale.tenant_id == tenant_id).scalar() or 0
    count_sales = db.query(func.count(Sale.id)).filter(Sale.tenant_id == tenant_id).scalar() or 0
    return {
        "total_revenue": total_sales,
        "total_sales_count": count_sales
    }

@router.get("/stock-summary")
async def get_stock_summary(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    if not tenant_id or tenant_id == "default":
        return {"total_stock_quantity": 0, "low_stock_items": 0}
    # Fixed: Book model uses 'stock_available' not 'stock_qty'
    total_stock = db.query(func.sum(Book.stock_available)).filter(Book.tenant_id == tenant_id).scalar() or 0
    low_stock_count = db.query(func.count(Book.id)).filter(
        Book.tenant_id == tenant_id,
        Book.stock_available < 10
    ).scalar() or 0
    return {
        "total_stock_quantity": total_stock,
        "low_stock_items": low_stock_count
    }
