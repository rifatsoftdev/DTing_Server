from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from typing import Optional
from datetime import datetime


# Schemas for Google Login
class GoogleLoginRequest(BaseModel):
    token_id: str
    device_id: str
    device_uuid: str


class EmailVerificationRequest(BaseModel):
    email_verification_token: str
    

# Schemas for Login Request
class LoginRequest(BaseModel):
    email_address: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    country_code: Optional[str] = None
    user_password: str = Field(..., min_length=1)
    device_id: str
    device_uuid: str

    @field_validator("phone_number", "country_code", "user_password", "device_id", "device_uuid")
    @classmethod
    def optional_strings_must_not_be_blank(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value

        if not value.strip():
            raise ValueError("Field must not be blank")

        return value.strip()

    @model_validator(mode="after")
    def email_or_phone_required(self):
        if not self.email_address and not self.phone_number:
            raise ValueError("Email address or phone number is required")

        return self


# Schemas for Logout Request
class LogoutRequest(BaseModel):
    user_id: str
    access_token: str
    device_id: str
    device_uuid: str


# Schemas for Registration
class RegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=30)
    email_address: EmailStr
    phone_number: str
    country_code: str
    user_password: str = Field(..., min_length=8)
    date_of_birth: Optional[datetime] = None
    user_gender: Optional[str] = None

    device_id: str
    device_uuid: str

    @field_validator("full_name", "phone_number", "country_code", "device_id", "device_uuid", "user_password")
    @classmethod
    def required_string_must_not_be_blank(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Field must not be blank")
        return value.strip()

    @field_validator("user_gender")
    @classmethod
    def validate_user_gender(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value

        normalized_value = value.strip().lower()
        if normalized_value not in {"male", "female", "other", "undefined"}:
            raise ValueError("Invalid gender value")

        return normalized_value


# Schema for OTP Request
class NewUserEmailVerificationRequest(BaseModel):
    user_id: str
    otp: str
    email_verification_token: str
    device_id: str
    device_uuid: str


# Schema for get new access token
class AccessTokenRequest(BaseModel):
    refresh_token: str
    user_id: str
    device_id: str
    device_uuid: str
    

# Schema for FCM token recive
class FCMTokenRequest(BaseModel):
    user_id: str
    access_token: str
    device_id: str
    device_uuid: str
    fcm_token: str


# Schema for forget password
class ForgetPasswordRequest(BaseModel):
    email_address: EmailStr
    device_id: str
    device_uuid: str


# Schema for reset password
class ResetPasswordRequest(BaseModel):
    password_token: str
    new_password: str


# delete account request
class DeleteAccountRequest(BaseModel):
    user_id: str
    access_token: str
    device_id: str
    device_uuid: str
    user_password: str
    reason: str


# cancel delete account
class CancelDeleteAccountRequest(BaseModel):
    user_id: str
    access_token: str
    device_id: str
    device_uuid: str
    user_password: str


# Change Password
class ChangePasswordRequest(BaseModel):
    user_id: str
    access_token: str
    device_id: str
    device_uuid: str
    user_password: str
    new_password: str


# Logout all
class LogoutAllRequest(BaseModel):
    user_id: str
    access_token: str
    device_id: str
    device_uuid: str


# Link Google Account
class LinkGoogleAccountRequest(BaseModel):
    user_id: str
    access_token: str
    device_id: str
    device_uuid: str
    token_id: str


class SetUsernameRequest(BaseModel):
    user_id: str
    access_token: str
    device_id: str
    device_uuid: str
    username: str = Field(..., min_length=3, max_length=30)

    @field_validator("user_id", "access_token", "device_id", "device_uuid", "username")
    @classmethod
    def required_string_must_not_be_blank(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Field must not be blank")
        return value.strip()
