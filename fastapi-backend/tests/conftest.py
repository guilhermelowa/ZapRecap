import os
import pytest
from dotenv import load_dotenv

# Load test-specific environment variables
load_dotenv(dotenv_path=".env.test", override=True)

# Set testing environment before importing database
os.environ["TESTING"] = "True"
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "test-openai-key")
os.environ["SECRET_KEY"] = os.getenv("SECRET_KEY", "test-secret-key")

# Set additional required environment variables for testing
os.environ["ADMIN_REGISTRATION_TOKEN"] = os.getenv(
    "ADMIN_REGISTRATION_TOKEN", "test_admin_registration_token"
)
os.environ["MERCADOPAGO_ACCESS_TOKEN"] = os.getenv(
    "MERCADOPAGO_ACCESS_TOKEN", "test_mercadopago_access_token"
)
os.environ["PAYER_EMAIL"] = os.getenv("PAYER_EMAIL", "test_payer@example.com")
os.environ["PAYER_FIRST_NAME"] = os.getenv("PAYER_FIRST_NAME", "Test")
os.environ["PAYER_LAST_NAME"] = os.getenv("PAYER_LAST_NAME", "User")
os.environ["PAYER_ID_TYPE"] = os.getenv("PAYER_ID_TYPE", "CPF")
os.environ["PAYER_ID_NUMBER"] = os.getenv("PAYER_ID_NUMBER", "12345678900")
os.environ["PAYER_ADDRESS"] = os.getenv(
    "PAYER_ADDRESS",
    '{"street": "Test Street", "number": "123", "city": "Test City",\
    "state": "TS", "zip_code": "12345"}',
)


@pytest.fixture(scope="session")
def setup_test_database():
    # Use SQLite for testing
    from app.database import engine
    from app.models.database_models import Base
    from app.auth.models import Admin  # noqa F401

    # Create all tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop all tables after tests
    Base.metadata.drop_all(bind=engine)
