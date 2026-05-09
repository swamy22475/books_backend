import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    try:
        # Check if table exists first
        conn.execute(text("ALTER TABLE books MODIFY COLUMN book_class VARCHAR(255)"))
        conn.commit()
        print("Successfully updated books.book_class to VARCHAR(255)")
    except Exception as e:
        print(f"Error: {e}")
