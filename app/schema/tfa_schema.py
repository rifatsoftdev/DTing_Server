from typing import Optional

from pydantic import BaseModel



# TOTP activation
class TOTPSetupRequest(BaseModel):
    user_id: str
    access_token: str
    device_id: str
    device_uuid: str


class TOTPConfirmRequest(BaseModel):
    user_id: str
    access_token: str
    device_id: str
    device_uuid: str
    totp_code: str


class TOTPAuthDisableRequest(BaseModel):
    user_id: str
    access_token: str
    device_id: str
    device_uuid: str
    user_password: str


class EmailTFASetupRequest(BaseModel):
    user_id: str
    access_token: str
    device_id: str
    device_uuid: str


class EmailTFAConfirmRequest(BaseModel):
    user_id: str
    access_token: str
    device_id: str
    device_uuid: str
    user_password: str
    otp: Optional[str] = None
    otp_token: Optional[str] = None


class EmailTFADisableRequest(BaseModel):
    user_id: str
    access_token: str
    device_id: str
    device_uuid: str
    user_password: str



class SMSTFASetupRequest(BaseModel):
    passuser_id: str
    access_token: str
    device_id: str
    device_uuid: str


class SMSTFAConfirmRequest(BaseModel):
    passuser_id: str
    access_token: str
    device_id: str
    device_uuid: str
    otp: str
    otp_token: str


class SMSTFADisableRequest(BaseModel):
    user_id: str
    access_token: str
    device_id: str
    device_uuid: str
    user_password: str
    