from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router
from app.core.config import get_settings
from app.middleware.security import SecurityHeadersMiddleware
from app.core.logging_config import configure_logging
import logging
from fastapi.staticfiles import StaticFiles
import os
from starlette.responses import FileResponse

# Configure logging before creating the FastAPI app
configure_logging()

logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Initialize FastAPI
app = FastAPI(title=settings.PROJECT_NAME, openapi_url="/openapi.json")

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

# Optionally, use the current working directory to locate/create the static folder.
static_directory = os.path.join(os.getcwd(), "static")
if not os.path.exists(static_directory):
    os.makedirs(static_directory)

# Mount the static files directory
app.mount("/static", StaticFiles(directory=static_directory), name="static")


# Custom middleware to set correct MIME types
@app.middleware("http")
async def add_content_type_headers(request, call_next):
    response = await call_next(request)
    if request.url.path.endswith(".js"):
        response.headers["Content-Type"] = "application/javascript"
    elif request.url.path.endswith(".css"):
        response.headers["Content-Type"] = "text/css"
    return response


# Log startup
logger.info("Starting FastAPI application...")

# Define the path to your frontend production build.
FRONTEND_DIST_PATH = os.path.join(os.path.dirname(__file__), "../static")


@app.get("/")
async def serve_index():
    """
    Serve the index.html from the production build of your React app.
    """
    index_file_path = os.path.join(os.getcwd(), "static", "index.html")
    return FileResponse(index_file_path)


@app.get("/test")
def test_prints():
    logger.info("Test endpoint hit")
    print("Test print 1")
    print("Test print 2")
    return {"message": "Check your console for prints"}


# Register routes without prefix
logger.info("Registering API routes...")
app.include_router(api_router)
logger.info("API routes registered successfully")
