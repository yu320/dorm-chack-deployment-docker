from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette import status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import subprocess
import logging # Import logging

from app import models, schemas # Import schemas
from app.database import async_engine, AsyncSessionLocal
from app.api.api import api_router
from app.services.initialization import seed_database
from app.config import settings
from app.limiter import limiter
from slowapi.errors import RateLimitExceeded
from app.core.logging import setup_logging # Import setup_logging
from app.utils.i18n import _ # Import translation function

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This code runs on startup
    logger.info("Running database migrations...")
    
    # Get the absolute path to the backend directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Run alembic upgrade head
    try:
        import sys
        subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], check=True, cwd=backend_dir)
        logger.info("Database migrations complete.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Database migrations failed: {e}")
        # We might want to stop startup here, but for now we log error
    
    logger.info("Seeding database...")
    async with AsyncSessionLocal() as db:
        await seed_database(db) # Database seeding should be part of migration or manual process
    logger.info("Database seeding complete.")
    logger.info("Application startup complete.") # Add a message
    yield
    # This code runs on shutdown
    logger.info("Application shutdown.")

app = FastAPI(
    title="Student Dormitory Inspection API",
    description="API for managing student dormitory inspections.",
    version="0.1.0",
    lifespan=lifespan,
    openapi_url="/openapi.json" if settings.DEBUG else None # Conditional OpenAPI URL
)

app.state.limiter = limiter

# --- Global Exception Handlers ---
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=schemas.ErrorResponse(
            detail=exc.detail,
            status_code=exc.status_code
        ).model_dump()
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        # Extract the raw message (which might be a translation key)
        raw_msg = error.get("msg", "")
        # Remove "Value error, " prefix added by Pydantic if present
        if raw_msg.startswith("Value error, "):
            raw_msg = raw_msg.replace("Value error, ", "")
        
        # Translate the message
        translated_msg = _(raw_msg, request)
        
        # Reconstruct a simplified error object or just use the translated message
        # Here we keep the structure but update the message
        error_copy = error.copy()
        error_copy["msg"] = translated_msg
        errors.append(error_copy)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=schemas.ErrorResponse(
            detail=f"Validation Error: {errors}", # Use the translated errors
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        ).model_dump()
    )

@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": f"Rate limit exceeded: {exc.detail}"}
    )

from fastapi.staticfiles import StaticFiles

# --- CORS Middleware ---
# Origins are read from the environment settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# if not os.path.exists("uploads"):
#     os.makedirs("uploads")
# app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def read_root():
    """
    Root endpoint to check if the API is running.
    """
    return {"message": "Welcome to the Student Dormitory Inspection API!"}
