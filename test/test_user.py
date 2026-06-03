"""
Tests for user profile endpoints and operations.
"""
import pytest
from fastapi import status


class TestUserProfile:
    """Test user profile endpoints."""
    
    def test_get_profile_without_auth(self, client):
        """Test getting profile without authentication."""
        response = client.get("/me/profile")
        
        # Should require authentication
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    def test_update_profile_without_auth(self, client):
        """Test updating profile without authentication."""
        payload = {
            "full_name": "Updated Name",
            "bio": "Updated bio"
        }
        response = client.put("/me/profile", json=payload)
        
        # Should require authentication
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


class TestUserSettings:
    """Test user settings endpoints."""
    
    def test_get_settings_without_auth(self, client):
        """Test getting settings without authentication."""
        response = client.get("/me/settings")
        
        # Should require authentication or return default settings
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]
    
    def test_update_settings_without_auth(self, client):
        """Test updating settings without authentication."""
        payload = {
            "dark_mode": True,
            "email_notifications": False,
            "login_alerts": True,
            "show_phone": True
        }
        response = client.put("/me/settings", json=payload)
        
        # Should require authentication
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


class TestSessionManagement:
    """Test session management endpoints."""
    
    def test_get_sessions_without_auth(self, client):
        """Test getting sessions without authentication."""
        response = client.get("/session")
        
        # Should require authentication
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    def test_logout_session_without_auth(self, client):
        """Test logging out session without authentication."""
        payload = {"device_id": "test_device"}
        response = client.post("/session/logout", json=payload)
        
        # May allow logout without auth or require it
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST, 
                                       status.HTTP_401_UNAUTHORIZED]


class TestTwoFactorAuth:
    """Test two-factor authentication endpoints."""
    
    def test_enable_tfa_without_auth(self, client):
        """Test enabling 2FA without authentication."""
        response = client.post("/tfa/enable")
        
        # Should require authentication
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    def test_verify_tfa_invalid_code(self, client):
        """Test verifying 2FA with invalid code."""
        payload = {"totp_code": "000000"}
        response = client.post("/tfa/verify", json=payload)
        
        # Should fail with invalid code
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, 
                                       status.HTTP_401_UNAUTHORIZED]


class TestPasswordManagement:
    """Test password management endpoints."""
    
    def test_change_password_without_auth(self, client):
        """Test changing password without authentication."""
        payload = {
            "old_password": "OldPass123!",
            "new_password": "NewPass123!"
        }
        response = client.post("/auth/change-password", json=payload)
        
        # Should require authentication
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    def test_forget_password_invalid_email(self, client):
        """Test forget password with invalid email."""
        payload = {"email_address": "invalid_email"}
        response = client.post("/auth/forget-password", json=payload)
        
        # Should reject invalid email
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
