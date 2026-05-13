from sqlalchemy.orm import Session
from . import models, schemas
from ..inventory.models import Book
from ..vendors.models import Vendor

def _stock_payload(stock: schemas.StockCreate):
    data = stock.model_dump() if hasattr(stock, "model_dump") else stock.dict()
    data = {key: value for key, value in data.items() if value is not None}
    if not data.get("movement_type"):
        data["movement_type"] = "stock_in"
    return data

def _normalize_stock_row(row):
    stock, book, vendor = row
    return {
        "id": stock.id,
        "book_id": stock.book_id,
        "book_name": stock.book_name or (book.name if book else None),
        "book_class": book.book_class if book else None,
        "book_type": book.book_type if book else None,
        "vendor_id": stock.vendor_id or (book.vendor_id if book else None),
        "vendor_name": stock.vendor_name or (vendor.name if vendor else None) or (book.vendor_name if book else None),
        "quantity": stock.quantity,
        "invoice_no": stock.invoice_no,
        "remarks": stock.remarks,
        "movement_type": stock.movement_type or ("stock_in" if stock.quantity >= 0 else "sale"),
        "tenant_id": stock.tenant_id,
        "date": stock.date,
    }

def add_stock(db: Session, tenant_id: str, stock: schemas.StockCreate):
    data = _stock_payload(stock)
    book = db.query(Book).filter(Book.tenant_id == tenant_id, Book.id == data["book_id"]).first()
    vendor = None
    if data.get("vendor_id"):
        vendor = db.query(Vendor).filter(Vendor.tenant_id == tenant_id, Vendor.id == data["vendor_id"]).first()
    if not vendor and data.get("vendor_name"):
        vendor = db.query(Vendor).filter(Vendor.tenant_id == tenant_id, Vendor.name == data["vendor_name"]).first()

    data["book_name"] = data.get("book_name") or (book.name if book else None)
    data["vendor_id"] = data.get("vendor_id") or (vendor.id if vendor else None) or (book.vendor_id if book else None)
    data["vendor_name"] = data.get("vendor_name") or (vendor.name if vendor else None) or (book.vendor_name if book else None)

    # Add stock entry
    db_stock = models.StockEntry(**data, tenant_id=tenant_id)
    db.add(db_stock)
    
    # Update book inventory
    if book:
        book.total_qty += data["quantity"]
        book.stock_available += data["quantity"]
    
    db.commit()
    db.refresh(db_stock)
    return db_stock

def get_stocks(db: Session, tenant_id: str, skip: int = 0, limit: int = 100):
    if not tenant_id or tenant_id == "default":
        return []
    rows = (
        db.query(models.StockEntry, Book, Vendor)
        .outerjoin(Book, (Book.id == models.StockEntry.book_id) & (Book.tenant_id == models.StockEntry.tenant_id))
        .outerjoin(Vendor, (Vendor.id == models.StockEntry.vendor_id) & (Vendor.tenant_id == models.StockEntry.tenant_id))
        .filter(models.StockEntry.tenant_id == tenant_id)
        .order_by(models.StockEntry.date.desc(), models.StockEntry.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [_normalize_stock_row(row) for row in rows]

def get_stock(db: Session, tenant_id: str, stock_id: int):
    return db.query(models.StockEntry).filter(
        models.StockEntry.tenant_id == tenant_id, 
        models.StockEntry.id == stock_id
    ).first()

def update_stock(db: Session, tenant_id: str, stock_id: int, stock: schemas.StockUpdate):
    db_stock = db.query(models.StockEntry).filter(
        models.StockEntry.tenant_id == tenant_id, 
        models.StockEntry.id == stock_id
    ).first()
    if not db_stock:
        return None
    
    # Update book inventory if quantity changed or book changed
    data = _stock_payload(stock)
    if db_stock.book_id == data["book_id"]:
        # Same book, just update quantity difference
        qty_diff = data["quantity"] - db_stock.quantity
        book = db.query(Book).filter(Book.tenant_id == tenant_id, Book.id == db_stock.book_id).first()
        if book:
            book.total_qty += qty_diff
            book.stock_available += qty_diff
    else:
        # Book changed: revert old book, update new book
        old_book = db.query(Book).filter(Book.tenant_id == tenant_id, Book.id == db_stock.book_id).first()
        if old_book:
            old_book.total_qty -= db_stock.quantity
            old_book.stock_available -= db_stock.quantity
        
        new_book = db.query(Book).filter(Book.tenant_id == tenant_id, Book.id == data["book_id"]).first()
        if new_book:
            new_book.total_qty += data["quantity"]
            new_book.stock_available += data["quantity"]

    # Update stock entry fields
    for key, value in data.items():
        setattr(db_stock, key, value)
    
    db.commit()
    db.refresh(db_stock)
    return db_stock

def delete_stock(db: Session, tenant_id: str, stock_id: int):
    db_stock = db.query(models.StockEntry).filter(
        models.StockEntry.tenant_id == tenant_id, 
        models.StockEntry.id == stock_id
    ).first()
    if db_stock:
        # Revert book inventory
        book = db.query(Book).filter(Book.tenant_id == tenant_id, Book.id == db_stock.book_id).first()
        if book:
            book.total_qty -= db_stock.quantity
            book.stock_available -= db_stock.quantity
        
        db.delete(db_stock)
        db.commit()
    return db_stock
