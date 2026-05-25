from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime, JSON, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.enums import ActivityStatus
from app.utils.helpers import utc6dhaka



class CountryTable(Base):
    __tablename__ = "country_list"

    id = Column(Integer, autoincrement=True, index=True)
    
    country_id = Column(
        String,
        primary_key=True,
        nullable=False,
        unique=True
    )

    country_name = Column(
        String,
        unique=True,
        nullable=False
    )

    # foreign key to user table for country code relationship
    country_code = Column(
        String(4),
        unique=True,
        nullable=False
    )
    country_iso = Column(String(3), unique=True, nullable=False)
    
    flag_emoji = Column(String, nullable=False)

    currency = Column(String, nullable=False)

    currency_symbol = Column(String, nullable=False)
    status = Column(Enum(ActivityStatus), nullable=False, default=ActivityStatus.PENDING)

    meta_data = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), default=utc6dhaka)
    updated_at = Column(DateTime(timezone=True), onupdate=utc6dhaka)

    # Relationship with UserTable
    users = relationship(
        "UserTable",
        back_populates="country"
    )
