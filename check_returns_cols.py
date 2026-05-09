from sqlalchemy import create_engine, text
import os

DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Mindwhile123")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "books")

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

with engine.connect() as conn:
    res = conn.execute(text("SHOW COLUMNS FROM returns"))
    for row in res:
        print(row)
