from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.utils.helpers import utc6dhaka



class SettingsTable(Base):
    __tablename__ = "user_settings"

    user_id = Column(String, ForeignKey("user_list.user_id"), primary_key=True)

    # Settins
    dark_mode = Column(Boolean, default=False)
    language = Column(String, default="en")

    # Notification preferences
    email_notifications = Column(Boolean, default=True)
    sms_notifications = Column(Boolean, default=False)
    push_notifications = Column(Boolean, default=True)
    marketing_notifications = Column(Boolean, default=False)

    # Security preferences
    login_alerts = Column(Boolean, default=True)
    new_device_alerts = Column(Boolean, default=True)
    password_change_alerts = Column(Boolean, default=True)

    # Privacy
    profile_visibility = Column(String, default="private")  # public/private
    show_email = Column(Boolean, default=False)
    show_phone = Column(Boolean, default=False)

    # Localization / UI
    timezone = Column(String, default="Asia/Dhaka")
    currency = Column(String, default="BDT")
    date_format = Column(String, default="YYYY-MM-DD")

    # Account state
    account_deactivated = Column(Boolean, default=False)
    deactivated_at = Column(DateTime(timezone=True), nullable=True)

    # Security timestamps
    last_password_changed_at = Column(DateTime(timezone=True), nullable=True)
    biometric_enabled_at = Column(DateTime(timezone=True), nullable=True)

    biometric_enabled = Column(Boolean, nullable=False, default=False)
    biometric_secret = Column(String, nullable=True)
    
    updated_at = Column(DateTime(timezone=True), onupdate=utc6dhaka)
    created_at = Column(DateTime(timezone=True), default=utc6dhaka)

    user = relationship(
        "UserTable",
        back_populates="settings"
    )
    
