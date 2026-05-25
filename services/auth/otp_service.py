from fastapi import HTTPException, Request, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import timedelta

from app.constants import ENV, AnsiColor, String
from app.enums import OTPMethod, OTPPurpose, TwoFactorType
from app.model import OTPTable, SessionTable, TwoFactorTable, UserTable
from app.schema import OTPRequest, GlobalResponse, VerifyOTPRequest
from app.utils import Generators, Hashing, Helpers, TwoFactorAuth
from services.auth.token_service import TokenGenerators
from services.notification.noticication_services import NotificationServices


class OTPService(TokenGenerators):
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

    @staticmethod
    def _enum_value(value) -> str:
        return value.value if hasattr(value, "value") else str(value)

    def _decode_otp_request_token(self, otp_token: str) -> dict:
        token_payload = self._decode_token(otp_token)

        if token_payload is None:
            raise HTTPException(status_code=401, detail=String.TIME_LIMET_EXPAIRE)

        if token_payload.get("type") != "otp_token":
            raise HTTPException(status_code=401, detail=String.INVALID_TOKEN_TYPE)

        if not token_payload.get("user_id"):
            raise HTTPException(status_code=401, detail=String.INVALID_TOKEN)

        return token_payload

    def _get_otp_user(self, user_id: str) -> UserTable:
        user = self.db.query(UserTable).filter(UserTable.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail=String.USER_NOT_FOUND)
        return user

    def _get_otp_delivery_address(self, user: UserTable, method: str) -> str:
        if method == OTPMethod.EMAIL.value:
            tfa_method = self.db.query(TwoFactorTable).filter(
                TwoFactorTable.user_id == user.user_id,
                TwoFactorTable.method_type == TwoFactorType.EMAIL,
                TwoFactorTable.is_enabled == True
            ).first()
            if not tfa_method:
                raise HTTPException(status_code=400, detail="Email two-factor method is not enabled")
            return tfa_method.delivery_address or user.email_address

        if method == OTPMethod.SMS.value:
            tfa_method = self.db.query(TwoFactorTable).filter(
                TwoFactorTable.user_id == user.user_id,
                TwoFactorTable.method_type == TwoFactorType.SMS,
                TwoFactorTable.is_enabled == True
            ).first()
            if not tfa_method:
                raise HTTPException(status_code=400, detail="SMS two-factor method is not enabled")
            phone_number = tfa_method.delivery_address or f"{user.country_code or ''}{user.phone_number or ''}"
            return phone_number or None

        raise HTTPException(status_code=400, detail="OTP can only be sent by email or sms")

    def _verify_totp(self, user: UserTable, otp: str) -> None:
        tfa_method = self.db.query(TwoFactorTable).filter(
            TwoFactorTable.user_id == user.user_id,
            TwoFactorTable.method_type == TwoFactorType.TOTP,
            TwoFactorTable.is_enabled == True
        ).first()

        if not tfa_method or not tfa_method.secret_key:
            raise HTTPException(status_code=400, detail="TOTP two-factor method is not enabled")

        if not TwoFactorAuth.verify_otp(tfa_method.secret_key, otp):
            raise HTTPException(status_code=401, detail=String.INVALID_OTP)

    def _validate_otp_request(
        self,
        token_payload: dict,
        method: str,
        purpose: str,
        device_id: str,
        device_uuid: str
    ) -> None:
        token_device_id = token_payload.get("device_id") or token_payload.get("android_id")
        token_device_uuid = token_payload.get("device_uuid") or token_payload.get("android_uuid")

        if device_id != token_device_id or device_uuid != token_device_uuid:
            raise HTTPException(status_code=401, detail="Invalid Device")

        if purpose != OTPPurpose.LOGIN.value:
            raise HTTPException(status_code=400, detail="Invalid OTP purpose")

    def send_otp(
        self,
        payload: OTPRequest
    ) -> GlobalResponse:
        try:
            method = self._enum_value(payload.method)
            purpose = self._enum_value(payload.purpose)
            otp_token = payload.otp_token
            device_id = payload.device_id
            device_uuid = payload.device_uuid

            token_payload = self._decode_otp_request_token(otp_token)
            self._validate_otp_request(token_payload, method, purpose, device_id, device_uuid)

            user = self._get_otp_user(token_payload.get("user_id"))
            delever_to = self._get_otp_delivery_address(user, method)

            if not delever_to:
                raise HTTPException(status_code=400, detail="OTP delivery address not found")

            # check otp record
            otp_record = self.db.query(OTPTable).filter(
                OTPTable.otp_token == otp_token
            ).first()

            # delete old otp if exist
            if otp_record:
                self.db.delete(otp_record)
                self.db.flush()

            # genaret OTP
            make_otp = Generators.generate_otp()
            otp_hash = Hashing.create_hash(make_otp)

            # insert otp data
            otp_record = OTPTable(
                user_id=user.user_id,
                otp_token=otp_token,
                device_id=device_id,
                device_uuid=device_uuid,
                delever_to=delever_to,
                otp_hash=otp_hash,
                expires_at=Helpers.utc6dhaka() + timedelta(minutes=5)
            )
            self.db.add(otp_record)

            if ENV.DEBUG:
                print(f"{AnsiColor.BLUE}INFO{AnsiColor.RESET}:     OTP sent to {delever_to} code {make_otp}")

            # send OTP on user
            status = False
            if method == OTPMethod.EMAIL.value:
                notification_service = NotificationServices(
                    self.db,
                    self.background_tasks,
                )
                status = notification_service.send_by_email(
                    to_email=delever_to,
                    subject="Your OTP Code",
                    body=f"Your OTP code is {make_otp}. Please use this code to complete your verification."
                )

                status = True
            elif method == OTPMethod.SMS.value:
                status = True
                # otp_manager = SMSSent()

                # status = otp_manager.send_sms(
                #     to_phone=delever_to,
                #     title="",
                #     body=f"Your OTP code is {make_otp}. Please use this code to complete your verification."
                # )

            # check otp send status
            if not status:
                raise HTTPException(status_code=500, detail="Failed to send OTP")

            self.db.commit()
            self.db.refresh(otp_record)

            return GlobalResponse(
                success=True,
                message="OTP resent successfully",
                data={
                    "otp_token": otp_token,
                    "method": method,
                    "purpose": purpose
                }
            )

        except HTTPException:
            raise

        except Exception as e:
            self.db.rollback()
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    def verify_otp(
        self,
        payload: VerifyOTPRequest
    ) -> GlobalResponse:
        try:
            method: str = self._enum_value(payload.method)
            purpose: str = self._enum_value(payload.purpose)
            otp: str = payload.otp
            otp_token: str = payload.otp_token
            device_id: str = payload.device_id
            device_uuid: str = payload.device_uuid

            ip: str = self.request.client.host

            token_payload = self._decode_otp_request_token(otp_token)
            self._validate_otp_request(token_payload, method, purpose, device_id, device_uuid)
            user = self._get_otp_user(token_payload.get("user_id"))

            if method == OTPMethod.TOTP.value:
                self._verify_totp(user, otp)
            else:
                otp_record = self.db.query(OTPTable).filter(
                    OTPTable.otp_token == otp_token
                ).first()

                if not otp_record:
                    raise HTTPException(status_code=404, detail=String.OTP_NOT_FOUND)

                if otp_record.expires_at and otp_record.expires_at < Helpers.utc6dhaka():
                    self.db.delete(otp_record)
                    self.db.commit()
                    raise HTTPException(status_code=401, detail=String.TIME_LIMET_EXPAIRE)

                if not Hashing.verify_otp(otp, otp_record.otp_hash):
                    raise HTTPException(status_code=401, detail=String.INVALID_OTP)

                expected_delivery_address = self._get_otp_delivery_address(user, method)
                if otp_record.delever_to != expected_delivery_address:
                    raise HTTPException(status_code=400, detail="Invalid OTP method")

                self.db.delete(otp_record)

                if not user.email_verified and method == OTPMethod.EMAIL.value:
                    user.email_verified = True

                if not user.phone_verified and method == OTPMethod.SMS.value:
                    user.phone_verified = True

                self.db.commit()

            access_token = self._create_token(
                data={
                    "user_id": user.user_id,
                    "email_address": user.email_address,
                    "device_id": device_id,
                    "device_uuid": device_uuid
                },
                token_type="access",
                expire_min=ENV.ACCESS_EXPIRE
            )

            refresh_token = self._create_token(
                data={
                    "user_id": user.user_id,
                    "email_address": user.email_address,
                    "device_id": device_id,
                    "device_uuid": device_uuid
                },
                token_type="refresh",
                expire_min=ENV.REFRESH_EXPIRE
            )

            session = self.db.query(SessionTable).filter(
                SessionTable.user_id == user.user_id,
                SessionTable.device_id == device_id,
                SessionTable.device_uuid == device_uuid,
                SessionTable.refresh_token_hash == None,
                SessionTable.is_login == False
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
                self.db.commit()
                self.db.refresh(session)

            return GlobalResponse(
                success=True,
                message="OTP verified successfully",
                data={
                    "user_id": user.user_id,
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_type": "bearer",
                    "expires_in": ENV.ACCESS_EXPIRE,
                    "email_address": user.email_address,
                    "phone_number": user.country_code + user.phone_number
                }
            )

        except HTTPException:
            raise

        except Exception as e:
            self.db.rollback()
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)

    
