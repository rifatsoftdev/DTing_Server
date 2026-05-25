from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.utils.helpers import utc6dhaka



class SettingsTable(Base):
    __tablename__ = "user_settings"

    user_id = Column(String, ForeignKey("user_list.user_id"), primary_key=True)

    # Settins
    allow_notifications = Column(Boolean, default=True)
    dark_mode = Column(Boolean, default=False)
    country = Column(String, default="BD")
    language = Column(String, default="en")

    biometric_enabled = Column(Boolean, nullable=False, default=False)
    biometric_secret = Column(String, nullable=True)

    # Account Deactived
    account_locked = Column(Boolean, default=False)
    
    updated_at = Column(DateTime(timezone=True), onupdate=utc6dhaka)
    created_at = Column(DateTime(timezone=True), default=utc6dhaka)

    user = relationship(
        "UserTable",
        back_populates="settings"
    )
    
