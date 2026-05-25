from sqlalchemy import Column, Integer, String, DateTime, Boolean

from app.core.database import Base
from app.utils.helpers import utc6dhaka



class ResetPasswordTable(Base):
    __tablename__ = "password_reset"

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, nullable=False)
    password_token = Column(String, nullable=False)
    device_id = Column(String, nullable=True)
    device_uuid = Column(String, nullable=True)
    is_used = Column(Boolean, nullable=False, default=False)
    
    created_at = Column(DateTime, default=utc6dhaka)
    expires_at = Column(DateTime, nullable=False)