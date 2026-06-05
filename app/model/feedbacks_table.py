from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    Text,
    Enum,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.enums import ReadStatus


class FeedbackTable(Base):
    __tablename__ = "feedbacks"

    id = Column(String(36), primary_key=True, index=True)

    user_id = Column(
        String(36),
        ForeignKey("user_list.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    rating = Column(Integer, nullable=True)  # 1-5

    subject = Column(String(255), nullable=True)

    message = Column(Text, nullable=False)

    app_version = Column(String(50), nullable=True)

    platform = Column(String(20), nullable=True)  # Android, iOS, Web

    device_info = Column(Text, nullable=True)

    status = Column(Enum(ReadStatus), default=ReadStatus.UNREAD)
    # open, in_review, resolved, closed

    admin_reply = Column(Text, nullable=True)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    user = relationship(
        "UserTable",
        back_populates="feedbacks"
    )