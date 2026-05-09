"""
Safe migration: adds paid_amount, remaining_amount, bill_no to vendors table if not already there.
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

columns_to_add = [
    ("paid_amount",      "ALTER TABLE vendors ADD COLUMN paid_amount FLOAT DEFAULT 0.0"),
    ("remaining_amount", "ALTER TABLE vendors ADD COLUMN remaining_amount FLOAT DEFAULT 0.0"),
    ("bill_no",          "ALTER TABLE vendors ADD COLUMN bill_no VARCHAR(100) DEFAULT NULL"),
]

with engine.connect() as conn:
    # Get existing columns
    rows = conn.execute(text("SHOW COLUMNS FROM vendors")).fetchall()
    existing = {r[0] for r in rows}
    print("Existing columns:", existing)

    for col_name, sql in columns_to_add:
        if col_name in existing:
            print(f"  SKIP  — '{col_name}' already exists.")
        else:
            try:
                conn.execute(text(sql))
                conn.commit()
                print(f"  ADDED — '{col_name}' successfully.")
            except Exception as e:
                print(f"  ERROR — '{col_name}': {e}")

print("\nDone. Current vendors columns:")
rows = conn.execute(text("SHOW COLUMNS FROM vendors")).fetchall()
for r in rows:
    print(f"  {r[0]:25s} {r[1]}")
