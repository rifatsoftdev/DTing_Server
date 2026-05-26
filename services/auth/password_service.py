from fastapi import HTTPException, Request, BackgroundTasks
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from app.constants import String, AnsiColor, ENV
from app.enums import NotificationType
from app.schema import ForgetPasswordRequest, GlobalResponse, ResetPasswordRequest, ChangePasswordRequest
from app.model import UserTable, ResetPasswordTable, NotificationTable

from services.auth.token_service import TokenGenerators
from app.utils import Hashing

from services.auth.user_verification import UserVerificationService
from services.notification.noticication_services import NotificationServices, NotificationData


templates = Jinja2Templates(directory="templates")


class PasswordService(TokenGenerators):
    def __init__(
        self,
        db: Session,
        background_tasks: BackgroundTasks,
        request: Request,
        authorization: str
    ):
        super().__init__(db)
        self.db = db
        self.background_tasks = background_tasks
        self.request = request
        self.authorization = authorization

    def reset_password(self, payload: ForgetPasswordRequest):
        try:
            # print(f"Forget password attempt: {request}")

            # request data
            email_address: str= payload.email_address
            android_id: str = payload.device_id
            android_uuid: str = payload.device_uuid
            
            # Request info
            ip: str = self.request.client.host
            user_agent: str = self.request.headers.get("user-agent")
            auth: str = self.request.headers.get("authorization"),
            path: str = self.request.url.path,
            query: dict = dict(self.request.query_params),
            cookies: dict = self.request.cookies


            # find user
            user = self.db.query(UserTable).filter(UserTable.email_address == email_address).first()
            if not user:
                raise HTTPException(status_code=404, detail=String.USER_NOT_FOUND)

            # generate token
            otp_token = self._create_token(
                token_type="otp",
                expire_min=ENV.PASS_RST_TOKEN_EXPIRE_MIN,
                data={
                    "user_id": user.user_id,
                    "email_address": user.email_address,
                    "device_id": android_id,
                    "device_uuid": android_uuid
                }
            )

            # check old password reset
            rst_password = self.db.query(ResetPasswordTable).filter(
                ResetPasswordTable.user_email == user.email_address,
                ResetPasswordTable.expires_at > datetime.now(timezone.utc),
                ResetPasswordTable.is_used == False
            ).first()
            if rst_password:
                raise HTTPException(status_code=409, detail=String.PASSWORD_RESET_ALREADY_SENT)
            
            else:
                rst_password = ResetPasswordTable(
                    user_email=email_address,
                    password_token=otp_token,
                    device_id=android_id,
                    device_uuid=android_uuid,
                    is_used=False,
                    expires_at=datetime.now(timezone.utc) + timedelta(minutes=15)
                )
                self.db.add(rst_password)
                self.db.flush()
            
            # send email
            notificationServices = NotificationServices(
                db=self.db,
                background_tasks=self.background_tasks
            )
            notificationServices.send_notification(
                data=NotificationData(
                    user_id=user.user_id,
                    template="auth.password.reset.request",
                    context={
                        "ip": ip,
                        "name": user.full_name,
                        "email": user.email_address,
                        "reset_link": otp_token,
                    },
                    noty_type=NotificationType.ALERT,
                    push=False,
                    sms=False,
                    email=True
                )
            )
            
            # user Notification
            new_notification = NotificationTable(
                target_id=user.user_id,
                type=NotificationType.ALERT,
                title="Reset Password Request Detected",
                body=f"We have received a password reset request for your account from {ip} IP address. Make sure you have your email address with you."
            )
            self.db.add(new_notification)
            self.db.flush()

            # real time notification
            notificationServices = NotificationServices(
                db=self.db,
                background_tasks=self.background_tasks
            )

            notificationServices.send_notification(
                data=NotificationData(
                    user_id=user.user_id,
                    template="auth.password.reset.request",
                    context={
                        "ip": ip,
                        "name": user.full_name,
                        "email": user.email_address,
                        "reset_link": otp_token,
                    },
                    noty_type=NotificationType.ALERT,
                    push=True,
                    sms=False,
                    email=False
                )
            )

            # db commit and refresh
            self.db.commit()
            self.db.refresh(rst_password)
            self.db.refresh(new_notification)

            return GlobalResponse(
                success=True,
                message="Password reset link sent successfully",
                data={}
            )

        except HTTPException:
            raise

        except Exception as e:
            self.db.rollback()
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)

    def reset_password_page(self, password_token: str):
        try:
            payload = self._decode_token(password_token)

            if not payload:
                return templates.TemplateResponse("expired.html", {"request": self.request})

            user = self.db.query(UserTable).filter(UserTable.user_id == payload["user_id"]).first()
            if not user:
                return templates.TemplateResponse("expired.html", {"request": self.request})

            rst_password = self.db.query(ResetPasswordTable).filter(
                ResetPasswordTable.user_email == user.email_address,
                ResetPasswordTable.is_used == False,
                ResetPasswordTable.expires_at > datetime.now(timezone.utc)
            ).first()

            if not rst_password:
                return templates.TemplateResponse("expired.html", {"request": self.request})

            return templates.TemplateResponse("reset_password.html", {
                "request": self.request,
                "password_token": password_token
            })

        except HTTPException:
            raise

        except Exception as e:
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)

    def set_password(self, payload: ResetPasswordRequest):
        try:
            # print(f"Reset password attempt: {request}")
            reset_token = payload.password_token
            new_password = payload.new_password

            # Request info
            ip: str = self.request.client.host
            user_agent: str = self.request.headers.get("user-agent")
            auth: str = self.request.headers.get("authorization"),
            path: str = self.request.url.path,
            query: dict = dict(self.request.query_params),
            cookies: dict = self.request.cookies

            # check token
            payload = self._decode_token(reset_token)

            if not payload:
                raise HTTPException(status_code=400, detail=String.INVALID_OR_EXPIRED_TOKEN)

            user = self.db.query(UserTable).filter(
                UserTable.user_id == payload["user_id"]
            ).first()

            if not user:
                raise HTTPException(status_code=404, detail=String.USER_NOT_FOUND)

            # check old password reset
            rst_password = self.db.query(ResetPasswordTable).filter(
                ResetPasswordTable.user_email == user.email_address,
                ResetPasswordTable.is_used == False
            ).first()

            if not rst_password:
                raise HTTPException(status_code=404, detail=String.PASSWORD_RESET_NOT_FOUND)

            # mark as used
            rst_password.is_used = True

            # update password
            user.password_hash = Hashing.create_hash(new_password)

            # user Notification
            new_notification = NotificationTable(
                target_id=user.user_id,
                type=NotificationType.ALERT,
                title="Password Reset Successful",
                body=f"Your password has been successfully reset on ip address {ip}."
            )
            self.db.add(new_notification)
            self.db.flush()

            # real time notification
            notificationServices = NotificationServices(
                db=self.db,
                background_tasks=self.background_tasks
            )

            notificationServices.send_notification(
                data=NotificationData(
                    user_id=user.user_id,
                    template="auth.password.reset.success",
                    context={
                        "ip": ip,
                    },
                    noty_type=NotificationType.ALERT,
                    push=True,
                    sms=False,
                    email=False
                )
            )

            self.db.commit()
            self.db.refresh(new_notification)
            self.db.refresh(user)
            self.db.refresh(rst_password)

            return GlobalResponse(
                success=True,
                message="Password reset successful",
                data={}
            )

        except HTTPException:
            raise

        except Exception as e:
            self.db.rollback()
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)

    def change_password(self, payload: ChangePasswordRequest):
        try:
            user_id: str = payload.user_id
            access_token: str = payload.access_token
            android_id: str = payload.device_id
            android_uuid: str = payload.device_uuid
            user_password: str = payload.user_password
            new_password: str = payload.new_password

            if user_password == new_password:
                raise HTTPException(status_code=400, detail="New password must be different")

            user_verification_service = UserVerificationService(self.db)

            user = user_verification_service.verify_user(
                user_id=user_id,
                access_token=access_token,
                android_id=android_id,
                android_uuid=android_uuid
            )

            user.password_hash = Hashing.create_hash(new_password)

            ip: str = self.request.client.host

            new_notification = NotificationTable(
                target_id=user.user_id,
                type=NotificationType.ALERT,
                title="Password Changed",
                body=f"Your password was changed from IP {ip}. If this wasn't you, reset your password immediately."
            )
            self.db.add(new_notification)
            self.db.flush()

            # real time notification
            notificationServices = NotificationServices(
                db=self.db,
                background_tasks=self.background_tasks
            )
            
            notificationServices.send_notification(
                data=NotificationData(
                    user_id=user.user_id,
                    template="auth.password.changed",
                    context={
                        "ip": ip,
                    },
                    noty_type=NotificationType.ALERT,
                    push=True,
                    sms=False,
                    email=False
                )
            )

            self.db.commit()
            self.db.refresh(user)
            self.db.refresh(new_notification)

            return GlobalResponse(
                success=True,
                message="Password changed successfully",
                data={}
            )

        except HTTPException:
            raise

        except Exception as e:
            self.db.rollback()
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)
    
