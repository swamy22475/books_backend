from sqlalchemy import create_engine, text
import os

DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Mindwhile123")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "books")

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

def sync():
    with engine.connect() as conn:
        print("Checking for missing columns in 'sales' table...")
        
        # Check book_selection
        result = conn.execute(text("SHOW COLUMNS FROM sales LIKE 'book_selection'"))
        if not result.fetchone():
            print("Adding column 'book_selection' to 'sales'...")
            conn.execute(text("ALTER TABLE sales ADD COLUMN book_selection VARCHAR(20) DEFAULT 'Single'"))
            print("Column 'book_selection' added.")
        else:
            print("Column 'book_selection' already exists.")
            
        conn.commit()

        # Check inventory table
        print("Checking for missing columns in 'books' table...")
        cols_to_add = {
            "total_qty": "INT DEFAULT 0",
            "sets_qty": "INT DEFAULT 0",
            "singles_qty": "INT DEFAULT 0"
        }
        for col, definition in cols_to_add.items():
            result = conn.execute(text(f"SHOW COLUMNS FROM books LIKE '{col}'"))
            if not result.fetchone():
                print(f"Adding column '{col}' to 'books'...")
                conn.execute(text(f"ALTER TABLE books ADD COLUMN {col} {definition}"))
                print(f"Column '{col}' added.")
            else:
                print(f"Column '{col}' already exists.")
        
        # Check returns table
        print("Ensuring 'returns' table structure...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS returns (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_name VARCHAR(100) NOT NULL,
                student_class VARCHAR(50),
                book_name VARCHAR(150) NOT NULL,
                qty INT DEFAULT 1,
                reason VARCHAR(255),
                status VARCHAR(50) DEFAULT 'Pending',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # In case it already exists with old schema, add new columns
        return_cols = {
            "book_id": "INT",
            "student_name": "VARCHAR(100) NOT NULL",
            "student_class": "VARCHAR(50)",
            "book_name": "VARCHAR(150) NOT NULL",
            "qty": "INT DEFAULT 1",
            "reason": "VARCHAR(255)",
            "status": "VARCHAR(50) DEFAULT 'Pending'",
            "created_at": "DATETIME DEFAULT CURRENT_TIMESTAMP"
        }
        for col, definition in return_cols.items():
            res = conn.execute(text(f"SHOW COLUMNS FROM returns LIKE '{col}'"))
            if not res.fetchone():
                try:
                    conn.execute(text(f"ALTER TABLE returns ADD COLUMN {col} {definition}"))
                except Exception as e:
                    print(f"Note: Could not add {col} (might already exist or incompatible): {e}")

        conn.commit()
    print("Database sync complete!")

if __name__ == "__main__":
    sync()
