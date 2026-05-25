from sqlalchemy import JSON, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.utils.helpers import utc6dhaka



class OfferTable(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, autoincrement=True)

    image_url = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    target_user = Column(JSON, nullable=True)

    meta_data = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=utc6dhaka)
    expires_at = Column(DateTime(timezone=True), nullable=False)
