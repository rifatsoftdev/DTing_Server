from datetime import timedelta

from fastapi import BackgroundTasks, HTTPException, Request, status, Header
from sqlalchemy.orm import Session

from app.constants import AnsiColor, String, ENV
from app.enums import NotificationType
from app.model import DeletedUserTable, NotificationTable, SessionTable, SettingsTable, TwoFactorTable, UserTable
from app.schema import (
    GlobalResponse, CancelDeleteAccountRequest, DeleteAccountRequest, LoginRequest,
    LogoutRequest, LogoutAllRequest, FCMTokenRequest, AccessTokenRequest
)
from app.utils import Hashing, Helpers

from services.auth.user_verification import UserVerificationService
from services.auth.otp_service import OTPService

from services.auth.user_repository import UserRepository
from services.auth.token_service import TokenGenerators
from services.auth.signup_service import RegistrationService

from services.notification.noticication_services import NotificationServices, NotificationData



class SigninService:
    def __init__(
        self,
        db: Session,
        background_tasks: BackgroundTasks,
        request: Request,
        authorization: str = Header(None)
    ):
        self.db = db
        self.background_tasks = background_tasks
        self.request = request
        self.authorization = authorization






# ==============================================================================
# ==============================================================================
