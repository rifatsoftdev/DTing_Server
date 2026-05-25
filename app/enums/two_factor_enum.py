from enum import Enum as PyEnum

class TwoFactorType(str, PyEnum):
    TOTP = "totp"
    EMAIL = "email"
    SMS = "sms"

