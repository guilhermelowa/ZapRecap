from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Log startup
logger.info("Starting FastAPI application...")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Adjust to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],
)

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
app.include_router(api_router)
logger.info("API routes registered successfully")