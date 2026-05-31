from pydantic import BaseModel
from typing import Optional



# Global request
class GlobalRequest(BaseModel):
    user_id: str
    access_token: str
    device_id: str
    device_uuid: str


# Global response
class GlobalResponse(BaseModel):
    status_code: Optional[int]
    success: bool
    action: Optional[str] = None
    message: str
    data: dict
    next_step: Optional[dict] = None
    pagination: Optional[dict] = None
