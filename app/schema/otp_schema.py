from pydantic import BaseModel, Field
from app.enums import OTPMethod, OTPPurpose


class OTPRequest(BaseModel):
    otp_token: str = Field(min_length=32)

    method: OTPMethod
    purpose: OTPPurpose
    
    device_id: str
    device_uuid: str


class VerifyOTPRequest(BaseModel):
    otp_token: str = Field(min_length=32)

    otp: str = Field(min_length=4, max_length=10)

    method: OTPMethod
    purpose: OTPPurpose

    device_id: str
    device_uuid: str