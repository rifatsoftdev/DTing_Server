from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Integer
from sqlalchemy.orm import relationship
from datetime import timedelta

from app.core.database import Base
from app.utils.helpers import utc6dhaka


class DevTable(Base):
    __tablename__ = "developer_list"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Reference to original user (kept for audit)
    user_id = Column(String, ForeignKey("user_list.user_id"), index=True)

    api_key = Column(String, unique=True, index=True, nullable=False)
    secret_key = Column(String, unique=True, index=True, nullable=False)
    status = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), default=utc6dhaka)
    expair_at = Column(DateTime(timezone=True), default=lambda: utc6dhaka() + timedelta(days=90))

    # Optional relationship if you want backrefs later
    user = relationship("UserTable", backref="dev_requests")
