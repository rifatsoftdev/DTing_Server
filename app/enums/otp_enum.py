from enum import Enum


class OTPMethod(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    TOTP = "totp"


class OTPPurpose(str, Enum):
    LOGIN = "login"
    CHANGE_EMAIL = "change_email"
    CHANGE_PASSWORD = "change_password"
    DELETE_ACCOUNT = "delete_account"