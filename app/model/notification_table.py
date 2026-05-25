from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.enums import NotificationType, NotificationCreator
from app.utils.helpers import utc6dhaka



class NotificationTable(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    target_id = Column(String, ForeignKey("user_list.user_id"), nullable=True)

    type = Column(Enum(NotificationType), nullable=False)
    title = Column(String, nullable=False)
    body = Column(String, nullable=False)
    img_url = Column(String, nullable=True)

    meta_data = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), default=utc6dhaka)
    read_at = Column(DateTime(timezone=True), nullable=True)
    is_read = Column(Boolean, default=False)

    creator = Column(Enum(NotificationCreator), default=NotificationCreator.SYSTEM)
    
    user = relationship(
        "UserTable",
        foreign_keys=[target_id],
        back_populates="notifications"
    )
