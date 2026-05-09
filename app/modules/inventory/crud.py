from sqlalchemy.orm import Session
from . import models, schemas

def get_books(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Book).offset(skip).limit(limit).all()

def get_book(db: Session, book_id: int):
    return db.query(models.Book).filter(models.Book.id == book_id).first()

def create_book(db: Session, book: schemas.BookCreate):
    db_book = models.Book(
        name=book.name,
        book_class=book.book_class,
        book_type=book.book_type,
        total_qty=book.total_qty,
        sets_qty=book.sets_qty,
        singles_qty=book.singles_qty,
        cost_price=book.cost_price,
        selling_price=book.selling_price,
        stock_available=book.stock_available,
        vendor_id=book.vendor_id,
        vendor_name=book.vendor_name,
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

def update_book(db: Session, book_id: int, book: schemas.BookCreate):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if db_book:
        db_book.name = book.name
        db_book.book_class = book.book_class
        db_book.book_type = book.book_type
        db_book.total_qty = book.total_qty
        db_book.sets_qty = book.sets_qty
        db_book.singles_qty = book.singles_qty
        db_book.cost_price = book.cost_price
        db_book.selling_price = book.selling_price
        db_book.stock_available = book.stock_available
        db_book.vendor_id = book.vendor_id
        db_book.vendor_name = book.vendor_name
        db.commit()
        db.refresh(db_book)
    return db_book

def delete_book(db: Session, book_id: int):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if db_book:
        db.delete(db_book)
        db.commit()
    return db_book
