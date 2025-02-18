from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models.database_models import Base
from app.auth.models import Admin  # noqa: F401
import os
from dotenv import load_dotenv
import urllib.parse

# Load environment variables
load_dotenv()

# Determine environment
is_testing = os.getenv("TESTING", "False") == "True"


def get_database_url():
    # Prioritize test database for testing environment
    if is_testing:
        return "sqlite:///./test.db"

    # Get database URL from environment variable
    POSTGRES_URL = os.getenv("DATABASE_URL")

    if not POSTGRES_URL:
        return "sqlite:///./sql_app.db"

    # Ensure postgres:// is converted to postgresql://
    if POSTGRES_URL.startswith("postgres://"):
        POSTGRES_URL = POSTGRES_URL.replace("postgres://", "postgresql://", 1)

    # Parse the URL
    parsed_url = urllib.parse.urlparse(POSTGRES_URL)

    # Extract components
    username = parsed_url.username
    password = parsed_url.password
    host = parsed_url.hostname
    port = parsed_url.port or 5432
    database = parsed_url.path.lstrip("/")

    # Reconstruct URL with SSL parameters
    query_params = urllib.parse.parse_qs(parsed_url.query)

    # Add sslmode if not present
    if "sslmode" not in query_params:
        query_params["sslmode"] = ["require"]

    # Encode password to handle special characters
    if password:
        password = urllib.parse.quote_plus(password)

    # Construct the final URL
    if password:
        connection_string = f"postgresql://{username}:{password}@{host}:{port}/{database}"
    else:
        connection_string = f"postgresql://{username}@{host}:{port}/{database}"

    # Append query parameters
    query_string = urllib.parse.urlencode(query_params, doseq=True)
    if query_string:
        connection_string += f"?{query_string}"

    return connection_string


SQLALCHEMY_DATABASE_URL = get_database_url()

# Simplified engine creation
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if is_testing else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Conditional table creation
def create_tables():
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Database connection error: {e}")
        raise


# Create tables in both testing and non-testing modes
create_tables()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
