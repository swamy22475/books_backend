from sqlalchemy import text

from app.core import database
from app.core.database import init_db


def fix_sales_balances():
    if not init_db():
        raise RuntimeError("Database connection failed. Check DATABASE_URL.")

    with database.engine.begin() as connection:
        result = connection.execute(text("""
            UPDATE sales
            SET remaining_amount = GREATEST(total_amount - IFNULL(concession, 0) - IFNULL(paid_amount, 0), 0)
            WHERE IFNULL(paid_amount, 0) = 0
              AND IFNULL(remaining_amount, 0) = 0
              AND total_amount > IFNULL(concession, 0)
        """))
        print(f"Updated sale rows: {result.rowcount}")


if __name__ == "__main__":
    fix_sales_balances()
