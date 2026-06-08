from sqlalchemy import Column, ForeignKey, String, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.enums.user_enum import Gender, UserType
from app.utils.helpers import utc6dhaka




class UserTable(Base):
    __tablename__ = "user_list"

    user_id = Column(String, primary_key=True, unique=True, index=True)

    full_name = Column(String(30), nullable=False)
    username = Column(String(30), unique=True, index=True, nullable=True)
    email_address = Column(String(255), unique=True, index=True, nullable=False)

    country_code = Column(
        String(4),
        ForeignKey("country_list.country_code"),
        nullable=True
    )
    
    phone_number = Column(String(14), unique=True, index=True, nullable=True)
    
    password_hash = Column(String, nullable=True)
    profile_image_url = Column(String, nullable=True)

    phone_verified = Column(Boolean, default=False)
    email_verified = Column(Boolean, default=False)
    link_google = Column(String, nullable=True)

    user_type = Column(Enum(UserType), default=UserType.NORMAL)
    user_gender = Column(Enum(Gender), default=Gender.UNDIFINED)
    date_of_birth = Column(DateTime(timezone=True), nullable=True)

    referral_account = Column(String, unique=False, nullable=True)

    last_active_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), default=utc6dhaka)
    updated_at = Column(DateTime(timezone=True), onupdate=utc6dhaka)

    # Country relationship for easy access to country information
    country = relationship(
        "CountryTable",
        back_populates="users"
    )
    
    # Settings relationship for one-to-one mapping between user and settings
    settings = relationship(
        "SettingsTable",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    feedbacks = relationship(
        "FeedbackTable",
        foreign_keys="FeedbackTable.user_id",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # Notifications relationship for one-to-many mapping between user and notifications
    notifications = relationship(
        "NotificationTable",
        foreign_keys="NotificationTable.target_id",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    sessions = relationship(
        "SessionTable",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    two_factor = relationship(
        "TwoFactorTable",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # KYC relationship for one-to-one mapping between user and kyc
    user_kyc = relationship(
        "KYCTable",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    # KYC relationship for one-to-one mapping between user and kyc
    user_services = relationship(
        "UserServicesTable",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # Activities relationship for one-to-many mapping between user and activity logs
    activities = relationship(
        "UserActivityTable",
        back_populates="user",
        cascade="all, delete-orphan"
    )


