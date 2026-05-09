from app.database import SessionLocal, engine, Base
from app.modules.vendors.models import Vendor
from app.modules.inventory.models import Book
from app.modules.sales.models import Sale
from app.modules.returns.models import ReturnEntry
from app.modules.stock.models import StockEntry

def clear_data():
    print("Connecting to database...")
    db = SessionLocal()
    try:
        print("Clearing tables...")
        # Order matters due to foreign keys: clear child tables first
        db.query(ReturnEntry).delete()
        db.query(Sale).delete()
        db.query(StockEntry).delete()
        db.query(Book).delete()
        db.query(Vendor).delete()
        
        db.commit()
        print("All data cleared successfully!")
    except Exception as e:
        print(f"Error clearing data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clear_data()
