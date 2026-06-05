from enum import Enum as PyEnum


class UserActivityType(str, PyEnum):
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET = "password_reset"
    API_KEY_CREATE = "api_key_create"
    API_KEY_DELETE = "api_key_delete"
    API_KEY_RENAME = "api_key_rename"
    PROFILE_UPDATE = "profile_update"
    NAME_CHANGE = "name_change"
    SETTINGS_CHANGE = "settings_change"
    LOGIN = "login"
    LOGOUT = "logout"
    OTHER = "other"


class ReadStatus(str, PyEnum):
    READ = "read"
    UNREAD = "unread"
    