from fastapi import HTTPException, BackgroundTasks, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
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
from services.auth.repository import Repository
from services.notification.notification_services import (
    NotificationServices,
    NotificationData,
    NotificationEvent,
)


templates = Jinja2Templates(directory="templates")


class RegistrationService(Repository, TokenGenerators):
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
        TokenGenerators.__init__(self)

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

            if self._check_user_already_exists(
                email=payload.email_address,
                phone=payload.phone_number,
                country_code=payload.country_code
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=String.USER_ALREADY_EXISTS
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
        email_sent: bool = False

        # Step 4: Create OTP token for email verification
        email_verification_token, _ = self._create_token(
            expire_min=ENV.OTP_TOKEN_EXPIRE_MIN,
            payload={
                "token_type": String.EMAIL_VERIFICATION_TOKEN,
                "user_id": user.user_id,
                "email_address": user.email_address,
                "device_id": device_id,
                "device_uuid": device_uuid,
                "requires_otp": True
            }
        )

        email_verification_link: str = f"{ENV.AUTH_SERVER_URL}/auth/verify-new-user-email/{email_verification_token}"

        

        if user.email_address:
            notification_service = NotificationServices(
                db=self.db,
                background_tasks=self.background_tasks,
                request=self.request,
                authorization=self.authorization,
            )

            notification_service.send_notification(
                NotificationData(
                    event=NotificationEvent.EMAIL_VERIFICATION,
                    user_id=user.user_id,
                    email_address=user.email_address,
                    # fcm_token=session.fcm_token,  # optional, না দিলেও session থেকে খুঁজবে
                    email=True,
                    push=False,
                    sms=False,
                    template="email_verification",
                    context={
                        "name": user.full_name,
                        "verification_link": email_verification_link,
                    }
                )
            )
        
        return GlobalResponse(
            status_code=status.HTTP_201_CREATED,
            success=True,
            action="verify_email",
            message="Email verification required. Please check your email for the verification link.",
            data={
                "user_id": user.user_id,
                "email_sent": email_sent
            },
            next_step={}
        )


    # New user email veryfication
    def verify_new_user_email(self, email_verification_token: str) -> GlobalResponse:
        try:
            payload: dict = self._decode_token(email_verification_token)

            if payload is None:
                return HTMLResponse(
                    content=templates.get_template("server/verify-email-error.html").render(request=self.request),
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            if payload.get("token_type") != String.EMAIL_VERIFICATION_TOKEN:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=String.INVALID_TOKEN_TYPE
                )

            user: UserTable = self.db.query(UserTable).filter(
                UserTable.user_id == payload["user_id"]
            ).first()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=String.USER_NOT_FOUND
                )

            if (user.email_verified == True):
                return HTMLResponse(
                    content=templates.get_template("server/verify-email-complete.html").render(request=self.request, user=user),
                    status_code=status.HTTP_200_OK
                )
            
            user.email_verified = True
            # user.email_verified_at = Helpers.utc6dhaka()


            self.db.commit()
            self.db.refresh(user)

            return HTMLResponse(
                content=templates.get_template("server/verify-email-complete.html").render(request=self.request, user=user),
                status_code=status.HTTP_200_OK
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
