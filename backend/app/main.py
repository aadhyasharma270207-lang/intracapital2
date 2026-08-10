import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.sqlite import engine, Base
from app.models.models import (
    Company, Asset, AssetChunk, Opportunity, 
    OpportunityEvidence, BusinessModel, ValidationResult, ProcessingJob
)
from app.api.routes import (
    health, system, company, assets, 
    discovery, opportunities, analytics, 
    architecture, demo, processing
)

# Configure system logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Run SQLite migrations at start
try:
    logger.info("Initializing SQLite database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully.")
except Exception as e:
    logger.critical(f"Critical error initializing database: {str(e)}")

# Initialize FastAPI App
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI Venture Intelligence Opportunity Discovery Platform backend engine.",
    version="1.0.0"
)

# Configure CORS
# Ensure FRONTEND_URL is loaded without wildcard fallback in production
origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
if settings.FRONTEND_URL and settings.FRONTEND_URL not in origins:
    origins.append(settings.FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers for structured API error responses
@app.exception_handler(Exception)
def generic_exception_handler(request: Request, exc: Exception):
    """
    Prevents raw Python trace errors from leaking to UI and formats structured outputs.
    """
    logger.error(f"Unhandled system error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "code": "INTERNAL_SERVER_ERROR",
            "message": "A critical system anomaly occurred inside the backend service.",
            "details": {"error_type": type(exc).__name__, "message": str(exc)}
        }
    )

# Mount Routers under /api
app.include_router(health.router, prefix="/api")
app.include_router(system.router, prefix="/api")
app.include_router(company.router, prefix="/api")
app.include_router(assets.router, prefix="/api")
app.include_router(discovery.router, prefix="/api")
app.include_router(opportunities.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(architecture.router, prefix="/api")
app.include_router(demo.router, prefix="/api")
app.include_router(processing.router, prefix="/api")

@app.get("/")
def get_root():
    """
    Quick endpoint redirect details
    """
    return {
        "message": "Welcome to INTRACAPITAL AI Venture Intelligence API Gateway.",
        "documentation": "/docs"
    }
