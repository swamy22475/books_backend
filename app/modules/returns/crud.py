from fastapi import HTTPException
from sqlalchemy.orm import Session
from . import models, schemas
from ..inventory.models import Book
from ..stock.models import StockEntry
from ..sales.models import Sale

ACTIVE_RETURN_STATUSES = ("Pending", "Approved")

def _return_amount(db_return: models.ReturnEntry):
    return float(db_return.total_amount or ((db_return.unit_price or 0) * (db_return.qty or 0)))

def _get_returned_qty(db: Session, tenant_id: str, sale_id: int, exclude_return_id: int | None = None):
    query = db.query(models.ReturnEntry).filter(
        models.ReturnEntry.tenant_id == tenant_id,
        models.ReturnEntry.sale_id == sale_id,
        models.ReturnEntry.status.in_(ACTIVE_RETURN_STATUSES)
    )
    if exclude_return_id:
        query = query.filter(models.ReturnEntry.id != exclude_return_id)
    return sum(int(r.qty or 0) for r in query.all())

def _validate_return_qty(db: Session, tenant_id: str, db_return: models.ReturnEntry, exclude_return_id: int | None = None):
    if not db_return.sale_id:
        return

    sale = db.query(Sale).filter(Sale.tenant_id == tenant_id, Sale.id == db_return.sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found for this return")

    if db_return.qty <= 0:
        raise HTTPException(status_code=400, detail="Return quantity must be at least 1")

    already_returned = _get_returned_qty(db, tenant_id, db_return.sale_id, exclude_return_id)
    remaining_qty = int(sale.qty or 0) - already_returned
    if db_return.qty > remaining_qty:
        raise HTTPException(
            status_code=400,
            detail=f"Only {max(remaining_qty, 0)} unit(s) are available to return for this sale"
        )

    if not db_return.unit_price:
        db_return.unit_price = sale.unit_price or 0.0
    db_return.total_amount = _return_amount(db_return)

def _apply_approved_return_stock(db: Session, tenant_id: str, db_return: models.ReturnEntry):
    if not db_return.book_id:
        return

    book = db.query(Book).filter(Book.tenant_id == tenant_id, Book.id == db_return.book_id).first()
    if book:
        book.stock_available += db_return.qty

    db_stock = StockEntry(
        tenant_id=tenant_id,
        book_id=db_return.book_id,
        book_name=db_return.book_name,
        quantity=db_return.qty,
        movement_type="return",
        remarks=f"Approved return from {db_return.student_name}"
    )
    db.add(db_stock)

def _revert_approved_return_stock(db: Session, tenant_id: str, db_return: models.ReturnEntry):
    if not db_return.book_id:
        return

    book = db.query(Book).filter(Book.tenant_id == tenant_id, Book.id == db_return.book_id).first()
    if book:
        book.stock_available -= db_return.qty

def create_return(db: Session, tenant_id: str, return_data: schemas.ReturnCreate):
    db_return = models.ReturnEntry(**return_data.dict(), tenant_id=tenant_id)
    _validate_return_qty(db, tenant_id, db_return)
    db.add(db_return)

    if db_return.status == "Approved":
        _apply_approved_return_stock(db, tenant_id, db_return)

    db.commit()
    db.refresh(db_return)
    return db_return

def get_returns(db: Session, tenant_id: str, skip: int = 0, limit: int = 100):
    if not tenant_id or tenant_id == "default":
        return []
    return db.query(models.ReturnEntry).filter(models.ReturnEntry.tenant_id == tenant_id).offset(skip).limit(limit).all()

def get_return(db: Session, tenant_id: str, return_id: int):
    return db.query(models.ReturnEntry).filter(
        models.ReturnEntry.tenant_id == tenant_id, 
        models.ReturnEntry.id == return_id
    ).first()

def update_return(db: Session, tenant_id: str, return_id: int, return_data: schemas.ReturnUpdate):
    db_return = db.query(models.ReturnEntry).filter(
        models.ReturnEntry.tenant_id == tenant_id, 
        models.ReturnEntry.id == return_id
    ).first()
    if db_return:
        old_status = db_return.status
        for key, value in return_data.dict().items():
            setattr(db_return, key, value)

        _validate_return_qty(db, tenant_id, db_return, exclude_return_id=return_id)

        if old_status != "Approved" and db_return.status == "Approved":
            _apply_approved_return_stock(db, tenant_id, db_return)
        elif old_status == "Approved" and db_return.status != "Approved":
            _revert_approved_return_stock(db, tenant_id, db_return)

        db.commit()
        db.refresh(db_return)
    return db_return

def delete_return(db: Session, tenant_id: str, return_id: int):
    db_return = db.query(models.ReturnEntry).filter(
        models.ReturnEntry.tenant_id == tenant_id, 
        models.ReturnEntry.id == return_id
    ).first()
    if db_return:
        if db_return.status == "Approved":
            _revert_approved_return_stock(db, tenant_id, db_return)
                
        db.delete(db_return)
        db.commit()
        return True
    return False
