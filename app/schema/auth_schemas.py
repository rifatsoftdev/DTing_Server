from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# Schemas for Google Login
class GoogleLoginRequest(BaseModel):
    token_id: str
    device_id: str
    device_uuid: str

class FinalSetupRequest(BaseModel):
    token_id: str
    device_id: str
    device_uuid: str
    
    phone_number: Optional[str] = None
    country_code: Optional[str] = None
    user_gender: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    

# Schemas for Login Request
class LoginRequest(BaseModel):
    email_address: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    country_code: Optional[str] = None
    user_password: str
    device_id: str
    device_uuid: str


# Schemas for Logout Request
class LogoutRequest(BaseModel):
    user_id: str
    access_token: str
    device_id: str
    device_uuid: str


# Schemas for Registration
class RegisterRequest(BaseModel):
    full_name: str
    email_address: EmailStr
    phone_number: str
    country_code: str
    user_password: str
    referral_account: Optional[str] = None
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
