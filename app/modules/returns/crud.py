from sqlalchemy.orm import Session
from . import models, schemas
from ..inventory.models import Book
from ..stock.models import StockEntry

def create_return(db: Session, return_data: schemas.ReturnCreate):
    db_return = models.ReturnEntry(**return_data.dict())
    db.add(db_return)
    
    # Update inventory stock and log movement
    if db_return.book_id:
        book = db.query(Book).filter(Book.id == db_return.book_id).first()
        if book:
            book.stock_available += db_return.qty
            
        # Add entry to 'stock' table (Positive qty for return)
        db_stock = StockEntry(
            book_id=db_return.book_id,
            quantity=db_return.qty
        )
        db.add(db_stock)
            
    db.commit()
    db.refresh(db_return)
    return db_return

def get_returns(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.ReturnEntry).offset(skip).limit(limit).all()

def get_return(db: Session, return_id: int):
    return db.query(models.ReturnEntry).filter(models.ReturnEntry.id == return_id).first()

def update_return(db: Session, return_id: int, return_data: schemas.ReturnUpdate):
    db_return = db.query(models.ReturnEntry).filter(models.ReturnEntry.id == return_id).first()
    if db_return:
        for key, value in return_data.dict().items():
            setattr(db_return, key, value)
        db.commit()
        db.refresh(db_return)
    return db_return

def delete_return(db: Session, return_id: int):
    db_return = db.query(models.ReturnEntry).filter(models.ReturnEntry.id == return_id).first()
    if db_return:
        # Revert inventory stock
        if db_return.book_id:
            book = db.query(Book).filter(Book.id == db_return.book_id).first()
            if book:
                book.stock_available -= db_return.qty
                
        db.delete(db_return)
        db.commit()
    return db_return
