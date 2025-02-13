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

    # Add sslmode=require if not present
    query_params = urllib.parse.parse_qs(parsed_url.query)
    if "sslmode" not in query_params:
        query_params["sslmode"] = ["require"]

    # Reconstruct the URL with SSL parameters
    new_query = urllib.parse.urlencode(query_params, doseq=True)

    # Reconstruct the URL, ensuring proper encoding
    POSTGRES_URL = urllib.parse.urlunparse(
        (
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            parsed_url.params,
            new_query,
            parsed_url.fragment,
        )
    )

    # Ensure postgres:// prefix for SQLAlchemy
    if POSTGRES_URL.startswith("postgres://"):
        POSTGRES_URL = POSTGRES_URL.replace("postgres://", "postgresql://", 1)

SQLALCHEMY_DATABASE_URL = POSTGRES_URL or "sqlite:///./sql_app.db"

# SSL configuration
connect_args = {"sslmode": "require", "connect_timeout": 30}

# Create engine with SSL config
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Add more verbose error handling
try:
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


def get_database_url():
    url = os.getenv("DATABASE_URL")
    if url and url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url
