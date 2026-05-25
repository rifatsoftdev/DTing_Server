from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.utils.helpers import utc6dhaka


class DeletedUserTable(Base):
    __tablename__ = "deleted_user"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    # Reference to original user (kept for audit)
    user_id = Column(
        String,
        ForeignKey("user_list.user_id"),
        index=True
    )

    # Snapshot of key user data at delete-request time
    full_name = Column(String(30), nullable=False)
    email_address = Column(String(30), index=True, nullable=False)
    country_code = Column(String(4), nullable=True)
    phone_number = Column(String(14), index=True, nullable=True)

    reason = Column(String, nullable=True)

    # Soft-delete workflow flags
    requested_at = Column(DateTime(timezone=True), default=utc6dhaka)
    scheduled_delete_at = Column(DateTime(timezone=True), nullable=True)
    is_processed = Column(Boolean, default=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), default=utc6dhaka)
    updated_at = Column(DateTime(timezone=True), onupdate=utc6dhaka)

    # Optional relationship if you want backrefs later
    user = relationship("UserTable", backref="delete_requests")
