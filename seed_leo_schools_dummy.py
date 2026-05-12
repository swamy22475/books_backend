from app.core import database
from app.core.database import Base, init_db
from app.modules.inventory.models import Book
from app.modules.returns.models import ReturnEntry
from app.modules.sales.models import Sale
from app.modules.stock.models import StockEntry
from app.modules.vendors.models import Vendor


TENANT_ID = "leo_schools"
MAX_ROWS = 10


VENDORS = [
    ("Leo Oxford Books", "Publisher", "9876500011", "MG Road, Hyderabad", "Bank Transfer", 120, 42000, 30000, "LEO-V-001", "Active"),
    ("Leo Pearson Supply", "Publisher", "9876500012", "Ameerpet, Hyderabad", "UPI", 95, 28500, 28500, "LEO-V-002", "Active"),
    ("Sri Vidya Distributors", "Wholesaler", "9876500013", "Koti, Hyderabad", "Cash", 180, 54000, 41000, "LEO-V-003", "Active"),
    ("Bright Kids Publications", "Publisher", "9876500014", "Secunderabad", "Cheque", 75, 22500, 12000, "LEO-V-004", "Active"),
    ("National School Books", "Wholesaler", "9876500015", "Begumpet, Hyderabad", "Card", 210, 63000, 50000, "LEO-V-005", "Active"),
    ("Scholastic Leo Partner", "Publisher", "9876500016", "Madhapur, Hyderabad", "Bank Transfer", 88, 35200, 35200, "LEO-V-006", "Active"),
    ("Excel Academic Depot", "Wholesaler", "9876500017", "Kukatpally, Hyderabad", "UPI", 160, 48000, 30000, "LEO-V-007", "Active"),
    ("Royal Stationery Mart", "Retailer", "9876500018", "Himayatnagar, Hyderabad", "Cash", 70, 17500, 10000, "LEO-V-008", "Active"),
    ("Bluebird Book House", "Publisher", "9876500019", "Banjara Hills, Hyderabad", "Cheque", 105, 36750, 20000, "LEO-V-009", "Active"),
    ("Campus Learning Supplies", "Wholesaler", "9876500020", "Gachibowli, Hyderabad", "Bank Transfer", 140, 56000, 45000, "LEO-V-010", "Active"),
]


BOOKS = [
    ("Leo Mathematics Kit", "Class 1, Class 2", "Set", 80, 45, 35, 180, 260),
    ("Leo English Reader", "Class 1", "Single", 120, 0, 120, 90, 150),
    ("Leo EVS Workbook", "Class 2", "Single", 100, 0, 100, 85, 140),
    ("Leo Science Explorer", "Class 3, Class 4", "Set", 75, 40, 35, 220, 320),
    ("Leo Social Studies", "Class 4", "Single", 90, 0, 90, 120, 190),
    ("Leo Hindi Pathmala", "Class 5", "Single", 85, 0, 85, 100, 165),
    ("Leo Computer Basics", "Class 6", "Set", 60, 32, 28, 250, 375),
    ("Leo General Knowledge", "Class 7", "Single", 110, 0, 110, 75, 130),
    ("Leo Advanced Mathematics", "Class 8", "Set", 55, 30, 25, 300, 450),
    ("Leo Grammar Practice", "Class 9, Class 10", "Single", 100, 0, 100, 130, 210),
]


STUDENTS = [
    ("Aarav Sharma", "9000001001", "Class 1"),
    ("Diya Reddy", "9000001002", "Class 2"),
    ("Vihaan Rao", "9000001003", "Class 3"),
    ("Ananya Gupta", "9000001004", "Class 4"),
    ("Ishaan Kumar", "9000001005", "Class 5"),
    ("Meera Patel", "9000001006", "Class 6"),
    ("Arjun Singh", "9000001007", "Class 7"),
    ("Saanvi Nair", "9000001008", "Class 8"),
    ("Rohan Verma", "9000001009", "Class 9"),
    ("Kavya Iyer", "9000001010", "Class 10"),
]


def add_vendors(db):
    existing_total = db.query(Vendor).filter(Vendor.tenant_id == TENANT_ID).count()
    created = []
    for name, vendor_type, contact, address, payment, supplied, total, paid, bill_no, status in VENDORS[: max(0, MAX_ROWS - existing_total)]:
        existing = db.query(Vendor).filter(Vendor.tenant_id == TENANT_ID, Vendor.name == name).first()
        if existing:
            created.append(existing)
            continue

        vendor = Vendor(
            tenant_id=TENANT_ID,
            name=name,
            vendor_type=vendor_type,
            contact=contact,
            address=address,
            payment_method=payment,
            books_supplied=supplied,
            total_amount=total,
            paid_amount=paid,
            remaining_amount=total - paid,
            bill_no=bill_no,
            status=status,
        )
        db.add(vendor)
        created.append(vendor)

    db.commit()
    return db.query(Vendor).filter(Vendor.tenant_id == TENANT_ID).limit(MAX_ROWS).all()


def add_books(db, vendors):
    existing_total = db.query(Book).filter(Book.tenant_id == TENANT_ID).count()
    created = []
    for idx, (name, book_class, book_type, total_qty, sets_qty, singles_qty, cost, selling) in enumerate(BOOKS[: max(0, MAX_ROWS - existing_total)]):
        existing = db.query(Book).filter(Book.tenant_id == TENANT_ID, Book.name == name).first()
        if existing:
            created.append(existing)
            continue

        vendor = vendors[idx % len(vendors)] if vendors else None
        book = Book(
            tenant_id=TENANT_ID,
            name=name,
            book_class=book_class,
            book_type=book_type,
            total_qty=total_qty,
            sets_qty=sets_qty,
            singles_qty=singles_qty,
            cost_price=cost,
            selling_price=selling,
            stock_available=total_qty,
            vendor_id=vendor.id if vendor else None,
            vendor_name=vendor.name if vendor else None,
        )
        db.add(book)
        created.append(book)

    db.commit()
    return db.query(Book).filter(Book.tenant_id == TENANT_ID).limit(MAX_ROWS).all()


def add_stock_entries(db, books):
    existing_count = db.query(StockEntry).filter(StockEntry.tenant_id == TENANT_ID, StockEntry.quantity > 0).count()
    for book in books[: max(0, MAX_ROWS - existing_count)]:
        db.add(StockEntry(tenant_id=TENANT_ID, book_id=book.id, quantity=book.total_qty or book.stock_available or 10))
    db.commit()


def add_sales(db, books):
    existing_count = db.query(Sale).filter(
        Sale.tenant_id == TENANT_ID,
        Sale.student_name.in_([student[0] for student in STUDENTS]),
    ).count()

    for idx, student in enumerate(STUDENTS[: max(0, MAX_ROWS - existing_count)]):
        book = books[idx % len(books)]
        qty = (idx % 3) + 1
        unit_price = float(book.selling_price or 100)
        total = unit_price * qty
        concession = 25.0 if idx % 2 else 0.0
        paid = total - concession if idx % 3 else max(total - concession - 100.0, 0.0)

        db.add(Sale(
            tenant_id=TENANT_ID,
            book_id=book.id,
            student_name=student[0],
            student_phone=student[1],
            student_class=student[2],
            book_name=book.name,
            book_type=book.book_type,
            qty=qty,
            unit_price=unit_price,
            total_amount=total,
            paid_amount=paid,
            concession=concession,
            remaining_amount=max(total - concession - paid, 0.0),
            payment_method=["Cash", "UPI", "Card", "Bank Transfer"][idx % 4],
            book_selection=book.book_type or "Single",
        ))

        if book.stock_available is not None:
            book.stock_available = max(book.stock_available - qty, 0)

    db.commit()


def add_returns(db, books):
    existing_count = db.query(ReturnEntry).filter(
        ReturnEntry.tenant_id == TENANT_ID,
        ReturnEntry.student_name.in_([student[0] for student in STUDENTS]),
    ).count()

    reasons = ["Wrong book selected", "Damaged copy", "Duplicate purchase", "Class changed", "Parent requested exchange"]
    for idx, student in enumerate(STUDENTS[: max(0, min(5, MAX_ROWS - existing_count))]):
        book = books[idx % len(books)]
        db.add(ReturnEntry(
            tenant_id=TENANT_ID,
            book_id=book.id,
            student_name=student[0],
            student_class=student[2],
            book_name=book.name,
            qty=1,
            reason=reasons[idx % len(reasons)],
            status=["Pending", "Approved", "Rejected"][idx % 3],
        ))

    db.commit()


def seed():
    if not init_db():
        raise RuntimeError("Database connection failed. Check DATABASE_URL.")

    Base.metadata.create_all(bind=database.engine)
    db = database.SessionLocal()

    try:
        vendor_count = db.query(Vendor).filter(Vendor.tenant_id == TENANT_ID).count()
        if vendor_count > MAX_ROWS:
            overflow = vendor_count - MAX_ROWS
            demo_names = [vendor[0] for vendor in reversed(VENDORS)]
            for name in demo_names:
                if overflow <= 0:
                    break
                vendor = db.query(Vendor).filter(Vendor.tenant_id == TENANT_ID, Vendor.name == name).first()
                if vendor:
                    db.delete(vendor)
                    overflow -= 1
            db.commit()

        vendors = add_vendors(db)
        books = add_books(db, vendors)
        add_stock_entries(db, books)
        add_sales(db, books)
        add_returns(db, books)

        print(f"Seeded tenant: {TENANT_ID}")
        print(f"Vendors: {db.query(Vendor).filter(Vendor.tenant_id == TENANT_ID).count()}")
        print(f"Books: {db.query(Book).filter(Book.tenant_id == TENANT_ID).count()}")
        print(f"Stock entries: {db.query(StockEntry).filter(StockEntry.tenant_id == TENANT_ID).count()}")
        print(f"Sales: {db.query(Sale).filter(Sale.tenant_id == TENANT_ID).count()}")
        print(f"Returns: {db.query(ReturnEntry).filter(ReturnEntry.tenant_id == TENANT_ID).count()}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
