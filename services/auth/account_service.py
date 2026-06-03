from datetime import timedelta

from fastapi import BackgroundTasks, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.constants import AnsiColor, String, ENV
from app.enums import NotificationType
from app.model import DeletedUserTable, NotificationTable, SessionTable, SettingsTable, TwoFactorTable, UserTable
from app.schema import (
    GlobalResponse, CancelDeleteAccountRequest, DeleteAccountRequest, LoginRequest,
    FCMTokenRequest, AccessTokenRequest, SetUsernameRequest
)
from app.utils import Hashing, Helpers

from services.auth.user_verification import UserVerificationService
from services.auth.otp_service import OTPService

from services.auth.user_repository import UserRepository
from services.auth.token_service import TokenGenerators
from services.auth.signup_service import RegistrationService

from services.notification.notification_services import NotificationServices, NotificationData, NotificationEvent
from services.auth.signin_service import SigninService


class AccountServices(OTPService, SigninService):
    def __init__(
        self,
        db: Session,
        background_tasks: BackgroundTasks,
        request: Request,
        authorization: str
    ):
        OTPService.__init__(
            self,
            db=db,
            background_tasks=background_tasks,
            request=request,
            authorization=authorization
        )
        UserRepository.__init__(self, db)
        SigninService.__init__(
            self,
            db=db,
            background_tasks=background_tasks,
            request=request,
            authorization=authorization
        )

    @staticmethod
    def _mask_email(email_address: str | None) -> str | None:
        if not email_address or "@" not in email_address:
            return None

        local_part, domain = email_address.split("@", 1)
        if not local_part:
            return f"***@{domain}"

        visible_count = 2 if len(local_part) > 2 else 1
        return f"{local_part[:visible_count]}***@{domain}"

    @staticmethod
    def _mask_phone(phone_number: str | None) -> str | None:
        if not phone_number:
            return None

        if len(phone_number) <= 4:
            return "*" * len(phone_number)

        visible_prefix = min(4, len(phone_number) - 2)
        return f"{phone_number[:visible_prefix]}{'*' * (len(phone_number) - visible_prefix - 2)}{phone_number[-2:]}"

    def set_username(self, payload: SetUsernameRequest) -> GlobalResponse:
        try:
            user_id: str = payload.user_id
            access_token: str = payload.access_token
            android_id: str = payload.device_id
            android_uuid: str = payload.device_uuid
            username: str = payload.username.strip()

            user_verification_service = UserVerificationService(
                db=self.db,
                background_tasks=self.background_tasks,
                request=self.request,
                authorization=self.authorization
            )

            user = user_verification_service.verify_user(
                user_id=user_id,
                access_token=access_token,
                device_id=android_id,
                device_uuid=android_uuid
            )

            existing_username = self.db.query(UserTable).filter(
                UserTable.username == username,
                UserTable.user_id != user.user_id
            ).first()
            if existing_username:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Username already taken"
                )

            user.username = username
            self.db.commit()
            self.db.refresh(user)

            return GlobalResponse(
                status_code=status.HTTP_200_OK,
                success=True,
                action="set_username",
                message="Username set successfully",
                data={
                    "username": user.username
                },
                next_step={}
            )

        except HTTPException:
            raise

        except Exception as e:
            self.db.rollback()
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)

    def get_new_access_token(self, payload: AccessTokenRequest) -> GlobalResponse:
        try:
            # get data
            refresh_token = payload.refresh_token
            user_id = payload.user_id
            android_id = payload.device_id
            android_uuid = payload.device_uuid

            session = self.db.query(SessionTable).filter(
                SessionTable.device_id == android_id,
                SessionTable.device_uuid == android_uuid
            ).first()

            if (not session):
                raise HTTPException(status_code=404, detail=String.SESSION_NOT_FOUND)

            if (not session.is_login or not session.otp_verified):
                raise HTTPException(status_code=401, detail=String.USER_NOT_LOGIN)

            payload = self._decode_token(refresh_token)

            # check token if expired payload is Null
            if payload == None:
                raise HTTPException(
                    status_code=401,
                    detail="Refresh token expired"
                )
            
            # check token type
            if payload.get("type") != "refresh":
                raise HTTPException(status_code=401, detail="Invalid token")

            access_token = self._create_token(
                expire_min=ENV.ACCESS_EXPIRE,
                data={
                    "user_id": payload.get("user_id"),
                    "email_address": payload.get("email_address"),
                    "android_id": payload.get("android_id"),
                    "android_uuid": payload.get("android_uuid")
                }
            )

            # update session
            session = self.db.query(SessionTable).filter(SessionTable.user_id == payload.get("user_id")).first()

            if session:
                session.access_token_hash = Hashing.create_hash(access_token)
                self.db.commit()
                self.db.refresh(session)

            print(payload.get("user_id"))
            print(f"Refreshed access token: {access_token}")

            return GlobalResponse(
                status_code=status.HTTP_200_OK,
                success=True,
                action="refresh_access_token",
                message="Access token refreshed successfully",
                data={
                    "access_token": access_token
                },
                next_step={}
            )

        except HTTPException:
            raise

        except Exception as e:
            self.db.rollback()
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)
    
    def receive_fcm_token(self, payload: FCMTokenRequest) -> GlobalResponse:
        try:
            # print(f"FCM token received: {request}")

            # get data
            user_id: str = payload.user_id
            access_token: str = payload.access_token
            android_id: str = payload.device_id
            android_uuid: str = payload.device_uuid
            fcm_token: str = payload.fcm_token
            
            # verify user
            user_verification_service = UserVerificationService(
                db=self.db,
                background_tasks=self.background_tasks,
                request=self.request,
                authorization=self.authorization
            )

            user = user_verification_service.verify_user(
                user_id=user_id,
                access_token=access_token,
                device_id=android_id,
                device_uuid=android_uuid
            )

            # find db
            existing = self.db.query(SessionTable).filter(
                SessionTable.user_id==user_id,
                SessionTable.device_id==android_id,
                SessionTable.device_uuid==android_uuid,
                SessionTable.is_login==True
            ).first()
            
            if existing:
                existing.fcm_token = fcm_token
                self.db.commit()
                self.db.refresh(existing)
            else:
                session = SessionTable(
                    user_id=user_id,
                    fcm_token=fcm_token
                )
                self.db.add(session)
                self.db.commit()
                self.db.refresh(session)
            
            return GlobalResponse(
                status_code=status.HTTP_200_OK,
                success=True,
                action="receive_fcm_token",
                message="FCM token received successfully",
                data={},
                next_step={}
            )
        
        except HTTPException:
            raise

        except Exception as e:
            self.db.rollback()
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)

    def delete_account(self, payload: DeleteAccountRequest):
        try:
            user_id: str = payload.user_id
            access_token: str = payload.access_token
            android_id: str = payload.device_id
            android_uuid: str = payload.device_uuid
            user_password: str = payload.user_password
            reason: str = payload.reason

            # Request info
            ip: str = self.request.client.host

            user_verification_service = UserVerificationService(self.db)

            user = user_verification_service.verify_user(
                user_id=user_id,
                access_token=access_token,
                android_id=android_id,
                android_uuid=android_uuid
            )

            # check existing delete request
            existing_request = self.db.query(DeletedUserTable).filter(
                DeletedUserTable.user_id == user.user_id,
                DeletedUserTable.is_processed == False
            ).first()

            if existing_request:
                raise HTTPException(
                    status_code=status.status.HTTP_409_CONFLICT,
                    detail="Delete request already submitted"
                )

            # schedule deletion (not immediate)
            scheduled_delete_at = Helpers.utc6dhaka() + timedelta(days=7)

            delete_record = DeletedUserTable(
                user_id=user.user_id,
                full_name=user.full_name,
                email_address=user.email_address,
                country_code=user.country_code,
                phone_number=user.phone_number,
                reason=reason,
                requested_at=Helpers.utc6dhaka(),
                scheduled_delete_at=scheduled_delete_at,
                is_processed=False
            )
            self.db.add(delete_record)

            # lock account to prevent further activity
            settings = self.db.query(SettingsTable).filter(
                SettingsTable.user_id == user.user_id
            ).first()

            if settings:
                settings.account_deactivated = True

            # logout all sessions
            sessions = self.db.query(SessionTable).filter(
                SessionTable.user_id == user.user_id,
                SessionTable.is_login == True
            ).all()
            
            for session in sessions:
                session.is_login = False
                session.access_token_hash = None
                session.refresh_token_hash = None
                session.fcm_token = None
                session.logout_at = Helpers.utc6dhaka()

            # user Notification
            new_notification = NotificationTable(
                target_id=user.user_id,
                type=NotificationType.ALERT,
                title="Delete Account Requested",
                body=f"We received a delete account request from IP {ip}. Your account will be removed after review."
            )
            self.db.add(new_notification)

            # real time notification
            notificationServices = NotificationServices(
                db=self.db,
                background_tasks=self.background_tasks
            )

            notificationServices.send_notification(
                data=NotificationData(
                    target_id=user.user_id,
                    type=NotificationType.ALERT,
                    title="Delete Account Requested",
                    template="admin.custom",
                    context={
                        "body": f"We received a delete account request from IP {ip}. Your account will be removed after review.",
                    },
                    push=True,
                    email=True,
                    sms=False
                )
            )

            self.db.commit()
            self.db.refresh(delete_record)
            self.db.refresh(new_notification)

            return GlobalResponse(
                status_code=status.HTTP_200_OK,
                success=True,
                action="delete_account_requested",
                message="Delete request submitted successfully",
                data={
                    "scheduled_delete_at": scheduled_delete_at
                },
                next_step={}
            )

        except HTTPException:
            raise

        except Exception as e:
            self.db.rollback()
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)

    def cancel_delete_account(self, payload: CancelDeleteAccountRequest) -> GlobalResponse:
        try:
            user_id: str = payload.user_id
            access_token: str = payload.access_token
            android_id: str = payload.device_id
            android_uuid: str = payload.device_uuid
            user_password: str = payload.user_password

            user_verification_service = UserVerificationService(self.db)

            user = user_verification_service.verify_user(
                user_id=user_id,
                access_token=access_token,
                android_id=android_id,
                android_uuid=android_uuid
            )

            delete_request = self.db.query(DeletedUserTable).filter(
                DeletedUserTable.user_id == user_id,
                DeletedUserTable.is_processed == False
            ).first()

            if not delete_request:
                raise HTTPException(
                    status_code=404,
                    detail="Delete request not found"
                )

            self.db.delete(delete_request)

            settings = self.db.query(SettingsTable).filter(
                SettingsTable.user_id == user_id
            ).first()

            if settings:
                settings.account_deactivated = False

            self.db.commit()

            return GlobalResponse(
                status_code=status.HTTP_200_OK,
                success=True,
                action="cancel_delete_account",
                message="Delete request cancelled successfully",
                data={},
                next_step={}
            )

        except HTTPException:
            raise

        except Exception as e:
            self.db.rollback()
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)








# ==============================================================================
# ==============================================================================
