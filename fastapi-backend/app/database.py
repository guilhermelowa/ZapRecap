from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models.database_models import Base
from app.auth.models import Admin  # noqa: F401
import os
from dotenv import load_dotenv
import urllib.parse

# Load environment variables
load_dotenv()

# Get database URL from environment variable, fallback to SQLite for development
POSTGRES_URL = os.getenv("DATABASE_URL")

# Ensure the URL is properly parsed and encoded
if POSTGRES_URL:
    # Parse the URL to handle any special characters
    parsed_url = urllib.parse.urlparse(POSTGRES_URL)

    # Reconstruct the URL, ensuring proper encoding
    POSTGRES_URL = urllib.parse.urlunparse(
        (
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            parsed_url.params,
            parsed_url.query,
            parsed_url.fragment,
        )
    )

    # Ensure postgres:// prefix for SQLAlchemy
    if POSTGRES_URL.startswith("postgres://"):
        POSTGRES_URL = POSTGRES_URL.replace("postgres://", "postgresql://", 1)

SQLALCHEMY_DATABASE_URL = POSTGRES_URL or "sqlite:///./sql_app.db"

# Remove check_same_thread for PostgreSQL
connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}

# Add more verbose error handling
try:
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create tables
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Database connection error: {e}")
    raise


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
