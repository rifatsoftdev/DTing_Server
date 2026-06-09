from sqlalchemy import Column, Integer, String, JSON, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base
# from app.model.user_table import UserTable
from app.utils.helpers import utc6dhaka




class SessionTable(Base):
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("user_list.user_id"), index=True, nullable=True)
    admin_id = Column(String, ForeignKey("admin_list.admin_id"), index=True, nullable=True)
    
    owner_type = Column(String, nullable=True, default="user")

    session_id = Column(String, unique=True, index=True)  # public session id

    access_token_hash = Column(String, nullable=True)
    refresh_token_hash = Column(String, nullable=True)
    fcm_token = Column(String, nullable=True)

    device_id = Column(String, nullable=True)
    device_uuid = Column(String, nullable=True)
    
    device_type = Column(String, nullable=True)  # android / web / ios
    device_name = Column(String, nullable=True)

    last_ip_address = Column(String, nullable=True)

    otp_verified = Column(Boolean, default=False)
    is_login = Column(Boolean, default=False)
    
    last_seen_at = Column(DateTime(timezone=True), default=utc6dhaka)
    
    login_at = Column(DateTime(timezone=True), default=utc6dhaka)
    logout_at = Column(DateTime(timezone=True), onupdate=utc6dhaka, nullable=True)

    user = relationship(
        "UserTable",
        back_populates="sessions"
    )

    admin = relationship(
        "AdminTable",
        back_populates="sessions",
        foreign_keys=[admin_id]
    )


