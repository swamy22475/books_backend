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

def _amount(value):
    return float(value or 0)

def _sale_bill_key(sale):
    sale_day = sale.date.date().isoformat() if sale.date else ""
    return "|".join([
        sale.student_name or "",
        sale.student_phone or "",
        sale.student_class or "",
        sale.student_section or "",
        sale_day,
        sale.payment_method or ""
    ])

def _same_return_target(sale, entry):
    if entry.student_name and (sale.student_name or "").strip().lower() != entry.student_name.strip().lower():
        return False
    if entry.book_name and (sale.book_name or "").strip().lower() != entry.book_name.strip().lower():
        return False
    if entry.student_class and sale.student_class and sale.student_class.strip().lower() != entry.student_class.strip().lower():
        return False
    return bool(entry.student_name or entry.book_name)

def _add_return_adjustment(adjustments, sale, qty, amount):
    if not sale or not sale.id or qty <= 0:
        return
    if sale.id not in adjustments:
        adjustments[sale.id] = {"qty": 0, "amount": 0.0}
    adjustments[sale.id]["qty"] += qty
    adjustments[sale.id]["amount"] += amount

def _return_adjustments(sales, approved_returns):
    sales_by_id = {sale.id: sale for sale in sales}
    adjustments = {}

    for entry in approved_returns:
        direct_sale = sales_by_id.get(entry.sale_id) if entry.sale_id else None
        if direct_sale:
            _add_return_adjustment(adjustments, direct_sale, int(entry.qty or 0), _amount(entry.total_amount))
            continue

        remaining_qty = int(entry.qty or 0)
        return_unit_price = _amount(entry.unit_price)
        candidates = sorted(
            [sale for sale in sales if _same_return_target(sale, entry)],
            key=lambda sale: sale.date or datetime.min
        )
        for sale in candidates:
            if remaining_qty <= 0:
                break
            already_returned = int(adjustments.get(sale.id, {}).get("qty", 0))
            available_qty = max(int(sale.qty or 0) - already_returned, 0)
            qty = min(available_qty, remaining_qty)
            unit_price = return_unit_price or _amount(sale.unit_price)
            _add_return_adjustment(adjustments, sale, qty, unit_price * qty)
            remaining_qty -= qty

    return adjustments

def _net_sales_metrics(sales, approved_returns):
    return_adjustments = _return_adjustments(sales, approved_returns)

    bills = {}
    total_sold = 0
    total_returns = 0
    return_amount = 0.0

    for sale in sales:
        returned_qty = return_adjustments.get(sale.id, {}).get("qty", 0)
        returned_amount = return_adjustments.get(sale.id, {}).get("amount", 0.0)
        net_qty = max(int(sale.qty or 0) - returned_qty, 0)
        net_amount = max(_amount(sale.total_amount) - returned_amount, 0.0)
        total_sold += net_qty

        key = _sale_bill_key(sale)
        if key not in bills:
            bills[key] = {
                "total_amount": 0.0,
                "concession": _amount(sale.concession),
                "paid_amount": _amount(sale.paid_amount)
            }
        bills[key]["total_amount"] += net_amount

    for entry in approved_returns:
        total_returns += int(entry.qty or 0)
        return_amount += _amount(entry.total_amount)

    total_revenue = 0.0
    total_paid = 0.0
    total_due = 0.0
    total_refund_due = 0.0
    for bill in bills.values():
        net_total = max(bill["total_amount"] - bill["concession"], 0.0)
        paid = bill["paid_amount"]
        total_revenue += net_total
        total_paid += min(paid, net_total)
        total_due += max(net_total - paid, 0.0)
        total_refund_due += max(paid - net_total, 0.0)

    return {
        "total_sold": total_sold,
        "total_revenue": total_revenue,
        "total_paid": total_paid,
        "total_due": total_due,
        "total_refund_due": total_refund_due,
        "total_returns": total_returns,
        "return_amount": return_amount
    }

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
    
    approved_returns_query = returns_query.filter(ReturnEntry.status == "Approved")
    net_metrics = _net_sales_metrics(sales_query.all(), approved_returns_query.all())

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

    returned_rows = db.query(
        func.date(ReturnEntry.created_at).label("day"),
        func.sum(ReturnEntry.qty).label("returned")
    ).filter(
        ReturnEntry.tenant_id == tenant_id,
        ReturnEntry.status == "Approved",
        ReturnEntry.created_at >= chart_start_date
    ).group_by(func.date(ReturnEntry.created_at)).all()

    stock_by_day = {row.day: int(row.stock or 0) for row in stock_rows}
    sold_by_day = {row.day: int(row.sold or 0) for row in sold_rows}
    returned_by_day = {row.day: int(row.returned or 0) for row in returned_rows}

    stock_vs_sold = [
        {
            "day": day.strftime("%d %b"),
            "date": day.isoformat(),
            "stock": stock_by_day.get(day, 0),
            "sold": max(sold_by_day.get(day, 0) - returned_by_day.get(day, 0), 0)
        }
        for day in days
    ]

    # 8. Monthly Sales & Revenue
    monthly_rows = db.query(
        func.month(Sale.date).label("month"),
        func.sum(Sale.qty).label("sales"),
        func.sum(Sale.total_amount).label("revenue")
    ).filter(
        Sale.tenant_id == tenant_id,
        Sale.date >= today.replace(month=1, day=1)
    ).group_by(func.month(Sale.date)).all()

    monthly_return_rows = db.query(
        func.month(ReturnEntry.created_at).label("month"),
        func.sum(ReturnEntry.qty).label("returned"),
        func.sum(ReturnEntry.total_amount).label("return_amount")
    ).filter(
        ReturnEntry.tenant_id == tenant_id,
        ReturnEntry.status == "Approved",
        ReturnEntry.created_at >= today.replace(month=1, day=1)
    ).group_by(func.month(ReturnEntry.created_at)).all()

    monthly_returns_lookup = {
        row.month: {
            "returned": int(row.returned or 0),
            "return_amount": float(row.return_amount or 0)
        }
        for row in monthly_return_rows
    }

    monthly_lookup = {
        row.month: {
            "sales": max(int(row.sales or 0) - monthly_returns_lookup.get(row.month, {}).get("returned", 0), 0),
            "revenue": max(float(row.revenue or 0) - monthly_returns_lookup.get(row.month, {}).get("return_amount", 0), 0)
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
            "total_sold": net_metrics["total_sold"],
            "total_revenue": net_metrics["total_revenue"],
            "total_paid": net_metrics["total_paid"],
            "total_due": net_metrics["total_due"],
            "total_refund_due": net_metrics["total_refund_due"],
            "total_returns": net_metrics["total_returns"],
            "return_amount": net_metrics["return_amount"]
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
