from pydantic import BaseModel
from typing import Optional
from decimal import Decimal



# Schema for QR request
class QRRequest(BaseModel):
    qr_type: str
    full_name: Optional[str] = None
    phone_number: str
    email_address: Optional[str] = None
    amount: Optional[Decimal] = None
    currency: Optional[str] = None
