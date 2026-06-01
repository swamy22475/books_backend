from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Database
from .core.database import init_db

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Routers
from .modules.vendors.router import router as vendor_router
from .modules.inventory.router import router as inventory_router
from .modules.stock.router import router as stock_router
from .modules.sales.router import router as sales_router
from .modules.returns.router import router as returns_router
from .modules.reports.router import router as reports_router
from .modules.dashboard.router import router as dashboard_router
from .modules.auth.router import router as auth_router
from .modules.academics.router import router as academics_router

# FastAPI App
app = FastAPI(
    title="MindWhile ERP - Book Sales API",
    version="1.0.0"
)

# =========================
# CORS CONFIG
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change later to frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import Request

@app.middleware("http")
async def log_tenant_header(request: Request, call_next):
    tenant_id = request.headers.get("X-Tenant-ID")
    logger.info(f"Incoming Request: {request.method} {request.url.path} | X-Tenant-ID: {tenant_id}")
    response = await call_next(request)
    return response
@app.get("/")
async def root():
    return {
        "message": "MindWhile ERP Book Sales API is running."
    }

# =========================
# HEALTH CHECK
# =========================
@app.get("/health")
async def health_check():
    try:
        db_status = init_db()

        return {
            "status": "online",
            "database": "connected" if db_status else "failed/disconnected"
        }

    except Exception as e:
        return {
            "status": "online",
            "database": "error",
            "details": str(e)
        }

# =========================
# DATABASE TEST ROUTE
# =========================
@app.get("/test-db")
async def test_db():
    try:
        db_status = init_db()

        if db_status:
            return {
                "database": "connected"
            }

        return {
            "database": "failed"
        }

    except Exception as e:
        return {
            "error": str(e)
        }

# =========================
# STARTUP EVENT
# =========================
@app.on_event("startup")
async def startup_event():
    logger.info("Application starting up...")

    try:
        success = init_db()

        if success:
            logger.info("Database successfully connected.")

            # Import Base, engine and models only after init_db succeeds
            from .core.database import Base, engine
            from .modules.vendors.models import Vendor
            from .modules.inventory.models import Book
            from .modules.stock.models import StockEntry
            from .modules.sales.models import Sale
            from .modules.returns.models import ReturnEntry
            from .modules.auth.models import User, School
            from .modules.academics.models import AcademicClass, AcademicSection

            logger.info("Creating database tables...")
            
            if engine:
                Base.metadata.create_all(bind=engine)
                logger.info("Tables created successfully.")
            else:
                logger.error("Engine is still None after init_db.")

        else:
            logger.error("Database connection FAILED.")

    except Exception as e:
        logger.error(f"Startup database error: {str(e)}")
# =========================
# API ROUTES
# =========================
api_v1_prefix = "/api/v1"

app.include_router(
    vendor_router,
    prefix=f"{api_v1_prefix}/vendors",
    tags=["Vendors"]
)

app.include_router(
    inventory_router,
    prefix=f"{api_v1_prefix}/inventory",
    tags=["Inventory"]
)

app.include_router(
    stock_router,
    prefix=f"{api_v1_prefix}/stock",
    tags=["Stock In"]
)

app.include_router(
    sales_router,
    prefix=f"{api_v1_prefix}/sales",
    tags=["Sales"]
)

app.include_router(
    returns_router,
    prefix=f"{api_v1_prefix}/returns",
    tags=["Returns"]
)

app.include_router(
    reports_router,
    prefix=f"{api_v1_prefix}/reports",
    tags=["Reports"]
)

app.include_router(
    dashboard_router,
    prefix=f"{api_v1_prefix}/dashboard",
    tags=["Dashboard"]
)

app.include_router(
    auth_router,
    tags=["Authentication"]
)

app.include_router(
    academics_router,
    prefix=f"{api_v1_prefix}/academics",
    tags=["Academics"]
)