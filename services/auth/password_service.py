from fastapi import HTTPException, Request, BackgroundTasks, status
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from app.constants import String, AnsiColor, ENV
from app.enums import NotificationType, UserActivityType
from app.schema import ForgetPasswordRequest, GlobalResponse, ResetPasswordRequest, ChangePasswordRequest
from app.model import UserTable, ResetPasswordTable, NotificationTable, UserActivityTable, SettingsTable

from services.auth.token_service import TokenGenerators
from app.utils import Hashing, Helpers

from services.notification.notification_services import NotificationServices, NotificationData


templates = Jinja2Templates(directory="templates")



class PasswordService(TokenGenerators):
    def __init__(
        self,
        db: Session,
        background_tasks: BackgroundTasks,
        request: Request,
        authorization: str
    ):
        super().__init__()
        self.db = db
        self.background_tasks = background_tasks
        self.request = request
        self.authorization = authorization
    
    # Forget password 
    def reset_password(self, payload: ForgetPasswordRequest) -> GlobalResponse:
        try:
            # Step 1: Extract data from payload
            email_address: str= payload.email_address
            android_id: str = payload.device_id
            android_uuid: str = payload.device_uuid
            
            ip: str = self.request.client.host
            user_agent: str = self.request.headers.get("user-agent")
            auth: str = self.request.headers.get("authorization"),
            path: str = self.request.url.path,
            query: dict = dict(self.request.query_params),
            cookies: dict = self.request.cookies


            # Step 2: Check if user exists
            user: UserTable = self.db.query(UserTable).filter(
                UserTable.email_address == email_address
            ).first()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail=String.USER_NOT_FOUND
                )


            # Step 3: Generate Reset Token
            otp_token, _ = self._create_token(
                expire_min=ENV.PASS_RST_TOKEN_EXPIRE_MIN,
                payload={
                    "token_type": "otp",
                    "user_id": user.user_id,
                    "email_address": user.email_address,
                    "device_id": android_id,
                    "device_uuid": android_uuid
                }
            )


            # Step 4: Check old password reset
            rst_password = self.db.query(ResetPasswordTable).filter(
                ResetPasswordTable.user_email == user.email_address,
                ResetPasswordTable.expires_at > datetime.now(timezone.utc),
                ResetPasswordTable.is_used == False
            ).first()

            if rst_password:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=String.PASSWORD_RESET_ALREADY_SENT
                )
            

            # Step 5: Create Reset Password Record
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
            

            # Step 6: Send Email
            notificationServices = NotificationServices(
                db=self.db,
                background_tasks=self.background_tasks
            )

            reset_link: str = f"{ENV.AUTH_SERVER_URL}/auth/reset-password/{otp_token}"

            notificationServices.send_notification(
                data=NotificationData(
                    user_id=user.user_id,
                    email_address=user.email_address,
                    template="auth.password.reset.request",
                    context={
                        "name": user.full_name,
                        "email": user.email_address,
                        "reset_link": reset_link,
                    },
                    noty_type=NotificationType.ALERT,
                    push=True,
                    sms=False,
                    email=True
                )
            )
            

            # Step 7: User Notification
            new_notification = NotificationTable(
                target_id=user.user_id,
                type=NotificationType.ALERT,
                title="Reset Password Request Detected",
                body=f"We have received a password reset request for your account from {ip} IP address. Make sure you have your email address with you."
            )
            self.db.add(new_notification)
            self.db.flush()


            # Step 8: Log activity
            activity = UserActivityTable(
                user_id=user.user_id,
                activity_type=UserActivityType.PASSWORD_RESET,
                detail={
                    "action": "password_reset_requested",
                    "email": user.email_address,
                    "device_id": android_id,
                    "device_uuid": android_uuid
                },
                ip_address=ip,
                user_agent=user_agent
            )
            self.db.add(activity)


            # Step 9: Commit and refresh db
            self.db.commit()
            self.db.refresh(rst_password)
            self.db.refresh(new_notification)


            # Step 10: Return Response
            return GlobalResponse(
                status_code=status.HTTP_200_OK,
                success=True,
                action="password_reset",
                message="Password reset link sent successfully",
                data={},
                next_step={}
            )

        except HTTPException:
            raise

        except Exception as e:
            self.db.rollback()
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)


    # Render Reset Password Page
    def reset_password_page(self, password_token: str):
        try:
            # Step 1: Decode and validate the password token
            payload = self._decode_token(password_token)

            if not payload:
                return templates.TemplateResponse(
                    "server/expired.html",
                    {"request": self.request}
                )


            # Step 2: Check if user and reset record exist
            user: UserTable = self.db.query(UserTable).filter(
                UserTable.user_id == payload["user_id"]
            ).first()

            if not user:
                return templates.TemplateResponse(
                    "server/expired.html",
                    {"request": self.request}
                )

            rst_password = self.db.query(ResetPasswordTable).filter(
                ResetPasswordTable.user_email == user.email_address,
                ResetPasswordTable.is_used == False,
                ResetPasswordTable.expires_at > datetime.now(timezone.utc)
            ).first()

            if not rst_password:
                return templates.TemplateResponse(
                    "server/expired.html",
                    {"request": self.request}
                )


            # Step 3: Return the reset password template
            return templates.TemplateResponse(
                "user/reset_password.html",
                {
                    "request": self.request,
                    "password_token": password_token
                }
            )

        except HTTPException:
            raise

        except Exception as e:
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)


    # Set New Password after reset request
    def set_password(self, payload: ResetPasswordRequest):
        try:
            # Step 1: Extract data from payload
            reset_token = payload.password_token
            new_password = payload.new_password

            ip: str = self.request.client.host
            user_agent: str = self.request.headers.get("user-agent")
            auth: str = self.request.headers.get("authorization"),
            path: str = self.request.url.path,
            query: dict = dict(self.request.query_params),
            cookies: dict = self.request.cookies


            # Step 2: Decode and validate the password token
            payload: dict = self._decode_token(reset_token)

            if not payload:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=String.INVALID_OR_EXPIRED_TOKEN
                )


            # Step 3: Check if user exists
            user: UserTable = self.db.query(UserTable).filter(
                UserTable.user_id == payload["user_id"]
            ).first()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=String.USER_NOT_FOUND
                )


            # Step 4: Check old password reset
            rst_password = self.db.query(ResetPasswordTable).filter(
                ResetPasswordTable.user_email == user.email_address,
                ResetPasswordTable.is_used == False
            ).first()

            if not rst_password:
                raise HTTPException(
                    status_code=404,
                    detail=String.PASSWORD_RESET_NOT_FOUND
                )
            
            if (rst_password.is_used):
                raise HTTPException(
                    status_code=403,
                    detail="Password Alrady Changed"
                )

            rst_password.is_used = True


            # Step 5: update password and settings
            settings: SettingsTable = user.settings
            user.password_hash = Hashing.create_hash(new_password)
            settings.last_password_changed_at = Helpers.utc6dhaka()


            # Step 6: user Notification
            new_notification = NotificationTable(
                target_id=user.user_id,
                type=NotificationType.ALERT,
                title="Password Reset Successful",
                body=f"Your password has been successfully reset on ip address {ip}."
            )
            self.db.add(new_notification)
            self.db.flush()


            # Step 7: Send Notification
            notificationServices = NotificationServices(
                db=self.db,
                background_tasks=self.background_tasks
            )

            notificationServices.send_notification(
                data=NotificationData(
                    user_id=user.user_id,
                    email_address=user.email_address,
                    template="auth.password_change",
                    context={
                        "name": user.full_name,
                        "changed_at": Helpers.utc6dhaka().strftime("%Y-%m-%d %H:%M:%S"),
                        "ip_address": ip
                    },
                    noty_type=NotificationType.ALERT,
                    push=True,
                    sms=False,
                    email=True
                )
            )


            # Step 8: Log activity
            activity = UserActivityTable(
                user_id=user.user_id,
                activity_type=UserActivityType.PASSWORD_RESET,
                detail={
                    "action": "password_reset_completed",
                    "status": "success"
                },
                ip_address=ip,
                user_agent=user_agent
            )
            self.db.add(activity)

            self.db.commit()
            self.db.refresh(new_notification)
            self.db.refresh(user)
            self.db.refresh(rst_password)


            # Step 9: Return Response 
            return GlobalResponse(
                status_code=status.HTTP_200_OK,
                success=True,
                action="password_reset",
                message="Password reset successful",
                data={},
                next_step={}
            )

        except HTTPException:
            raise

        except Exception as e:
            self.db.rollback()
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)


    # Change Password
    def change_password(self, payload: ChangePasswordRequest):
        try:
            # Step 1: Extract data from payload
            user_id: str = payload.user_id
            android_id: str = payload.device_id
            access_token: str = payload.access_token
            android_uuid: str = payload.device_uuid
            user_password: str = payload.user_password
            new_password: str = payload.new_password

            ip: str = self.request.client.host


            # Step 1: Get current user
            user: UserTable = self.request.state.current_user
            

            # Step 3: Check current password
            if (not user.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=String.PASSWORD_NOT_SET
                )
                
            if not Hashing.verify_hash(user_password, user.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect current password"
                )
            

            # Step 4: Check if new password is same as old password
            if user_password == new_password:
                raise HTTPException(
                    status_code=400,
                    detail="New password must be different"
                )

            
            # Step 5: Update password and settings
            user.password_hash = Hashing.create_hash(new_password)
            settings: SettingsTable = user.settings
            settings.last_password_changed_at = Helpers.utc6dhaka()

            
            # Step 6: Create notification record and send alerts
            new_notification = NotificationTable(
                target_id=user.user_id,
                type=NotificationType.ALERT,
                title="Password Changed",
                body=f"Your password was changed from IP {ip}. If this wasn't you, reset your password immediately."
            )
            self.db.add(new_notification)
            self.db.flush()

            notificationServices = NotificationServices(
                db=self.db,
                background_tasks=self.background_tasks
            )
            
            notificationServices.send_notification(
                data=NotificationData(
                    user_id=user.user_id,
                    email_address=user.email_address,
                    template="auth.password_change",
                    context={
                        "name": user.full_name,
                        "changed_at": Helpers.utc6dhaka().strftime("%Y-%m-%d %H:%M:%S"),
                        "ip_address": ip
                    },
                    noty_type=NotificationType.ALERT,
                    push=True,
                    sms=False,
                    email=True
                )
            )

            
            # Step 7: Log activity
            user_agent: str = self.request.headers.get("user-agent")

            activity = UserActivityTable(
                user_id=user.user_id,
                activity_type=UserActivityType.PASSWORD_CHANGE,
                detail={
                    "action": "password_changed",
                    "device_id": android_id,
                    "device_uuid": android_uuid,
                    "status": "success"
                },
                ip_address=ip,
                user_agent=user_agent
            )
            self.db.add(activity)
            self.db.flush()


            # Step 8: Finalize database changes
            self.db.commit()
            self.db.refresh(user)
            self.db.refresh(new_notification)


            # Step 9: Return Response
            return GlobalResponse(
                status_code=status.HTTP_200_OK,
                success=True,
                action="password_changed",
                message="Password changed successfully",
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
