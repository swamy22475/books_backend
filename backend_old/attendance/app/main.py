from fastapi import FastAPI
from .routes import router as attendance_router
from .database import Base, engine

# Create tables (for demo / initial run)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Attendance Module")
app.include_router(attendance_router)

@app.get("/health")
def health():
    return {"status":"ok"}
