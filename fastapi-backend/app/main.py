from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router
from app.core.config import get_settings
from app.middleware.security import SecurityHeadersMiddleware
from app.core.logging_config import configure_logging
import logging

# Configure logging before creating the FastAPI app
configure_logging()

logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Initialize FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Add Security Headers Middleware
app.add_middleware(SecurityHeadersMiddleware)

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS_LIST,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
    expose_headers=["Content-Length"],
    max_age=3600,
)

# Log startup
logger.info("Starting FastAPI application...")

@app.get("/")
def read_root():
    logger.info("Root endpoint hit")
    return {"message": "Welcome to the FastAPI Text Analyzer"}

@app.get("/test")
def test_prints():
    logger.info("Test endpoint hit")
    print("Test print 1")
    print("Test print 2")
    return {"message": "Check your console for prints"}

# Register routes
logger.info("Registering API routes...")
app.include_router(api_router, prefix=settings.API_V1_STR)
logger.info("API routes registered successfully")