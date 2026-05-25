from enum import Enum as PyEnum


# User Gender
class Gender(str, PyEnum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNDIFINED = "undefined"


# Uaer type
class UserType(str, PyEnum):
    NORMAL = "normal"
    AGENT = "agent"


class KYCStatus(str, PyEnum):
    VERIFIED = "verified"
    PENDING = "pending"
    REJECTED = "rejected"
    FAILED = "failed"
    DISABLED = "disable"
    REQUIRED = "required"