from sqlalchemy.orm import Session
from . import models, schemas
from ..inventory.models import Book
from ..stock.models import StockEntry

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
