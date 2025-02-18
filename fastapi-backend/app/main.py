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
from fastapi.exceptions import HTTPException

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

# Ensure static directory is correctly set
static_directory = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
os.makedirs(static_directory, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=static_directory), name="static")


# Add an explicit route for the root endpoint
@app.get("/", response_class=FileResponse)
async def root():
    index_path = os.path.join(static_directory, "index.html")

    # Log for debugging
    logger.info(
        "Attempting to serve index.html from: %s\n" "Static directory contents: %s",
        index_path,
        (
            os.listdir(static_directory)
            if os.path.exists(static_directory)
            else "Directory does not exist"
        ),
    )

    if os.path.exists(index_path):
        return index_path
    else:
        logger.error("index.html not found in static directory")
        raise HTTPException(status_code=404, detail="Index file not found")


# Keep the catch-all route for client-side routing
@app.get("/{path:path}")
async def serve_static_files(path: str):
    logger.info(f"Serving path: {path}")

    # If path is empty or just '/', serve index.html
    if not path or path == "/":
        index_path = os.path.join(static_directory, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        else:
            logger.error(f"Index file not found at {index_path}")
            raise HTTPException(status_code=404, detail="Index file not found")

    # Try to serve the specific file first
    file_path = os.path.join(static_directory, path)

    # If the specific file doesn't exist, serve index.html
    if not os.path.exists(file_path):
        index_path = os.path.join(static_directory, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)

    # If it's a static file, serve it
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)

    # If no file is found, return a 404
    logger.error(f"File not found: {file_path}")
    raise HTTPException(status_code=404, detail="File not found")


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
