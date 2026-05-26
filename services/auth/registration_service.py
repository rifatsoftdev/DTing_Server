from fastapi import HTTPException, BackgroundTasks, Request, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from decimal import Decimal
from google.oauth2 import id_token
from google.auth.transport import requests

from app.constants import AnsiColor, ENV, String
from app.utils import Generators, Hashing, Validator, Helpers
from app.enums import Gender, KYCStatus, NotificationType
from app.model import UserTable, SettingsTable, SessionTable, NotificationTable, CountryTable
from app.schema import RegisterRequest, GlobalResponse, FinalSetupRequest

from services.auth.user_repository import UserRepository
from services.notification.noticication_services import NotificationServices, NotificationData



class RegistrationService(UserRepository):
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
    
    def __create_new_user(
        self,
        full_name: str,
        email_address: str,
        phone_number: str,
        country_code: str,
        country_iso: str,
        user_password: str,
        profile_image_url: str,
        device_id: str,
        device_uuid: str,
        ip: str,
        referral_account: str
    ) -> UserTable | None:
        
        if (not Validator.valid_email(email_address)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=String.INVALID_EMAIL_ADDRESS
            )
        
        if (phone_number and not Validator.validate_phone(country_code+phone_number, country_iso)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=String.INVALID_PHONE_NUMBER
            )

        user_id = Generators.generate_id("user")

        new_user = UserTable(
            user_id=user_id,
            full_name=full_name,
            email_address=email_address,
            phone_number=phone_number,
            country_code=country_code,
            password_hash=Hashing.create_hash(user_password) if user_password else None,
            profile_image_url=profile_image_url,
            referral_account=referral_account
        )
        self.db.add(new_user)
        self.db.flush()
        

        # create settings
        settings = SettingsTable(
            user_id=user_id,
            allow_notifications=True,
            dark_mode=False,
            language="en",
            account_locked=False
        )
        self.db.add(settings)
        self.db.flush()
    
        # create session
        session = SessionTable(
            user_id=user_id,
            fcm_token=None,
            access_token_hash=None,
            refresh_token_hash=None,
            device_uuid=device_uuid,
            device_id=device_id,
            last_ip_address=ip
        )
        self.db.add(session)
        self.db.flush()

        return new_user

    def new_user(
        self,
        full_name: str,
        email_address: str,
        device_id: str,
        device_uuid: str,
        ip: str,
        country_iso: str,
        phone_number: str = None,
        country_code: str = None,
        user_password: str = None,
        profile_image_url: str = None,
        referral_account: str = None
    )-> UserTable | None:
        """Create a new user."""
        try:
            if self.check_user_already_exists(
                email=email_address,
                phone=phone_number,
                country_code=country_code
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=String.USER_ALRADY_EXISTS
                )

            created_user = self.__create_new_user(
                full_name=full_name,
                email_address=email_address,
                phone_number=phone_number,
                country_code=country_code,
                country_iso=country_iso,
                user_password=user_password,
                profile_image_url=profile_image_url,
                device_id=device_id,
                device_uuid=device_uuid,
                ip=ip,
                referral_account=referral_account
            )
            
            # user Notification
            new_notification = NotificationTable(
                target_id=created_user.user_id,
                type=NotificationType.ALERT,
                title="Welcome to PocketPay! 🔐",
                body=f"Your account has been successfully set up. Your security is our priority—let’s get started."
            )
            self.db.add(new_notification)
            self.db.flush()

            # sent welcome email
            # self.background_tasks.add_task(send_welcome_email, email_address)

            # real time notification
            notificationServices = NotificationServices(
                db=self.db,
                background_tasks=self.background_tasks,
                request=self.request,
                authorization=self.authorization
            )

            notificationServices.send_notification(
                NotificationData(
                    user_id=created_user.user_id,
                    template="auth.welcome",
                    context={
                        "name": created_user.full_name,
                    },
                    noty_type=NotificationType.ALERT,
                    push=True,
                    sms=False,
                    email=False
                )
            )

            # return new user
            return created_user

        
        except HTTPException:
            raise

        except Exception as e:
            self.db.rollback()
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)
    
    def register(
        self,
        payload: RegisterRequest
    ) -> GlobalResponse:
        """Register a user and apply referral/welcome rewards."""
        try:
            # Helpers.print_payload(payload)
            ip: str = self.request.client.host

            country = self.db.query(CountryTable).filter(
                CountryTable.country_code == payload.country_code
            ).first()

            created_user = self.new_user(
                full_name=payload.full_name,
                email_address=payload.email_address,
                phone_number=payload.phone_number,
                country_code=payload.country_code,
                country_iso=country.country_iso,
                user_password=payload.user_password,
                profile_image_url=String.DEMO_PROFILE_IMAGE_URL,
                device_id=payload.device_id,
                device_uuid=payload.device_uuid,
                ip=ip,
                referral_account=payload.referral_account
            )
                
                
            self.db.commit()
            self.db.refresh(created_user)

            return GlobalResponse(
                success=True,
                message="Registration successful. Please verify with the OTP sent to your phone.",
                data={"sent_otp": False}
            )

        except HTTPException:
            self.db.rollback()
            raise

        except Exception as e:
            self.db.rollback()
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)

    def final_setup(self, payload: FinalSetupRequest):
        """Only required on google signin or singup"""
        try:
            idinfo = id_token.verify_oauth2_token(
                payload.token_id,
                requests.Request(),
                audience=ENV.GOOGLE_CLIENT_ID
            )

            google_id = idinfo.get("sub")
            email_address = idinfo.get("email")
            email_verified = idinfo.get("email_verified")

            if not google_id or not email_address or not email_verified:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=String.EMAIL_OR_PHONE_REQUIRED
                )

            user = self.db.query(UserTable).filter(
                UserTable.email_address == email_address
            ).first()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=String.USER_NOT_FOUND
                )

            if user.link_google and user.link_google != google_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=String.USER_ALRADY_EXISTS
                )

            country = None
            if payload.country_code:
                country = self.db.query(CountryTable).filter(
                    CountryTable.country_code == payload.country_code
                ).first()

                if not country:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Country not found"
                    )
                
                user.country_code = payload.country_code

            if payload.phone_number:
                if not payload.country_code or not country:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Country code is required with phone number"
                    )

                if not Validator.validate_phone(
                    payload.country_code + payload.phone_number,
                    country.country_iso
                ):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=String.INVALID_PHONE_NUMBER
                    )

                existing_phone_user = self.db.query(UserTable).filter(
                    UserTable.phone_number == payload.phone_number,
                    UserTable.country_code == payload.country_code,
                    UserTable.user_id != user.user_id
                ).first()

                if existing_phone_user:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=String.USER_ALRADY_EXISTS
                    )

                user.phone_number = payload.phone_number
                user.country_code = payload.country_code

            if payload.user_gender:
                try:
                    user.user_gender = Gender(payload.user_gender)
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid gender"
                    )

            if payload.date_of_birth:
                user.date_of_birth = payload.date_of_birth

            user.email_verified = True
            user.link_google = google_id
            user.updated_at = Helpers.utc6dhaka()

            settings = self.db.query(SettingsTable).filter(
                SettingsTable.user_id == user.user_id
            ).first()

            if settings and country:
                settings.country = country.country_iso

            session = self.db.query(SessionTable).filter(
                SessionTable.user_id == user.user_id,
                SessionTable.device_id == payload.device_id,
                SessionTable.device_uuid == payload.device_uuid
            ).first()

            if session:
                session.last_ip_address = self.request.client.host
                session.is_login = True
                session.otp_verified = True
                session.login_at = Helpers.utc6dhaka()

            self.db.commit()
            self.db.refresh(user)

            return GlobalResponse(
                success=True,
                message="Final setup completed successfully",
                data={
                    "user_id": user.user_id,
                    "email_address": user.email_address,
                    "phone_number": user.phone_number,
                    "country_code": user.country_code,
                    "user_gender": user.user_gender.value if user.user_gender else None,
                    "date_of_birth": user.date_of_birth,
                    "email_verified": user.email_verified
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
        

