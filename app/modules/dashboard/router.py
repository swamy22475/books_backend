from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ...core.database import get_db
from ..vendors.models import Vendor
from ..inventory.models import Book
from ..sales.models import Sale

from ..returns.models import ReturnEntry

from datetime import datetime, timedelta

router = APIRouter()

@router.get("/")
async def get_dashboard_summary(period: str = "Today", db: Session = Depends(get_db)):
    # 0. Date Filtering Logic
    start_date = None
    # Use timezone-naive today as the models use naive dates usually or handle accordingly
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    if period == "Today":
        start_date = today
    elif period == "This Week":
        start_date = today - timedelta(days=today.weekday())
    elif period == "This Month":
        start_date = today.replace(day=1)
    elif period == "This Year":
        start_date = today.replace(month=1, day=1)

    # Base query for filtered metrics
    sales_query = db.query(Sale)
    returns_query = db.query(ReturnEntry)
    
    if start_date:
        sales_query = sales_query.filter(Sale.date >= start_date)
        returns_query = returns_query.filter(ReturnEntry.created_at >= start_date)

    # 1. KPI Stats
    vendor_count = db.query(func.count(Vendor.id)).scalar() or 0
    active_vendors = db.query(func.count(Vendor.id)).filter(Vendor.status == "Active").scalar() or 0
    total_stock = db.query(func.sum(Book.stock_available)).scalar() or 0
    total_titles = db.query(func.count(Book.id)).scalar() or 0
    
    # Filtered KPIs
    total_sold = sales_query.with_entities(func.sum(Sale.qty)).scalar() or 0
    total_revenue = sales_query.with_entities(func.sum(Sale.total_amount)).scalar() or 0
    return_count = returns_query.with_entities(func.count(ReturnEntry.id)).scalar() or 0

    # 2. Recent Sales (Filtered by period)
    recent_sales = sales_query.order_by(Sale.date.desc()).limit(6).all()
    
    # 3. Recent Vendors (Always global)
    recent_vendors = db.query(Vendor).order_by(Vendor.id.desc()).limit(5).all()

    # 4. Low Stock Items (Always global/current)
    low_stock_items = db.query(Book).filter(Book.stock_available <= 20).all()

    # 5. Payment Methods Distribution (Filtered)
    payment_data = sales_query.with_entities(Sale.payment_method, func.count(Sale.id)).group_by(Sale.payment_method).all()
    
    # 6. Vendor Types Distribution (Global)
    vendor_type_data = db.query(Vendor.vendor_type, func.count(Vendor.id)).group_by(Vendor.vendor_type).all()

    return {
        "kpis": {
            "vendors": vendor_count,
            "active_vendors": active_vendors,
            "total_stock": total_stock,
            "total_titles": total_titles,
            "total_sold": total_sold,
            "total_revenue": total_revenue,
            "total_returns": return_count
        },
        "recent_sales": [
            {
                "id": s.id,
                "student": s.student_name,
                "class": s.student_class,
                "book": s.book_name,
                "qty": s.qty,
                "price": s.total_amount,
                "payment": s.payment_method,
                "date": s.date.strftime("%Y-%m-%d") if s.date else ""
            } for s in recent_sales
        ],
        "recent_vendors": [
            {
                "id": v.id,
                "name": v.name,
                "type": v.vendor_type,
                "contact": v.contact,
                "status": v.status
            } for v in recent_vendors
        ],
        "low_stock": [
            {
                "id": b.id,
                "name": b.name,
                "stock": b.stock_available,
                "price": b.selling_price
            } for b in low_stock_items
        ],
        "payment_methods": [
            {"name": p[0] or "Unknown", "value": p[1]} for p in payment_data
        ],
        "vendor_types": [
            {"name": v[0] or "Other", "value": v[1]} for v in vendor_type_data
        ]
    }
