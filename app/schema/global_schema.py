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
    success: bool
    message: str
    data: dict
    pagination: Optional[dict] = None
