from sqlalchemy.orm import Session
from . import models, schemas
from ..inventory.models import Book
from ..stock.models import StockEntry

def get_sales(db: Session, tenant_id: str, skip: int = 0, limit: int = 100):
    if not tenant_id or tenant_id == "default":
        return []
    return db.query(models.Sale).filter(models.Sale.tenant_id == tenant_id).order_by(models.Sale.date.desc()).offset(skip).limit(limit).all()

def get_sale(db: Session, tenant_id: str, sale_id: int):
    return db.query(models.Sale).filter(models.Sale.tenant_id == tenant_id, models.Sale.id == sale_id).first()

def create_sale(db: Session, tenant_id: str, sale: schemas.SaleCreate):
    data = sale.model_dump(by_alias=True)
    db_sale = models.Sale(
        tenant_id=tenant_id,
        book_id=data.get("book_id"),
        student_name=data.get("student_name"),
        student_phone=data.get("student_phone"),
        student_class=data.get("class"),
        book_name=data.get("book_name"),
        book_type=data.get("book_type", "Set"),
        qty=data.get("qty"),
        unit_price=data.get("unit_price", 0.0),
        total_amount=data.get("total_amount"),
        paid_amount=data.get("paid_amount", 0.0),
        concession=data.get("concession", 0.0),
        remaining_amount=data.get("remaining_amount", 0.0),
        payment_method=data.get("payment_method"),
        book_selection=data.get("book_selection", "Single")
    )
    db.add(db_sale)
    
    # 1. Update inventory stock available
    if db_sale.book_id:
        book = db.query(Book).filter(Book.tenant_id == tenant_id, Book.id == db_sale.book_id).first()
        if book:
            book.stock_available -= db_sale.qty
            
        # Add entry to 'stock' table for tracking
        db_stock = StockEntry(
            tenant_id=tenant_id,
            book_id=db_sale.book_id,
            quantity=-db_sale.qty  # Negative to show stock going out
        )
        db.add(db_stock)
            
    db.commit()
    db.refresh(db_sale)
    return db_sale

def update_sale(db: Session, tenant_id: str, sale_id: int, sale: schemas.SaleCreate):
    db_sale = db.query(models.Sale).filter(models.Sale.tenant_id == tenant_id, models.Sale.id == sale_id).first()
    if db_sale:
        data = sale.model_dump(by_alias=True)
        
        # Handle stock update if qty or book changed
        if db_sale.book_id == data.get("book_id"):
            qty_diff = data.get("qty") - db_sale.qty
            book = db.query(Book).filter(Book.tenant_id == tenant_id, Book.id == db_sale.book_id).first()
            if book:
                book.stock_available -= qty_diff
        else:
            # Book changed: revert old, deduct new
            old_book = db.query(Book).filter(Book.tenant_id == tenant_id, Book.id == db_sale.book_id).first()
            if old_book:
                old_book.stock_available += db_sale.qty
            
            new_book = db.query(Book).filter(Book.tenant_id == tenant_id, Book.id == data.get("book_id")).first()
            if new_book:
                new_book.stock_available -= data.get("qty")

        db_sale.book_id = data.get("book_id")
        db_sale.student_name = data.get("student_name")
        db_sale.student_phone = data.get("student_phone")
        db_sale.student_class = data.get("class")
        db_sale.book_name = data.get("book_name")
        db_sale.book_type = data.get("book_type")
        db_sale.qty = data.get("qty")
        db_sale.unit_price = data.get("unit_price")
        db_sale.total_amount = data.get("total_amount")
        db_sale.paid_amount = data.get("paid_amount", 0.0)
        db_sale.concession = data.get("concession", 0.0)
        db_sale.remaining_amount = data.get("remaining_amount", 0.0)
        db_sale.payment_method = data.get("payment_method")
        db_sale.book_selection = data.get("book_selection")
        db.commit()
        db.refresh(db_sale)
    return db_sale

def delete_sale(db: Session, tenant_id: str, sale_id: int):
    db_sale = db.query(models.Sale).filter(models.Sale.tenant_id == tenant_id, models.Sale.id == sale_id).first()
    if db_sale:
        # Revert inventory stock
        if db_sale.book_id:
            book = db.query(Book).filter(Book.tenant_id == tenant_id, Book.id == db_sale.book_id).first()
            if book:
                book.stock_available += db_sale.qty
        
        db.delete(db_sale)
        db.commit()
    return db_sale
