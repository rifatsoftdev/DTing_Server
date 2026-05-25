from fastapi import Request, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests

from app.model import UserTable, SessionTable, NotificationTable
from app.enums import NotificationType
from app.constants import ENV, String, AnsiColor
from app.utils import Hashing, Helpers
from services import RegistrationService
from app.schema import GoogleLoginRequest, GlobalResponse, LinkGoogleAccountRequest

from services.notification.noticication_services import NotificationServices, NotificationData

from services.auth.user_verification import UserVerificationService
from services.auth.token_service import TokenGenerators


class GoogleOauth(TokenGenerators):
    def __init__(
        self,
        db: Session,
        background_tasks: BackgroundTasks,
        request: Request,
        authorization: str
    ):
        self.db = db
        self.background_tasks = background_tasks
        self.request = request
        self.authorization = authorization
        super().__init__(self.db)

    def google_login(
        self,
        payload: GoogleLoginRequest
    ) -> GlobalResponse:
        try:
            token_id = payload.token_id
            device_id = payload.device_id
            device_uuid = payload.device_uuid

            # 🔑 Verify token
            idinfo = id_token.verify_oauth2_token(
                token_id,
                requests.Request(),
                audience=ENV.GOOGLE_CLIENT_ID
            )
            
            google_id = idinfo["sub"]
            email_address = idinfo.get("email")
            email_verified = idinfo.get("email_verified")
            full_name =  idinfo.get("name")
            profile_image_url = idinfo.get("picture")

            # print(google_id)

            # Request info
            ip: str = self.request.client.host
            user_agent: str = self.request.headers.get("user-agent")
            auth: str = self.request.headers.get("authorization")
            path: str = self.request.url.path
            query: dict = dict(self.request.query_params)
            cookies: dict = self.request.cookies

            # print(f"{email_address} {email_verified}")
            if (not email_address or not email_verified):
                raise HTTPException(
                    status_code=400,
                    detail=String.EMAIL_OR_PHONE_REQUIRED
                )
            
            registrationService = RegistrationService(
                db=self.db,
                background_tasks=self.background_tasks,
                request=self.request,
                authorization=self.authorization
            )
            
            existing_user: UserTable = registrationService.check_user_already_exists(
                email=email_address
            )

            # login
            if existing_user:
                if (existing_user.link_google and existing_user.link_google != google_id):
                    raise HTTPException(
                        status_code=409,
                        detail=String.USER_ALRADY_EXISTS
                    )
                
                if not existing_user.link_google:
                    existing_user.link_google = google_id
                    self.db.commit()
                    self.db.refresh(existing_user)
            
            # registration
            else:
                created_user = registrationService.new_user(
                    full_name=full_name,
                    email_address=email_address,
                    device_id=device_id,
                    device_uuid=device_uuid,
                    profile_image_url=profile_image_url,
                    ip=ip,
                    country_iso=None
                )

                # email verified
                created_user.email_verified = True
                created_user.link_google = google_id

                self.db.commit()
                self.db.refresh(created_user)

                # reward
                reward = ENV.NEW_USER_REWARD_WITH_NO_REFERRAL

                self.send_reward(
                    user_id=created_user.user_id,
                    title="Welcome Reward",
                    body=f"Welcome to PocketPay! You have rechived a reward of {reward} BD.",
                    amount=reward
                )
            
            user = existing_user if existing_user else created_user

            # Generate access token
            access_token = self._create_token(
                token_type="access",
                expire_min=ENV.ACCESS_EXPIRE,
                data={
                    "user_id": user.user_id,
                    "email_address": user.email_address,
                    "device_id": device_id,
                    "device_uuid": device_uuid
                }
            )

            # Generate refresh token
            refresh_token = self._create_token(
                token_type="refresh",
                expire_min=ENV.REFRESH_EXPIRE,
                data={
                    "user_id": user.user_id,
                    "email_address": user.email_address,
                    "device_id": device_id,
                    "device_uuid": device_uuid
                }
            )

            # Update session
            session = self.db.query(SessionTable).filter(
                SessionTable.user_id == user.user_id,
                SessionTable.device_id == device_id,
                SessionTable.device_uuid == device_uuid,
                SessionTable.is_login == True
            ).first()

            if session:
                session.access_token_hash = Hashing.create_hash(access_token)
                session.refresh_token_hash = Hashing.create_hash(refresh_token)
                session.last_ip_address = ip
                session.is_login = True
                session.otp_verified = True
                session.login_at = Helpers.utc6dhaka()
                self.db.commit()
                self.db.refresh(session)
            
            else:
                session = SessionTable(
                    user_id=user.user_id,
                    fcm_token=None,
                    access_token_hash=Hashing.create_hash(access_token),
                    refresh_token_hash=Hashing.create_hash(refresh_token),
                    device_uuid=device_uuid,
                    device_id=device_id,
                    last_ip_address=ip,
                    is_login=True,
                    otp_verified=True,
                )
                self.db.add(session)

                # all commit and refresh
                self.db.commit()
                if not existing_user:
                    self.db.refresh(created_user)
                self.db.refresh(session)
            
            return GlobalResponse(
                success=True,
                message="Login Successful",
                data={
                    "user_id": user.user_id,
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "email_address": user.email_address,
                    "phone_number": None
                }
            )
        
        except HTTPException:
            self.db.rollback()
            raise

        except ValueError:
            self.db.rollback()
            raise HTTPException(status_code=401, detail=String.INVALID_TOKEN)

        except Exception as e:
            self.db.rollback()
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)

    def link_google(
        self,
        payload: LinkGoogleAccountRequest,
        request: Request,
        background_tasks: BackgroundTasks,
        db: Session
    ):
        try:
            user_id: str = payload.user_id
            access_token: str = payload.access_token
            android_id: str = payload.device_id
            android_uuid: str = payload.device_uuid
            token_id: str = payload.token_id

            user_verification_service = UserVerificationService(db)

            user = user_verification_service.verify_user(
                user_id=user_id,
                access_token=access_token,
                android_id=android_id,
                android_uuid=android_uuid
            )

            idinfo = id_token.verify_oauth2_token(
                token_id,
                requests.Request(),
                ENV.GOOGLE_CLIENT_ID
            )

            email_address = idinfo.get("email")
            email_verified = idinfo.get("email_verified")
            full_name = idinfo.get("name")
            profile_image_url = idinfo.get("picture")

            if not email_address:
                raise HTTPException(status_code=400, detail="Google account email not found")

            if user.email_address.lower() != email_address.lower():
                raise HTTPException(status_code=409, detail="Google account email does not match")

            if email_verified:
                user.email_verified = True

            if profile_image_url and not user.profile_image_url:
                user.profile_image_url = profile_image_url

            if full_name and not user.full_name:
                user.full_name = full_name

            ip: str = request.client.host

            new_notification = NotificationTable(
                target_id=user.user_id,
                type=NotificationType.ALERT,
                title="Google Account Linked",
                body=f"Your Google account was linked from IP {ip}."
            )
            db.add(new_notification)
            db.flush()

            notificationServices = NotificationServices(
                db=db,
                background_tasks=background_tasks
            )

            notificationServices.send_notification(
                NotificationData(
                    user_id=user.user_id,
                    title="Google Account Linked",
                    template="admin.custom",
                    context={
                        "body": "Your Google account was linked successfully.",
                    },
                    noty_type=NotificationType.ALERT,
                    push=True,
                    sms=False,
                    email=False
                )
            )

            db.commit()
            db.refresh(user)
            db.refresh(new_notification)

            return GlobalResponse(
                success=True,
                message="Google account linked successfully",
                data={}
            )
        
        except HTTPException:
            raise

        except Exception as e:
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)



