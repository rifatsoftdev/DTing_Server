from pydantic import BaseModel
from typing import Optional


# 
class KYCUpdateRequest(BaseModel):
    user_id: str
    kyc_status: str
    rejection_reason: Optional[str] = None


# 
class KYCRequest(BaseModel):
    user_id: str
    access_token: str
    device_id: str
    device_uuid: str

    document_type: str