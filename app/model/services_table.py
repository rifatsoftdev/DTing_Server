from sqlalchemy import Column, Integer, String, JSON, DateTime, Boolean, ForeignKey, Enum, Numeric
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.enums import ActivityStatus
from app.utils.helpers import utc6dhaka





class ServicesTable(Base):
    __tablename__ = "available_services"

    id = Column(Integer, primary_key=True, index=True)

    service_name = Column(String, nullable=False)
    service_slug = Column(String, nullable=False)
    
    service_details = Column(JSON, nullable=True)

    status = Column(Enum(ActivityStatus), default=ActivityStatus.ACTIVE, nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=utc6dhaka)
    updated_at = Column(DateTime(timezone=True), onupdate=utc6dhaka)
