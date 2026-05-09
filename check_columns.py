from sqlalchemy import create_engine, inspect
import os

DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Mindwhile123")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "books")

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

def check():
    inspector = inspect(engine)
    columns = [c['name'] for c in inspector.get_columns("sales")]
    print(f"Columns in 'sales' table: {columns}")
    if "book_selection" in columns:
        print("✅ book_selection column exists.")
    else:
        print("❌ book_selection column is MISSING!")

if __name__ == "__main__":
    check()
