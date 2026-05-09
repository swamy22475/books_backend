from sqlalchemy.orm import Session
from . import models, schemas
from ..inventory.models import Book

def add_stock(db: Session, stock: schemas.StockCreate):
    # Add stock entry
    db_stock = models.StockEntry(**stock.dict())
    db.add(db_stock)
    
    # Update book inventory
    book = db.query(Book).filter(Book.id == stock.book_id).first()
    if book:
        book.total_qty += stock.quantity
        book.stock_available += stock.quantity
    
    db.commit()
    db.refresh(db_stock)
    return db_stock

def get_stocks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.StockEntry).offset(skip).limit(limit).all()

def get_stock(db: Session, stock_id: int):
    return db.query(models.StockEntry).filter(models.StockEntry.id == stock_id).first()

def update_stock(db: Session, stock_id: int, stock: schemas.StockUpdate):
    db_stock = db.query(models.StockEntry).filter(models.StockEntry.id == stock_id).first()
    if not db_stock:
        return None
    
    # Update book inventory if quantity changed or book changed
    if db_stock.book_id == stock.book_id:
        # Same book, just update quantity difference
        qty_diff = stock.quantity - db_stock.quantity
        book = db.query(Book).filter(Book.id == db_stock.book_id).first()
        if book:
            book.total_qty += qty_diff
            book.stock_available += qty_diff
    else:
        # Book changed: revert old book, update new book
        old_book = db.query(Book).filter(Book.id == db_stock.book_id).first()
        if old_book:
            old_book.total_qty -= db_stock.quantity
            old_book.stock_available -= db_stock.quantity
        
        new_book = db.query(Book).filter(Book.id == stock.book_id).first()
        if new_book:
            new_book.total_qty += stock.quantity
            new_book.stock_available += stock.quantity

    # Update stock entry fields
    for key, value in stock.dict().items():
        setattr(db_stock, key, value)
    
    db.commit()
    db.refresh(db_stock)
    return db_stock

def delete_stock(db: Session, stock_id: int):
    db_stock = db.query(models.StockEntry).filter(models.StockEntry.id == stock_id).first()
    if db_stock:
        # Revert book inventory
        book = db.query(Book).filter(Book.id == db_stock.book_id).first()
        if book:
            book.total_qty -= db_stock.quantity
            book.stock_available -= db_stock.quantity
        
        db.delete(db_stock)
        db.commit()
    return db_stock
