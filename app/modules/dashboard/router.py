from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ...core.database import get_db, get_tenant_id
from ..vendors.models import Vendor
from ..inventory.models import Book
from ..sales.models import Sale
from ..returns.models import ReturnEntry
from ..stock.models import StockEntry

from datetime import datetime, timedelta

router = APIRouter()

@router.get("/")
async def get_dashboard_summary(
    period: str = "Today", 
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    # 0. Date Filtering Logic
    start_date = None
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    if period == "Today":
        start_date = today
    elif period == "This Week":
        start_date = today - timedelta(days=today.weekday())
    elif period == "This Month":
        start_date = today.replace(day=1)
    elif period == "This Year":
        start_date = today.replace(month=1, day=1)

    chart_start_date = start_date or today
    if period == "This Year":
        chart_start_date = today - timedelta(days=29)

    # Base query for filtered metrics
    sales_query = db.query(Sale).filter(Sale.tenant_id == tenant_id)
    returns_query = db.query(ReturnEntry).filter(ReturnEntry.tenant_id == tenant_id)
    
    if start_date:
        sales_query = sales_query.filter(Sale.date >= start_date)
        returns_query = returns_query.filter(ReturnEntry.created_at >= start_date)

    # 1. KPI Stats
    vendor_count = db.query(func.count(Vendor.id)).filter(Vendor.tenant_id == tenant_id).scalar() or 0
    active_vendors = db.query(func.count(Vendor.id)).filter(
        Vendor.tenant_id == tenant_id, 
        Vendor.status == "Active"
    ).scalar() or 0
    total_stock = db.query(func.sum(Book.stock_available)).filter(Book.tenant_id == tenant_id).scalar() or 0
    total_titles = db.query(func.count(Book.id)).filter(Book.tenant_id == tenant_id).scalar() or 0
    
    # Filtered KPIs
    total_sold = sales_query.with_entities(func.sum(Sale.qty)).scalar() or 0
    total_revenue = sales_query.with_entities(func.sum(Sale.total_amount)).scalar() or 0
    return_count = returns_query.with_entities(func.count(ReturnEntry.id)).scalar() or 0

    # 2. Recent Sales (Filtered by period)
    recent_sales = sales_query.order_by(Sale.date.desc()).limit(6).all()
    
    # 3. Recent Vendors
    recent_vendors = db.query(Vendor).filter(Vendor.tenant_id == tenant_id).order_by(Vendor.id.desc()).limit(5).all()

    # 4. Low Stock Items
    low_stock_items = db.query(Book).filter(
        Book.tenant_id == tenant_id,
        Book.stock_available <= 20
    ).all()

    # 5. Payment Methods Distribution (Filtered)
    payment_data = sales_query.with_entities(Sale.payment_method, func.count(Sale.id)).group_by(Sale.payment_method).all()
    
    # 6. Vendor Types Distribution
    vendor_type_data = db.query(Vendor.vendor_type, func.count(Vendor.id)).filter(
        Vendor.tenant_id == tenant_id
    ).group_by(Vendor.vendor_type).all()

    # 7. Daily Stock Added vs Sold
    day_count = max((today.date() - chart_start_date.date()).days + 1, 1)
    days = [chart_start_date.date() + timedelta(days=i) for i in range(day_count)]

    stock_rows = db.query(
        func.date(StockEntry.date).label("day"),
        func.sum(StockEntry.quantity).label("stock")
    ).filter(
        StockEntry.tenant_id == tenant_id,
        StockEntry.date >= chart_start_date,
        StockEntry.quantity > 0
    ).group_by(func.date(StockEntry.date)).all()

    sold_rows = db.query(
        func.date(Sale.date).label("day"),
        func.sum(Sale.qty).label("sold")
    ).filter(
        Sale.tenant_id == tenant_id,
        Sale.date >= chart_start_date
    ).group_by(func.date(Sale.date)).all()

    stock_by_day = {row.day: int(row.stock or 0) for row in stock_rows}
    sold_by_day = {row.day: int(row.sold or 0) for row in sold_rows}

    stock_vs_sold = [
        {
            "day": day.strftime("%d %b"),
            "date": day.isoformat(),
            "stock": stock_by_day.get(day, 0),
            "sold": sold_by_day.get(day, 0)
        }
        for day in days
    ]

    # 8. Monthly Sales & Revenue
    monthly_rows = db.query(
        func.month(Sale.date).label("month"),
        func.count(Sale.id).label("sales"),
        func.sum(Sale.total_amount).label("revenue")
    ).filter(
        Sale.tenant_id == tenant_id,
        Sale.date >= today.replace(month=1, day=1)
    ).group_by(func.month(Sale.date)).all()

    monthly_lookup = {
        row.month: {
            "sales": int(row.sales or 0),
            "revenue": float(row.revenue or 0)
        }
        for row in monthly_rows
    }
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    monthly_sales = [
        {
            "month": month_names[index],
            "sales": monthly_lookup.get(index + 1, {}).get("sales", 0),
            "revenue": monthly_lookup.get(index + 1, {}).get("revenue", 0)
        }
        for index in range(12)
    ]

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
        ],
        "monthly_sales": monthly_sales,
        "stock_vs_sold": stock_vs_sold
    }
