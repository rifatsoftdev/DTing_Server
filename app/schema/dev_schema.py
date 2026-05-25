from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from typing import Optional




# Payment Request
class PaymentRequest(BaseModel):
    user_id: str
    api_key: str
    secret_key: str

    user_account: str
    amount: Decimal
    refarence: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)



# Devrloper connection
class DevConnection(BaseModel):
    user_id: str
    api_key: str
    secret_key: str

    model_config = ConfigDict(from_attributes=True)