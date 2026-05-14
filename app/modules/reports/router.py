from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ...core.database import get_db, get_tenant_id
from ..sales.models import Sale
from ..inventory.models import Book
from ..returns.models import ReturnEntry
from datetime import datetime

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

@router.get("/sales-summary")
async def get_sales_summary(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    if not tenant_id or tenant_id == "default":
        return {
            "total_revenue": 0,
            "total_paid": 0,
            "total_due": 0,
            "total_refund_due": 0,
            "total_sales_count": 0,
            "total_books_sold": 0,
            "total_returns": 0,
            "return_amount": 0
        }
    sales = db.query(Sale).filter(Sale.tenant_id == tenant_id).all()
    approved_returns = db.query(ReturnEntry).filter(
        ReturnEntry.tenant_id == tenant_id,
        ReturnEntry.status == "Approved"
    ).all()

    return_adjustments = _return_adjustments(sales, approved_returns)
    returned_qty = 0
    return_amount = 0.0
    for entry in approved_returns:
        returned_qty += int(entry.qty or 0)
        return_amount += _amount(entry.total_amount)

    bills = {}
    total_books_sold = 0
    for sale in sales:
        net_qty = max(int(sale.qty or 0) - return_adjustments.get(sale.id, {}).get("qty", 0), 0)
        net_amount = max(_amount(sale.total_amount) - return_adjustments.get(sale.id, {}).get("amount", 0.0), 0.0)
        total_books_sold += net_qty

        key = _sale_bill_key(sale)
        if key not in bills:
            bills[key] = {
                "total_amount": 0.0,
                "concession": _amount(sale.concession),
                "paid_amount": _amount(sale.paid_amount)
            }
        bills[key]["total_amount"] += net_amount

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
        "total_revenue": total_revenue,
        "total_paid": total_paid,
        "total_due": total_due,
        "total_refund_due": total_refund_due,
        "total_sales_count": total_books_sold,
        "total_books_sold": total_books_sold,
        "total_returns": returned_qty,
        "return_amount": return_amount
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
