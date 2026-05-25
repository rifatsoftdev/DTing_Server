from sqlalchemy import Column, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.enums import KYCStatus
from app.utils.helpers import utc6dhaka



class KYCTable(Base):
    __tablename__ = "user_kyc"
    
    user_id = Column(
        String,
        ForeignKey("user_list.user_id"),
        primary_key=True,
        nullable=False,
        unique=True
    )

    document_type = Column(String, nullable=False)
    document_number = Column(String, nullable=True)
    front_image_url = Column(String, nullable=True)
    back_image_url = Column(String, nullable=True)
    user_face_image_url = Column(String, nullable=True)
    kyc_status = Column(Enum(KYCStatus), default=KYCStatus.PENDING)
    rejection_reason = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), default=utc6dhaka)
    updated_at = Column(DateTime(timezone=True), onupdate=utc6dhaka)

    # Relationship with UserTable for one-to-one mapping between user and kyc
    user = relationship(
        "UserTable",
        back_populates="user_kyc"
    )
