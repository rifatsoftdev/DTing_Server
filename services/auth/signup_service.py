from fastapi import HTTPException, BackgroundTasks, Request, status
from sqlalchemy.orm import Session
from datetime import datetime
from google.oauth2 import id_token
from google.auth.transport import requests

from app.constants import AnsiColor, ENV, String
from app.schema.auth_schemas import NewUserEmailVerificationRequest
from app.utils import Generators, Hashing, Validator, Helpers
from app.enums import Gender
from app.model import UserTable, SettingsTable, CountryTable, OTPTable, SessionTable
from app.schema import RegisterRequest, GlobalResponse

from services.auth.token_service import TokenGenerators
from services.auth.user_repository import UserRepository
from services.notification.notification_services import (
    NotificationServices,
    NotificationData,
    NotificationEvent,
)


class RegistrationService(UserRepository, TokenGenerators):
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

        TokenGenerators.__init__(self, db=db)

    @staticmethod
    def _is_expired(expires_at: datetime | None) -> bool:
        if not expires_at:
            return False

        now = Helpers.utc6dhaka()
        if expires_at.tzinfo is None:
            now = now.replace(tzinfo=None)

        return expires_at < now
    
    def _create_new_user(
        self,
        full_name: str,
        email_address: str,
        phone_number: str,
        country: CountryTable,
        user_password: str,
        date_of_birth: datetime | None = None,
        user_gender: str = None,
        device_id: str = None,
        device_uuid: str = None,
        ip: str = None
        
    ) -> UserTable | None:
        gender = Gender.UNDIFINED
        if user_gender:
            try:
                gender = Gender(user_gender.strip().lower())
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid gender value"
                )

        if not Validator.valid_email(email_address):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=String.INVALID_EMAIL_ADDRESS
            )

        if phone_number and not Validator.validate_phone(
            country.country_code + phone_number,
            country.country_iso
        ):
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
            country_code=country.country_code,
            password_hash=Hashing.create_hash(user_password) if user_password else None,
            profile_image_url=None,
            date_of_birth=date_of_birth,
            user_gender=gender
        )
        self.db.add(new_user)
        self.db.flush()
        

        # create settings
        settings = SettingsTable(
            user_id=user_id,
            dark_mode=False,
            language="en",
            email_notifications=True,
            sms_notifications=False,
            push_notifications=True,
            marketing_notifications=False,
            login_alerts=True,
            new_device_alerts=True,
            password_change_alerts=True,
            profile_visibility="private",
            show_email=False,
            show_phone=False,
            timezone="Asia/Dhaka",
            currency=country.currency,
            date_format="YYYY-MM-DD",
            account_deactivated=False,
            biometric_enabled=False
        )
        self.db.add(settings)
        self.db.flush()

        return new_user
    
    # Signup function
    def signup(self, payload: RegisterRequest) -> GlobalResponse:
        """ Register a user """
        try:
            
            ip: str = self.request.client.host

            # Step 1: Check if user already exists and validate country
            country = self.db.query(CountryTable).filter(
                CountryTable.country_code == payload.country_code
            ).first()

            if (not country):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=String.COUNTRY_NOT_FOUND
                )

            if self.check_user_already_exists(
                email=payload.email_address,
                phone=payload.phone_number,
                country_code=payload.country_code
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=String.USER_ALRADY_EXISTS
                )

            # Step 2: Create User
            created_user: UserTable = self._create_new_user(
                full_name=payload.full_name,
                email_address=payload.email_address,
                phone_number=payload.phone_number,
                country=country,
                user_password=payload.user_password,
                user_gender=payload.user_gender,
                device_id=payload.device_id,
                device_uuid=payload.device_uuid,
                ip=ip,
                date_of_birth=payload.date_of_birth
            )

            # Step 3-5: Send and save email verification OTP
            response = self.email_verification_required_response(
                user=created_user,
                device_id=payload.device_id,
                device_uuid=payload.device_uuid
            )

            # Step 6: Commit db if no error
            self.db.commit()
            self.db.refresh(created_user)

            # Step 7: Return Response
            return response

        except HTTPException:
            self.db.rollback()
            raise

        except Exception as e:
            self.db.rollback()
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)


    # Email verification required response
    def email_verification_required_response(
        self,
        user: UserTable,
        device_id: str,
        device_uuid: str
    ) -> GlobalResponse:
        otp: str = Generators.generate_otp()
        email_sent: bool = False

        email_verification_token: str = self._create_token(
            token_type=String.EMAIL_VERIFICATION_TOKEN,
            expire_min=ENV.OTP_TOKEN_EXPIRE_MIN,
            data={
                "user_id": user.user_id,
                "email_address": user.email_address,
                "device_id": device_id,
                "device_uuid": device_uuid,
                "requires_otp": True
            }
        )

        self.db.query(OTPTable).filter(
            OTPTable.user_id == user.user_id
        ).delete()

        new_otp_record = OTPTable(
            user_id=user.user_id,
            otp_token=email_verification_token,
            device_id=device_id,
            device_uuid=device_uuid,
            delever_to=user.email_address,
            otp_hash=Hashing.create_hash(otp),
            expires_at=Helpers.utc6dhaka() + Helpers.minutes_to_timedelta(ENV.OTP_TOKEN_EXPIRE_MIN)
        )
        self.db.add(new_otp_record)
        self.db.flush()

        if user.email_address:
            notification_service = NotificationServices(
                db=self.db,
                background_tasks=self.background_tasks
            )

            notification_service = NotificationServices(
            db=self.db,
            background_tasks=self.background_tasks,
            request=self.request,
            authorization=self.authorization,
        )

        notification_service.send_notification(
            NotificationData(
                event=NotificationEvent.OTP,
                user_id=user.user_id,
                email_address=user.email_address,
                # fcm_token=session.fcm_token,  # optional, না দিলেও session থেকে খুঁজবে
                email=True,
                push=True,
                sms=False,
                context={
                    "name": user.full_name,
                    "email": user.email_address,
                    "otp": otp,
                },
                payload={
                    "type": "otp",
                    "user_id": user.user_id,
                }
            )
        )
        
        return GlobalResponse(
            status_code=status.HTTP_201_CREATED,
            success=True,
            action="verify_email",
            message="Please verify your email before login.",
            data={
                "user_id": user.user_id,
                "email_sent": email_sent,
                "email_verification_token": email_verification_token
            },
            next_step={
                "endpoint": "/auth/verify-new-user-email",
                "method": "POST",
                "payload": {
                    "user_id": user.user_id,
                    "otp": "otp",
                    "email_verification_token": email_verification_token,
                    "device_id": device_id,
                    "device_uuid": device_uuid
                }
            }
        )


    # New user email veryfication
    def veryfy_new_user_email(self, payload: NewUserEmailVerificationRequest) -> GlobalResponse:
        try:
            token_payload = self._decode_token(payload.email_verification_token)

            if token_payload is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=String.INVALID_OR_EXPIRED_TOKEN
                )

            if token_payload.get("type") != String.EMAIL_VERIFICATION_TOKEN:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=String.INVALID_TOKEN_TYPE
                )

            if token_payload.get("user_id") != payload.user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=String.INVALID_TOKEN
                )

            user = self.db.query(UserTable).filter(
                UserTable.user_id == payload.user_id
            ).first()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=String.USER_NOT_FOUND
                )

            otp_record = self.db.query(OTPTable).filter(
                OTPTable.user_id == user.user_id,
                OTPTable.otp_token == payload.email_verification_token,
                OTPTable.device_id == payload.device_id,
                OTPTable.device_uuid == payload.device_uuid,
                OTPTable.delever_to == user.email_address
            ).first()

            if not otp_record:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=String.OTP_NOT_FOUND
                )

            if self._is_expired(otp_record.expires_at):
                self.db.delete(otp_record)
                self.db.commit()
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=String.TIME_LIMET_EXPAIRE
                )

            if not Hashing.verify_otp(payload.otp, otp_record.otp_hash):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=String.INVALID_OTP
                )

            user.email_verified = True
            self.db.delete(otp_record)

            token_data = {
                "user_id": user.user_id,
                "email_address": user.email_address,
                "device_id": payload.device_id,
                "device_uuid": payload.device_uuid
            }

            access_token = self._create_token(
                token_type=String.ACCESS_TOKEN,
                expire_min=ENV.ACCESS_EXPIRE,
                data=token_data
            )

            refresh_token = self._create_token(
                token_type=String.REFRESH_TOKEN,
                expire_day=ENV.REFRESH_EXPIRE,
                data=token_data
            )

            ip = self.request.client.host if self.request and self.request.client else None
            session = self.db.query(SessionTable).filter(
                SessionTable.user_id == user.user_id,
                SessionTable.device_id == payload.device_id,
                SessionTable.device_uuid == payload.device_uuid
            ).first()

            if session:
                session.access_token_hash = Hashing.create_hash(access_token)
                session.refresh_token_hash = Hashing.create_hash(refresh_token)
                session.last_ip_address = ip
                session.is_login = True
                session.otp_verified = True
                session.login_at = Helpers.utc6dhaka()
            else:
                session = SessionTable(
                    user_id=user.user_id,
                    fcm_token=None,
                    access_token_hash=Hashing.create_hash(access_token),
                    refresh_token_hash=Hashing.create_hash(refresh_token),
                    device_uuid=payload.device_uuid,
                    device_id=payload.device_id,
                    last_ip_address=ip,
                    is_login=True,
                    otp_verified=True,
                    login_at=Helpers.utc6dhaka()
                )
                self.db.add(session)

            self.db.commit()
            self.db.refresh(user)

            return GlobalResponse(
                status_code=status.HTTP_200_OK,
                success=True,
                action="login",
                message="Login successful",
                data={
                    "requires_2fa": False,
                    "user_id": user.user_id,
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_type": "bearer",
                    "expires_in": ENV.ACCESS_EXPIRE,
                    "email_address": user.email_address,
                    "phone_number": f"{user.country_code or ''}{user.phone_number or ''}" or None
                },
                next_step={}
            )

        except HTTPException:
            self.db.rollback()
            raise

        except Exception as e:
            self.db.rollback()
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)





# ==============================================================================
# ==============================================================================
