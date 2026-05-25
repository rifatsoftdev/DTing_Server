from pydantic import BaseModel
from datetime import datetime


# Schema for transaction history response
class TransactionResponse(BaseModel):
    id: str
    user_id: str
    sender_id: str
    receiver_id: str
    amount: float
    type: str
    status: str
    payment_method: str
    timestamp: datetime