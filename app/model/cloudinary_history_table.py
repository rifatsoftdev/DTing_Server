from sqlalchemy import Column, String, DateTime, Integer

from app.core.database import Base
from app.utils.helpers import utc6dhaka


class CloudinaryHistory(Base):
    __tablename__ = "cloudinary_history"

    id = Column(Integer, primary_key=True, autoincrement=True)

    public_id = Column(String, nullable=False)
    secure_url = Column(String, nullable=False)
    file_type = Column(String, nullable=False, default="image")
    
    created_at = Column(DateTime(timezone=True), default=utc6dhaka)
    
