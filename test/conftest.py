import pytest
import sys
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app
from app.core.database import Base, get_db


# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Provide a test client with overridden database dependency."""
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def valid_registration_payload():
    """Valid user registration payload."""
    return {
        "full_name": "Test User",
        "email_address": "testuser@example.com",
        "phone_number": "1234567890",
        "country_code": "+1",
        "user_password": "SecurePass123!",
        "device_id": "device_123",
        "device_uuid": "uuid_123"
    }


@pytest.fixture
def valid_login_payload():
    """Valid user login payload."""
    return {
        "email_address": "testuser@example.com",
        "phone_number": "null",
        "country_code": "null",
        "user_password": "SecurePass123!",
        "device_id": "device_123",
        "device_uuid": "uuid_123"
    }
