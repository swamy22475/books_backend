from sync_db import engine
from sqlalchemy import text

with engine.connect() as conn:
    print("Dropping 'returns' table...")
    conn.execute(text("DROP TABLE IF EXISTS returns"))
    conn.commit()
    print("Done.")
