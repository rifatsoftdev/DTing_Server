from sqlalchemy import Column, String, JSON, DateTime

from app.core.database import Base
from app.utils.helpers import utc6dhaka


class AppConfigTable(Base):
    __tablename__ = "app_configurations"

    key = Column(String, primary_key=True)

    value = Column(JSON, nullable=False)

    created_at = Column(DateTime(timezone=True), default=utc6dhaka)
    updated_at = Column(DateTime(timezone=True), onupdate=utc6dhaka)