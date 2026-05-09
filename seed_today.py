from app.database import SessionLocal, engine, Base
from app.modules.vendors.models import Vendor
from app.modules.inventory.models import Book
from app.modules.sales.models import Sale
from datetime import datetime

# Ensure all models are known to Base
import app.modules.vendors.models
import app.modules.inventory.models
import app.modules.sales.models

def seed_today():
    db = SessionLocal()
    try:
        # 1. Create a dummy book if none exists
        book = db.query(Book).first()
        if not book:
            book = Book(
                name="Mathematics Class 10",
                book_class="Class 10",
                selling_price=500,
                stock_available=100,
                total_qty=100
            )
            db.add(book)
            db.commit()
            db.refresh(book)

        # 2. Add a sale for today
        new_sale = Sale(
            book_id=book.id,
            student_name="Test Student",
            student_class="Class 10",
            book_name=book.name,
            qty=2,
            unit_price=500,
            total_amount=1000,
            payment_method="Cash",
            date=datetime.now()
        )
        db.add(new_sale)
        db.commit()
        print("Success: Added a sale of ₹1,000 for Today!")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_today()
