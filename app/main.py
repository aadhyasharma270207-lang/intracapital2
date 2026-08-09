from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from app.db.database import init_db
from app.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("[STARTUP] Initializing Intracapital database tables...")
    init_db()
    logger.info("[STARTUP] Intracapital Backend fully online and ready.")
    yield


app = FastAPI(
    title="Intracapital API",
    description="Discovering Businesses Hidden Inside Enterprise Assets using IBM Granite & Local AI Stack",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for local/frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(api_router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"[ERROR] Internal server exception at {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal error occurred during local processing. Details logged securely."}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
