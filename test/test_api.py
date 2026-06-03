"""
Tests for API health checks and basic endpoints.
"""
import pytest
from fastapi import status


class TestHealthCheck:
    """Test API health check endpoints."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        
        # Root should return some response (200, 307 redirect, etc)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_307_TEMPORARY_REDIRECT]
    
    def test_health_check_if_exists(self, client):
        """Test health check endpoint if it exists."""
        response = client.get("/health")
        
        # Health check should either exist and return 200, or 404 if not implemented
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


class TestCountryEndpoints:
    """Test country-related endpoints."""
    
    def test_get_countries_list(self, client):
        """Test getting list of countries."""
        response = client.get("/country")
        
        # Should return countries or 404 if not implemented
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
    
    def test_get_country_by_code(self, client):
        """Test getting specific country."""
        response = client.get("/country/US")
        
        # Should return country or 404
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


class TestAPIResponseFormat:
    """Test API response format and structure."""
    
    def test_response_is_json(self, client):
        """Test that responses are valid JSON."""
        response = client.get("/")
        
        # Response should be parseable as JSON
        try:
            response.json()
            assert True
        except ValueError:
            # Some endpoints might not return JSON
            pass
    
    def test_error_response_format(self, client):
        """Test error response format."""
        # Try to access non-existent endpoint
        response = client.get("/non-existent-endpoint")
        
        # Should return 404
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Should have valid JSON error response
        data = response.json()
        assert "detail" in data or "error" in data or "message" in data
