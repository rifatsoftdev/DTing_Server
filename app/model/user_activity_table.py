from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.enums.activity_enum import UserActivityType
from app.utils.helpers import utc6dhaka


class UserActivityTable(Base):
    __tablename__ = "user_activity"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("user_list.user_id"), index=True, nullable=False)

    activity_type = Column(Enum(UserActivityType), nullable=False)
    detail = Column(JSON, nullable=True)

    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), default=utc6dhaka)

    user = relationship(
        "UserTable",
        back_populates="activities"
    )
