from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class OfferCreateRequest(BaseModel):
    image_url: str
    title: str
    description: str
    target_user: Optional[Dict[str, Any]] = None
    meta_data: Optional[Dict[str, Any]] = None
    expires_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OfferUpdateRequest(BaseModel):
    offer_id: int
    image_url: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    target_user: Optional[Dict[str, Any]] = None
    meta_data: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)