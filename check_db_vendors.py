from app.database import engine
from sqlalchemy import text

def check():
    try:
        with engine.connect() as conn:
            tables = conn.execute(text('SHOW TABLES')).fetchall()
            print("Tables found:", [t[0] for t in tables])
            
            if 'vendors' in [t[0] for t in tables]:
                print("Vendors table exists.")
                columns = conn.execute(text('SHOW COLUMNS FROM vendors')).fetchall()
                print("Columns in vendors:", [c[0] for c in columns])
            else:
                print("Vendors table MISSING!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check()
