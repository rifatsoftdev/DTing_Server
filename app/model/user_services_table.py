from sqlalchemy import Column, Integer, String, JSON, DateTime, Boolean, ForeignKey, Enum, Numeric
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.enums import BillCategory, ActivityStatus
from app.utils.helpers import utc6dhaka





class UserServicesTable(Base):
    __tablename__ = "user_services"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(String, ForeignKey("user_list.user_id"), index=True, nullable=False)
    
    service_name = Column(String, nullable=False)
    service_slug = Column(String, nullable=False)
    
    service_category = Column(Enum(BillCategory), nullable=False)
    service_details = Column(JSON, nullable=True)

    status = Column(Enum(ActivityStatus), default=ActivityStatus.PENDING, nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=utc6dhaka)
    updated_at = Column(DateTime(timezone=True), onupdate=utc6dhaka)

    user = relationship(
        "UserTable",
        back_populates="user_services"
    )
