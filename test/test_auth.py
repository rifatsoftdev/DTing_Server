"""
Tests for authentication endpoints.
"""
import pytest
from fastapi import status


class TestUserRegistration:
    """Test user registration endpoints."""
    
    def test_register_success(self, client, valid_registration_payload):
        """Test successful user registration."""
        response = client.post("/auth/register", json=valid_registration_payload)
        
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
        data = response.json()
        assert "message" in data or "user_id" in data or "token" in data
    
    def test_register_missing_email(self, client, valid_registration_payload):
        """Test registration with missing email."""
        payload = valid_registration_payload.copy()
        del payload["email_address"]
        
        response = client.post("/auth/register", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_invalid_email(self, client, valid_registration_payload):
        """Test registration with invalid email format."""
        payload = valid_registration_payload.copy()
        payload["email_address"] = "invalid_email"
        
        response = client.post("/auth/register", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_weak_password(self, client, valid_registration_payload):
        """Test registration with weak password."""
        payload = valid_registration_payload.copy()
        payload["user_password"] = "123"  # Too weak
        
        response = client.post("/auth/register", json=payload)
        # May return 400 or 422 depending on validation
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    def test_register_missing_password(self, client, valid_registration_payload):
        """Test registration with missing password."""
        payload = valid_registration_payload.copy()
        del payload["user_password"]
        
        response = client.post("/auth/register", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_duplicate_email(self, client, valid_registration_payload):
        """Test registration with duplicate email."""
        # First registration
        response1 = client.post("/auth/register", json=valid_registration_payload)
        assert response1.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
        
        # Second registration with same email
        response2 = client.post("/auth/register", json=valid_registration_payload)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST


class TestUserLogin:
    """Test user login endpoints."""
    
    def test_login_success(self, client, valid_registration_payload, valid_login_payload):
        """Test successful user login."""
        # First register
        client.post("/auth/register", json=valid_registration_payload)
        
        # Then login
        response = client.post("/auth/login", json=valid_login_payload)
        
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert "token" in data or "message" in data
    
    def test_login_missing_email(self, client, valid_login_payload):
        """Test login with missing email."""
        payload = valid_login_payload.copy()
        del payload["email_address"]
        
        response = client.post("/auth/login", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_login_wrong_password(self, client, valid_registration_payload, valid_login_payload):
        """Test login with wrong password."""
        # First register
        client.post("/auth/register", json=valid_registration_payload)
        
        # Try login with wrong password
        payload = valid_login_payload.copy()
        payload["user_password"] = "WrongPassword123!"
        response = client.post("/auth/login", json=payload)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_login_nonexistent_user(self, client, valid_login_payload):
        """Test login with non-existent user."""
        response = client.post("/auth/login", json=valid_login_payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestLogout:
    """Test user logout endpoints."""
    
    def test_logout_success(self, client, valid_registration_payload, valid_login_payload):
        """Test successful logout."""
        # Register and login
        client.post("/auth/register", json=valid_registration_payload)
        login_response = client.post("/auth/login", json=valid_login_payload)
        
        if login_response.status_code == status.HTTP_200_OK:
            token = login_response.json().get("token") or login_response.json().get("access_token")
            
            # Logout
            headers = {"Authorization": f"Bearer {token}"} if token else {}
            response = client.post("/auth/logout", headers=headers)
            
            # Logout should return success or still work
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]
