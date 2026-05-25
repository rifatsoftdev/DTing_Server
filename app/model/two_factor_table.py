from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.utils.helpers import utc6dhaka
from app.enums import TwoFactorType



class TwoFactorTable(Base):
    __tablename__ = "two_factor_methods"

    user_id = Column(String, ForeignKey("user_list.user_id"), primary_key=True)

    is_primary = Column(Boolean, default=False)
    
    method_type = Column(Enum(TwoFactorType), primary_key=True, nullable=False)  # e.g., 'totp', 'email', 'sms'
    is_enabled = Column(Boolean, default=False)
    delivery_address = Column(String, nullable=True)
    secret_key = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=utc6dhaka)
    updated_at = Column(DateTime(timezone=True), onupdate=utc6dhaka)

    user = relationship(
        "UserTable",
        back_populates="two_factor"
    )
    
