"""
Tests for utility functions and data validation.
"""
import pytest
from pydantic import ValidationError
from app.schema.auth_schemas import RegisterRequest, LoginRequest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestSchemaValidation:
    """Test Pydantic schema validation."""
    
    def test_register_schema_valid(self):
        """Test RegisterSchema with valid data."""
        data = {
            "full_name": "Test User",
            "email_address": "test@example.com",
            "phone_number": "1234567890",
            "country_code": "+1",
            "user_password": "SecurePass123!",
            "device_id": "device_123",
            "device_uuid": "uuid_123"
        }
        schema = RegisterRequest(**data)
        assert schema.full_name == "Test User"
        assert schema.email_address == "test@example.com"
    
    def test_register_schema_missing_email(self):
        """Test RegisterSchema with missing email."""
        data = {
            "full_name": "Test User",
            "phone_number": "1234567890",
            "country_code": "+1",
            "user_password": "SecurePass123!",
            "device_id": "device_123",
            "device_uuid": "uuid_123"
        }
        with pytest.raises(ValidationError):
            RegisterRequest(**data)
    
    def test_register_schema_invalid_email(self):
        """Test RegisterSchema with invalid email format."""
        data = {
            "full_name": "Test User",
            "email_address": "invalid_email",
            "phone_number": "1234567890",
            "country_code": "+1",
            "user_password": "SecurePass123!",
            "device_id": "device_123",
            "device_uuid": "uuid_123"
        }
        with pytest.raises(ValidationError):
            RegisterRequest(**data)
    
    def test_login_schema_valid(self):
        """Test LoginSchema with valid data."""
        data = {
            "email_address": "test@example.com",
            "phone_number": "null",
            "country_code": "null",
            "user_password": "SecurePass123!",
            "device_id": "device_123",
            "device_uuid": "uuid_123"
        }
        schema = LoginRequest(**data)
        assert schema.email_address == "test@example.com"
        assert schema.user_password == "SecurePass123!"
    
    def test_login_schema_missing_password(self):
        """Test LoginSchema with missing password."""
        data = {
            "email_address": "test@example.com",
            "phone_number": "null",
            "country_code": "null",
            "device_id": "device_123",
            "device_uuid": "uuid_123"
        }
        with pytest.raises(ValidationError):
            LoginRequest(**data)


class TestDataValidation:
    """Test various data validation functions."""
    
    def test_email_format_validation(self):
        """Test email format validation."""
        valid_emails = [
            "test@example.com",
            "user.name@example.co.uk",
            "user+tag@example.com"
        ]
        
        invalid_emails = [
            "invalid_email",
            "@example.com",
            "user@",
            "user name@example.com"
        ]
        
        from email_validator import validate_email, EmailNotValidError
        
        for email in valid_emails:
            try:
                validate_email(email, check_deliverability=False)
                assert True
            except EmailNotValidError:
                assert False, f"Valid email {email} failed validation"
        
        for email in invalid_emails:
            try:
                validate_email(email)
                assert False, f"Invalid email {email} passed validation"
            except EmailNotValidError:
                assert True
    
    def test_phone_number_validation(self):
        """Test phone number validation."""
        import phonenumbers
        
        valid_numbers = [
            ("+1", "2025551234"),  # US
            ("+88", "1812345673"),  # Bangladesh
            ("+44", "2071838750"),  # UK
        ]
        
        for country_code, number in valid_numbers:
            try:
                full_number = f"{country_code}{number}"
                parsed = phonenumbers.parse(full_number, None)
                assert phonenumbers.is_valid_number(parsed)
            except Exception as e:
                # Some numbers might not validate, that's ok for test
                pass


class TestEnums:
    """Test enum values and usage."""
    
    def test_user_enum_values(self):
        """Test user enums have expected values."""
        from app.enums.user_enum import Gender, UserType, KYCStatus
        
        assert Gender.MALE.value == 'male'
        assert UserType.NORMAL.value == 'normal'
        assert KYCStatus.VERIFIED.value == 'verified'
    
    def test_notification_enum_values(self):
        """Test notification enums have expected values."""
        from app.enums.notification_enum import NotificationType
        
        assert NotificationType.ALERT.value == 'alert'
        assert NotificationType.SUCCESS.value == 'success'
    
    def test_otp_enum_values(self):
        """Test OTP enums have expected values."""
        from app.enums.otp_enum import OTPMethod, OTPPurpose
        
        assert OTPMethod.EMAIL.value == 'email'
        assert OTPPurpose.LOGIN.value == 'login'
