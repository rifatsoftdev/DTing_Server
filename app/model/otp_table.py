from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.utils.helpers import utc6dhaka



class OTPTable(Base):
    __tablename__ = "otps"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=True)

    otp_token = Column(String, unique=True, index=True)
    device_id = Column(String, nullable=False)
    device_uuid = Column(String, nullable=False)

    delever_to = Column(String, nullable=True)

    otp_hash = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), default=utc6dhaka)
    expires_at = Column(DateTime(timezone=True), nullable=False)
