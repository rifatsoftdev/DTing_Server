from fastapi import HTTPException, BackgroundTasks, Request, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.constants import AnsiColor, ENV, String
from app.enums import TwoFactorType
from app.model import OTPTable, TwoFactorTable
from app.schema import (
    GlobalResponse, TOTPSetupRequest, TOTPConfirmRequest, TOTPAuthDisableRequest,
    EmailTFASetupRequest, EmailTFAConfirmRequest, EmailTFADisableRequest,
    SMSTFASetupRequest, SMSTFAConfirmRequest, SMSTFADisableRequest
)
from services.auth.token_service import TokenGenerators
from services.auth.user_verification import UserVerificationService
from app.utils import Generators, Hashing, Helpers, TwoFactorAuth

from services.notification.notification_services import NotificationServices, NotificationData, NotificationEvent


class TFAServices(TokenGenerators):
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

    def __verify_user(self, user_id: str, access_token: str, device_id: str, device_uuid: str, password: str = None):
        user_verification_service = UserVerificationService(
            db=self.db,
            background_tasks=self.background_tasks,
            request=self.request,
            authorization=self.authorization
        )

        return user_verification_service.verify_user_authorization()

    def __get_method(self, user_id: str, method_type: TwoFactorType) -> TwoFactorTable | None:
        return self.db.query(TwoFactorTable).filter(
            TwoFactorTable.user_id == user_id,
            TwoFactorTable.method_type == method_type
        ).first()

    def __has_enabled_method(self, user_id: str) -> bool:
        return self.db.query(TwoFactorTable).filter(
            TwoFactorTable.user_id == user_id,
            TwoFactorTable.is_enabled == True
        ).first() is not None

    def __upsert_method(
        self,
        user_id: str,
        method_type: TwoFactorType,
        is_enabled: bool,
        delivery_address: str = None,
        secret_key: str = None
    ) -> TwoFactorTable:
        method = self.__get_method(user_id, method_type)
        if not method:
            method = TwoFactorTable(
                user_id=user_id,
                method_type=method_type
            )
            self.db.add(method)
            self.db.flush()

        should_be_primary = is_enabled and not self.__has_enabled_method(user_id)
        method.is_enabled = is_enabled
        method.delivery_address = delivery_address
        method.secret_key = secret_key
        method.is_primary = should_be_primary
        
        return method

    @staticmethod
    def __device_id(payload) -> str:
        return getattr(payload, "device_id", None) or getattr(payload, "android_id", None)

    @staticmethod
    def __device_uuid(payload) -> str:
        return getattr(payload, "device_uuid", None) or getattr(payload, "android_uuid", None)

    # ==============================================================================

    def totp_setup(self, payload: TOTPSetupRequest) -> GlobalResponse:
        try:
            user = self.__verify_user(
                user_id=payload.user_id,
                access_token=payload.access_token,
                device_id=self.__device_id(payload),
                device_uuid=self.__device_uuid(payload)
            )

            existing_totp = self.__get_method(user.user_id, TwoFactorType.TOTP)
            if existing_totp and existing_totp.is_enabled:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Two Factor Authentication already enabled"
                )

            secret = TwoFactorAuth.generate_secret()
            method = self.__upsert_method(
                user_id=user.user_id,
                method_type=TwoFactorType.TOTP,
                is_enabled=False,
                secret_key=secret
            )

            qr_uri = TwoFactorAuth.get_qr_uri(
                user_email=user.email_address,
                issuer="PocketPay",
                secret=secret
            )

            self.db.commit()
            self.db.refresh(method)

            return GlobalResponse(
                status_code=status.HTTP_200_OK,
                success=True,
                action="tfa_setup",
                message="TOTP secret generated",
                data={
                    "totp_secret": secret,
                    "qr_uri": qr_uri
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

    def totp_confirm(self, payload: TOTPConfirmRequest) -> GlobalResponse:
        try:
            user = self.__verify_user(
                user_id=payload.user_id,
                access_token=payload.access_token,
                device_id=self.__device_id(payload),
                device_uuid=self.__device_uuid(payload)
            )

            method = self.__get_method(user.user_id, TwoFactorType.TOTP)
            stored_secret = method.secret_key if method else None

            if not stored_secret:
                raise HTTPException(status_code=400, detail="TOTP secret not found")

            if not TwoFactorAuth.verify_otp(stored_secret, payload.totp_code):
                raise HTTPException(status_code=400, detail="Invalid TOTP code")

            should_be_primary = not self.__has_enabled_method(user.user_id)
            method.is_enabled = True
            method.delivery_address = None
            method.is_primary = should_be_primary

            self.db.commit()
            self.db.refresh(method)

            return GlobalResponse(
                status_code=status.HTTP_200_OK,
                success=True,
                action="tfa_enabled",
                message="Two Factor Authentication enabled",
                data={},
                next_step={}
            )

        except HTTPException:
            self.db.rollback()
            raise

        except Exception as e:
            self.db.rollback()
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)

    def totp_disable(self, payload: TOTPAuthDisableRequest) -> GlobalResponse:
        try:
            user = self.__verify_user(
                user_id=payload.user_id,
                access_token=payload.access_token,
                device_id=self.__device_id(payload),
                device_uuid=self.__device_uuid(payload),
                password=payload.user_password
            )

            method = self.__get_method(user.user_id, TwoFactorType.TOTP)
            if not method or not method.is_enabled:
                raise HTTPException(status_code=400, detail="TOTP secret not found")

            self.db.delete(method)

            self.db.commit()

            return GlobalResponse(
                status_code=status.HTTP_200_OK,
                success=True,
                action="tfa_disabled",
                message="Two Factor Authentication disabled",
                data={},
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

    def email_setup(self, payload: EmailTFASetupRequest) -> GlobalResponse:
        try:
            # Strp 1: Verify user and token
            user = self.__verify_user(
                user_id=payload.user_id,
                access_token=payload.access_token,
                device_id=self.__device_id(payload),
                device_uuid=self.__device_uuid(payload)
            )

            # Step 2: Check if email TFA is already enabled            
            existing_email = self.__get_method(user.user_id, TwoFactorType.EMAIL)
            if existing_email and existing_email.is_enabled:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail="Email Two Factor Authentication already enabled"
                )

            old_otp = self.db.query(OTPTable).filter(
                OTPTable.user_id == user.user_id,
                OTPTable.delever_to == user.email_address
            ).first()

            if old_otp:
                self.db.delete(old_otp)
                self.db.flush()
            
            # Step 3: Generate OTP and Token
            otp_token = self._create_token(
                data={
                    "method": "email_tfa",
                    "user_id": user.user_id,
                    "delever_to": user.email_address,
                    "device_id": self.__device_id(payload),
                    "device_uuid": self.__device_uuid(payload)
                },
                token_type="email_tfa",
                expire_min=ENV.OTP_TOKEN_EXPIRE_MIN
            )

            otp: str = Generators.generate_otp()
            
            # Step 4: Send Email
            notification_service = NotificationServices(
                db=self.db,
                background_tasks=self.background_tasks,
                request=self.request,
                authorization=self.authorization
            )

            notification_service.send_notification(
                NotificationData(
                    user_id=user.user_id,
                    email_address=user.email_address,
                    template="auth.otp",
                    context={
                        "name": user.full_name,
                        "email": user.email_address,
                        "otp": otp
                    },
                    noty_type="otp",
                    push=False,
                    email=True,
                    sms=False
                )
            )
            
            # Step 5: Save OTP on db
            otp_record = OTPTable(
                user_id=user.user_id,
                otp_token=otp_token,
                device_id=self.__device_id(payload),
                device_uuid=self.__device_uuid(payload),
                delever_to=user.email_address,
                otp_hash=Hashing.create_hash(otp),
                expires_at=Helpers.utc6dhaka() + timedelta(minutes=5)
            )
            self.db.add(otp_record)
            self.db.flush()

            if ENV.DEBUG:
                print(f"{AnsiColor.BLUE}INFO{AnsiColor.RESET}:     Email TFA OTP sent to {user.email_address} code {otp}")

            # Step 6: commit and refresh db
            self.db.commit()
            self.db.refresh(otp_record)

            # Step 7: Return Responce
            return GlobalResponse(
                status_code=status.HTTP_200_OK,
                success=True,
                action="email_tfa_setup",
                message="Email TFA code sent",
                data={
                    "otp_token": otp_token,
                    "email": user.email_address
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

    def email_confirm(self, payload: EmailTFAConfirmRequest) -> GlobalResponse:
        try:
            user = self.__verify_user(
                user_id=payload.user_id,
                access_token=payload.access_token,
                device_id=self.__device_id(payload),
                device_uuid=self.__device_uuid(payload)
            )

            otp_record = self.db.query(OTPTable).filter(
                OTPTable.user_id == user.user_id,
                OTPTable.delever_to == user.email_address,
                OTPTable.otp_token == payload.otp_token
            ).first()

            if not otp_record:
                raise HTTPException(status_code=404, detail=String.OTP_NOT_FOUND)

            token_payload = self._decode_token(payload.otp_token)

            if token_payload is None:
                raise HTTPException(status_code=401, detail=String.TIME_LIMET_EXPAIRE)

            if token_payload.get("method") != "email_tfa":
                raise HTTPException(status_code=401, detail=String.INVALID_TOKEN_TYPE)

            if token_payload.get("user_id") != user.user_id:
                raise HTTPException(status_code=401, detail=String.INVALID_TOKEN)

            token_device_id = token_payload.get("device_id") or token_payload.get("android_id")
            token_device_uuid = token_payload.get("device_uuid") or token_payload.get("android_uuid")
            
            if self.__device_id(payload) != token_device_id or self.__device_uuid(payload) != token_device_uuid:
                raise HTTPException(status_code=401, detail="Invalid Device")

            if not Hashing.verify_otp(payload.otp, otp_record.otp_hash):
                raise HTTPException(status_code=401, detail=String.INVALID_OTP)

            method = self.__upsert_method(
                user_id=user.user_id,
                method_type=TwoFactorType.EMAIL,
                is_enabled=True,
                delivery_address=user.email_address,
                secret_key=None
            )
            self.db.delete(otp_record)

            self.db.commit()
            self.db.refresh(method)

            return GlobalResponse(
                status_code=status.HTTP_200_OK,
                success=True,
                action="email_tfa_enabled",
                message="Email Two Factor Authentication enabled",
                data={},
                next_step={}
            )

        except HTTPException:
            self.db.rollback()
            raise

        except Exception as e:
            self.db.rollback()
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)

    def email_disable(self, payload: EmailTFADisableRequest) -> GlobalResponse:
        try:
            user = self.__verify_user(
                user_id=payload.user_id,
                access_token=payload.access_token,
                device_id=self.__device_id(payload),
                device_uuid=self.__device_uuid(payload),
                password=payload.user_password
            )

            method = self.__get_method(user.user_id, TwoFactorType.EMAIL)
            if not method or not method.is_enabled:
                raise HTTPException(status_code=400, detail="Email Two Factor Authentication is already disabled")

            self.db.delete(method)

            self.db.commit()

            return GlobalResponse(
                status_code=status.HTTP_200_OK,
                success=True,
                action="email_tfa_disabled",
                message="Email Two Factor Authentication disabled",
                data={},
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

    def sms_setup(self, payload: SMSTFASetupRequest) -> GlobalResponse:
        try:
            user = self.__verify_user(
                user_id=payload.user_id,
                access_token=payload.access_token,
                device_id=self.__device_id(payload),
                device_uuid=self.__device_uuid(payload)
            )

            if not user.phone_number:
                raise HTTPException(status_code=400, detail="User phone number is required for SMS TFA")

            existing_sms = self.__get_method(user.user_id, TwoFactorType.SMS)
            if existing_sms and existing_sms.is_enabled:
                raise HTTPException(status_code=400, detail="SMS Two Factor Authentication already enabled")

            old_otp = self.db.query(OTPTable).filter(
                OTPTable.user_id == user.user_id,
                OTPTable.delever_to == f"{user.country_code or ''}{user.phone_number or ''}"
            ).first()
            if old_otp:
                self.db.delete(old_otp)
                self.db.flush()

            otp_token = self._create_token(
                data={
                    "method": "sms_tfa",
                    "user_id": user.user_id,
                    "delever_to": f"{user.country_code or ''}{user.phone_number or ''}",
                    "device_id": self.__device_id(payload),
                    "device_uuid": self.__device_uuid(payload)
                },
                token_type="sms_tfa",
                expire_min=ENV.OTP_TOKEN_EXPIRE_MIN
            )

            otp = Generators.generate_otp()
            otp_record = OTPTable(
                user_id=user.user_id,
                otp_token=otp_token,
                device_id=self.__device_id(payload),
                device_uuid=self.__device_uuid(payload),
                delever_to=f"{user.country_code or ''}{user.phone_number or ''}",
                otp_hash=Hashing.create_hash(otp),
                expires_at=Helpers.utc6dhaka() + timedelta(minutes=5)
            )
            self.db.add(otp_record)

            if ENV.DEBUG:
                print(f"{AnsiColor.BLUE}INFO{AnsiColor.RESET}:     SMS TFA OTP sent to {user.phone_number} code {otp}")

            self.db.commit()
            self.db.refresh(otp_record)

            return GlobalResponse(
                status_code=status.HTTP_200_OK,
                success=True,
                action="sms_tfa_setup",
                message="SMS TFA code sent",
                data={
                    "otp_token": otp_token,
                    "phone_number": f"{user.country_code or ''}{user.phone_number or ''}"
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

    def sms_confirm(self, payload: SMSTFAConfirmRequest) -> GlobalResponse:
        try:
            user = self.__verify_user(
                user_id=payload.user_id,
                access_token=payload.access_token,
                device_id=self.__device_id(payload),
                device_uuid=self.__device_uuid(payload)
            )

            otp_record = self.db.query(OTPTable).filter(
                OTPTable.user_id == user.user_id,
                OTPTable.delever_to == f"{user.country_code or ''}{user.phone_number or ''}",
                OTPTable.otp_token == payload.otp_token
            ).first()

            if not otp_record:
                raise HTTPException(status_code=404, detail=String.OTP_NOT_FOUND)

            token_payload = self._decode_token(payload.otp_token)
            if token_payload is None:
                raise HTTPException(status_code=401, detail=String.TIME_LIMET_EXPAIRE)

            if token_payload.get("method") != "sms_tfa":
                raise HTTPException(status_code=401, detail=String.INVALID_TOKEN_TYPE)

            if token_payload.get("user_id") != user.user_id:
                raise HTTPException(status_code=401, detail=String.INVALID_TOKEN)

            token_device_id = token_payload.get("device_id") or token_payload.get("android_id")
            token_device_uuid = token_payload.get("device_uuid") or token_payload.get("android_uuid")

            if self.__device_id(payload) != token_device_id or self.__device_uuid(payload) != token_device_uuid:
                raise HTTPException(status_code=401, detail="Invalid Device")

            if not Hashing.verify_otp(payload.otp, otp_record.otp_hash):
                raise HTTPException(status_code=401, detail=String.INVALID_OTP)

            method = self.__upsert_method(
                user_id=user.user_id,
                method_type=TwoFactorType.SMS,
                is_enabled=True,
                delivery_address=f"{user.country_code or ''}{user.phone_number or ''}",
                secret_key=None
            )
            self.db.delete(otp_record)

            self.db.commit()
            self.db.refresh(method)

            return GlobalResponse(
                status_code=status.HTTP_200_OK,
                success=True,
                action="sms_tfa_enabled",
                message="SMS Two Factor Authentication enabled",
                data={},
                next_step={}
            )

        except HTTPException:
            self.db.rollback()
            raise

        except Exception as e:
            self.db.rollback()
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)

    def sms_disable(self, payload: SMSTFADisableRequest) -> GlobalResponse:
        try:
            user = self.__verify_user(
                user_id=payload.user_id,
                access_token=payload.access_token,
                device_id=self.__device_id(payload),
                device_uuid=self.__device_uuid(payload),
                password=payload.user_password
            )

            method = self.__get_method(user.user_id, TwoFactorType.SMS)
            if not method or not method.is_enabled:
                raise HTTPException(status_code=400, detail="SMS Two Factor Authentication is already disabled")

            self.db.delete(method)

            self.db.commit()

            return GlobalResponse(
                status_code=status.HTTP_200_OK,
                success=True,
                action="sms_tfa_disabled",
                message="SMS Two Factor Authentication disabled",
                data={},
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
