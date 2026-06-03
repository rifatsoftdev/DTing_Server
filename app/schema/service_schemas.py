from pydantic import BaseModel, Field
from typing import Any, Dict, Optional


class ServiceAddRequest(BaseModel):
    service_slug: str = Field(..., min_length=1)
    service_name: Optional[str] = None
    service_details: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class ServiceUpdateRequest(BaseModel):
    service_slug: str = Field(..., min_length=1)
    service_name: Optional[str] = None
    service_details: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class ServiceDeleteRequest(BaseModel):
    service_slug: str = Field(..., min_length=1)
