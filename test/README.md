# Authentication Server - Test Suite

This directory contains comprehensive pytest tests for the Authentication Server API.

## Test Structure

```
test/
├── __init__.py              # Test package initialization
├── conftest.py              # Pytest fixtures and configuration
├── test_auth.py             # Authentication endpoint tests
├── test_user.py             # User profile and settings tests
├── test_schemas.py          # Schema validation tests
├── test_api.py              # API health checks and basic tests
├── api.py                   # Legacy manual test file
└── demo.py                  # Legacy demo file
```

## Setup

### 1. Install Testing Dependencies

```bash
# Option 1: Install development requirements
pip install -r requirements-dev.txt

# Option 2: Install pytest and related tools manually
pip install pytest pytest-asyncio pytest-cov httpx
```

### 2. Verify Installation

```bash
pytest --version
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run with verbose output
```bash
pytest -v
```

### Run specific test file
```bash
pytest test/test_auth.py
```

### Run specific test class
```bash
pytest test/test_auth.py::TestUserRegistration
```

### Run specific test function
```bash
pytest test/test_auth.py::TestUserRegistration::test_register_success
```

### Run with coverage report
```bash
pytest --cov=app --cov-report=html --cov-report=term-missing
```

### Run tests matching a pattern
```bash
pytest -k "registration"
pytest -k "login and not logout"
```

### Run with markers
```bash
pytest -m auth
pytest -m "not slow"
```

### Run with timeout
```bash
pytest --timeout=300
```

## Test Categories

Tests are organized into the following categories:

- **test_auth.py**: Authentication tests (registration, login, logout)
- **test_user.py**: User profile, settings, sessions, and password management
- **test_schemas.py**: Schema validation and data validation tests
- **test_api.py**: General API health checks and response format tests

## Test Markers

Available test markers (use with `-m`):

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.auth` - Authentication tests
- `@pytest.mark.user` - User profile tests
- `@pytest.mark.api` - API endpoint tests
- `@pytest.mark.schema` - Schema validation tests
- `@pytest.mark.slow` - Slow running tests

## Fixtures

The `conftest.py` provides the following fixtures:

### `client`
- TestClient instance for making API requests
- Scope: function (fresh for each test)
- Includes database override for isolation

### `db`
- Fresh database instance for each test
- Automatically creates and cleans up tables

### `valid_registration_payload`
- Valid registration request data

### `valid_login_payload`
- Valid login request data

## Example Test Cases

### Basic Registration Test
```python
def test_register_success(self, client, valid_registration_payload):
    response = client.post("/auth/register", json=valid_registration_payload)
    assert response.status_code in [200, 201]
```

### Authentication Test
```python
def test_login_success(self, client, valid_registration_payload, valid_login_payload):
    # Register first
    client.post("/auth/register", json=valid_registration_payload)
    
    # Then login
    response = client.post("/auth/login", json=valid_login_payload)
    assert response.status_code == 200
```

### Schema Validation Test
```python
def test_register_schema_valid(self):
    data = {
        "full_name": "Test User",
        "email_address": "test@example.com",
        "phone_number": "1234567890",
        "country_code": "+1",
        "user_password": "SecurePass123!",
        "device_id": "device_123",
        "device_uuid": "uuid_123"
    }
    schema = RegisterSchema(**data)
    assert schema.email_address == "test@example.com"
```

## Configuration

Pytest configuration is defined in `pytest.ini`:

```ini
[pytest]
testpaths = test
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

## CI/CD Integration

To run tests in CI/CD pipelines:

```bash
# With coverage and XML output (for CI systems)
pytest --cov=app --cov-report=xml --cov-report=term-missing -v

# Generate JUnit XML report
pytest --junit-xml=test-results.xml -v
```

## Troubleshooting

### Import Errors
If you get import errors, ensure the project root is in PYTHONPATH:
```bash
export PYTHONPATH="${PYTHONPATH}:/home/rifatsoftdev/Projects/Authentication_Server"
pytest
```

### Database Errors
Tests use an in-memory SQLite database. If you see database errors:
1. Ensure SQLAlchemy models are properly imported
2. Check that `Base.metadata` is configured correctly
3. Verify `get_db` dependency is properly overridden

### Connection Issues
If tests fail with connection errors:
1. Ensure the app is not running on the same port
2. Tests use mock database, not production database
3. Check environment variables in `.env`

## Performance

Run slow tests separately:
```bash
# Skip slow tests
pytest -m "not slow"

# Only run slow tests
pytest -m slow
```

## Adding New Tests

1. Create test file with `test_` prefix: `test_new_feature.py`
2. Create test classes with `Test` prefix
3. Create test functions with `test_` prefix
4. Use fixtures from `conftest.py`
5. Add appropriate markers with `@pytest.mark.marker_name`

Example:
```python
import pytest
from fastapi import status

@pytest.mark.auth
class TestNewFeature:
    def test_new_feature(self, client):
        response = client.get("/new-endpoint")
        assert response.status_code == status.HTTP_200_OK
```

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/advanced/testing-dependencies/)
- [TestClient Documentation](https://starlette.io/testclient/)
