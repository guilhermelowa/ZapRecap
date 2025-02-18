from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router
from app.core.config import get_settings
from app.middleware.security import SecurityHeadersMiddleware
from app.core.logging_config import configure_logging
import logging
from fastapi.staticfiles import StaticFiles
import os
from starlette.responses import FileResponse, HTMLResponse

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
    # Try multiple potential paths for index.html
    possible_paths = [
        os.path.join(os.getcwd(), "static", "index.html"),
        os.path.join(os.path.dirname(__file__), "..", "static", "index.html"),
        os.path.join(os.path.dirname(__file__), "static", "index.html"),
        os.path.join(os.getcwd(), "fastapi-backend", "static", "index.html"),
    ]

    logger.info(f"Searching for index.html in possible paths: {possible_paths}")

    for index_file_path in possible_paths:
        logger.info(f"Checking path: {index_file_path}")
        if os.path.exists(index_file_path):
            logger.info(f"Found index.html at: {index_file_path}")
            return FileResponse(index_file_path)

    # Log all files in potential directories
    for directory in set(os.path.dirname(path) for path in possible_paths):
        try:
            if os.path.exists(directory):
                logger.info(f"Files in {directory}: {os.listdir(directory)}")
        except Exception as e:
            logger.error(f"Error listing files in {directory}: {e}")

    # If no index.html is found, create a basic fallback
    logger.warning("No index.html found. Serving fallback content.")
    fallback_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ZapRecap</title>
    </head>
    <body>
        <div id="root">Application not loaded. Please check your build.</div>
        <p>Current working directory: {}</p>
        <p>Script directory: {}</p>
    </body>
    </html>
    """.format(
        os.getcwd(), os.path.dirname(__file__)
    )

    return HTMLResponse(content=fallback_content)


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
