from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import SessionLocal, engine, Base
from app.modules.vendors.models import Vendor
from app.modules.inventory.models import Book
import sys

def seed():
    print("Clearing existing data...")
    # This will create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Clear existing data
        print("Clearing existing data...")
        with engine.connect() as conn:
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            conn.execute(text("DELETE FROM vendors"))
            conn.execute(text("DELETE FROM books"))
            conn.execute(text("DELETE FROM sales"))
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
            conn.commit()

        print("Adding dummy Vendors...")
        vendors = [
            Vendor(name="Oxford University Press", vendor_type="Publisher", contact="1234567890", address="London, UK", payment_method="Credit Card", books_supplied=150, total_amount=45000.0),
            Vendor(name="Pearson Education", vendor_type="Publisher", contact="9876543210", address="New York, USA", payment_method="Bank Transfer", books_supplied=200, total_amount=60000.0),
            Vendor(name="Global Book Distributors", vendor_type="Wholesaler", contact="5556667777", address="New Delhi, India", payment_method="Cash", books_supplied=500, total_amount=120000.0),
        ]
        db.add_all(vendors)

        print("Adding dummy Books...")
        books = [
            Book(name="Mathematics for Grade 10", book_class="Class 10", book_type="Set", selling_price=450.0, stock_available=50),
            Book(name="English Grammar Pro", book_class="Class 10", book_type="Single", selling_price=300.0, stock_available=100),
            Book(name="Science Explorer", book_class="Class 8", book_type="Set", selling_price=550.0, stock_available=30),
            Book(name="History of the World", book_class="Class 9", book_type="Single", selling_price=400.0, stock_available=45),
            Book(name="Computer Science Basics", book_class="Class 7", book_type="Set", selling_price=350.0, stock_available=60),
        ]
        db.add_all(books)

        db.commit()
        print("Database seeded successfully!")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
