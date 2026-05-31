import traceback
from typing import Any, Dict, Optional

from fastapi import HTTPException, Request, BackgroundTasks, UploadFile, status
from sqlalchemy.orm import Session
from datetime import date, datetime

from app.constants import AnsiColor, String, ENV
from app.enums import KYCStatus
from app.schema import GlobalResponse
from app.model import SessionTable, UserTable, SettingsTable, KYCTable
from app.utils import Helpers

from services.auth.user_verification import UserVerificationService
from app.utils.cloudinary_storage import CloudinaryStorage



ALLOWED_TYPES = ["image/*", "image/jpeg", "image/jpg", "image/png", "image/webp"]
MAX_SIZE = 5 * 1024 * 1024  # 5MB


class UserServices:
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
    def _format_date_of_birth(value):
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.date().isoformat()
        if isinstance(value, date):
            return value.isoformat()
        return str(value).split("T", 1)[0].split(" ", 1)[0]

    @staticmethod
    def _enum_value(value):
        return value.value if hasattr(value, "value") else value

    @staticmethod
    def _serialize_settings(settings: SettingsTable | None):
        return {
            column.name: (
                getattr(settings, column.name).isoformat()
                if settings and isinstance(getattr(settings, column.name), datetime)
                else getattr(settings, column.name, None)
            )
            for column in SettingsTable.__table__.columns
        }

    @staticmethod
    def _normalize_setting_value(value: Any) -> Any:
        if isinstance(value, str):
            return value.strip()
        return value

    @staticmethod
    def _serialize_session(session: SessionTable | None):
        if not session:
            return None

        return {
            "id": session.id,
            "session_id": session.session_id,
            "device_id": session.device_id,
            "device_uuid": session.device_uuid,
            "device_type": session.device_type,
            "device_name": session.device_name,
            "last_ip_address": session.last_ip_address,
            "otp_verified": session.otp_verified,
            "is_login": session.is_login,
            "last_seen_at": session.last_seen_at.isoformat() if session.last_seen_at else None,
            "login_at": session.login_at.isoformat() if session.login_at else None,
            "logout_at": session.logout_at.isoformat() if session.logout_at else None
        }


    # a function of get user profile information
    def get_profile(self):
        try:
            # Step 1: Extract and validate access token
            userVerificationService = UserVerificationService(
                db=self.db,
                background_tasks=self.background_tasks,
                request=self.request,
                authorization=self.authorization
            )
            user_id: str = userVerificationService.verify_authorization(authorization=self.authorization)

            # Step 2: Fetch user profile data
            user = self.db.query(UserTable).filter(
                UserTable.user_id == user_id
            ).first()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=String.USER_NOT_FOUND
                )

            # Step 3: Return profile response
            return GlobalResponse(
                status_code=status.HTTP_200_OK,
                success=True,
                action="profile_fetched",
                message="Profile fetched successfully",
                data={
                    "profile": {
                        "full_name": user.full_name,
                        "username": user.username or "null",
                        "email_address": user.email_address,
                        "phone_number": f"{user.country_code or ''}{user.phone_number or ''}",
                        "country_code": user.country_code,
                        "gender": self._enum_value(user.user_gender),
                        "date_of_birth": self._format_date_of_birth(user.date_of_birth),
                        "phone_verified": user.phone_verified,
                        "email_verified": user.email_verified,
                        "link_google": user.link_google,
                        "profile_picture": user.profile_image_url,
                        "created_at": user.created_at.isoformat() if user.created_at else None
                    }
                }
            )
        
        except HTTPException:
            raise

        except Exception as e:
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)


    # a function to get user settings information
    def get_settings(self) -> GlobalResponse:
        try:
            # Step 1: Extract and validate access token
            userVerificationService = UserVerificationService(
                db=self.db,
                background_tasks=self.background_tasks,
                request=self.request,
                authorization=self.authorization
            )
            user_id: str = userVerificationService.verify_authorization(authorization=self.authorization)

            # Step 2: Fetch user settings data
            user = self.db.query(UserTable).filter(
                UserTable.user_id == user_id
            ).first()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=String.USER_NOT_FOUND
                )

            settings: SettingsTable = user.settings

            if not settings:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=String.SETTINGS_NOT_FOUND
                )

            # Stap 3: Return settings response
            return GlobalResponse(
                status_code=status.HTTP_200_OK,
                success=True,
                action="settings_fetched",
                message="Settings fetched successfully",
                data={
                    "settings": self._serialize_settings(settings)
                },
                next_step={}
            )
        
        except HTTPException:
            raise

        except Exception as e:
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)

    def get_me(self) -> GlobalResponse:
        try:
            userVerificationService = UserVerificationService(
                db=self.db,
                background_tasks=self.background_tasks,
                request=self.request,
                authorization=self.authorization
            )
            user_id: str = userVerificationService.verify_authorization(authorization=self.authorization)

            user = self.db.query(UserTable).filter(
                UserTable.user_id == user_id
            ).first()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=String.USER_NOT_FOUND
                )

            current_session = self.db.query(SessionTable).filter(
                SessionTable.user_id == user_id,
                SessionTable.is_login == True
            ).order_by(SessionTable.login_at.desc()).first()

            kyc = self.db.query(KYCTable).filter(
                KYCTable.user_id == user_id
            ).first()

            return GlobalResponse(
                status_code=status.HTTP_200_OK,
                success=True,
                action="me_fetched",
                message="User data fetched successfully",
                data={
                    "profile": {
                        "user_id": user.user_id,
                        "full_name": user.full_name,
                        "username": user.username,
                        "email_address": user.email_address,
                        "phone_number": f"{user.country_code or ''}{user.phone_number or ''}",
                        "country_code": user.country_code,
                        "gender": self._enum_value(user.user_gender),
                        "date_of_birth": self._format_date_of_birth(user.date_of_birth),
                        "phone_verified": user.phone_verified,
                        "email_verified": user.email_verified,
                        "profile_picture": user.profile_image_url,
                        "created_at": user.created_at.isoformat() if user.created_at else None
                    },
                    "settings": self._serialize_settings(user.settings),
                    "session": self._serialize_session(current_session),
                    "kyc": self._serialize_kyc(kyc)
                }
            )

        except HTTPException:
            raise

        except Exception as e:
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)


    def update_settings(self, payload: Dict[str, Any]) -> GlobalResponse:
        try:
            userVerificationService = UserVerificationService(
                db=self.db,
                background_tasks=self.background_tasks,
                request=self.request,
                authorization=self.authorization
            )
            user_id: str = userVerificationService.verify_authorization(authorization=self.authorization)

            settings = self.db.query(SettingsTable).filter(
                SettingsTable.user_id == user_id
            ).first()

            if not settings:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=String.SETTINGS_NOT_FOUND
                )

            blocked_fields = {
                "user_id",
                "account_deactivated",
                "deactivated_at",
                "last_password_changed_at",
                "biometric_enabled_at",
                "biometric_secret",
                "created_at",
                "updated_at"
            }
            allowed_fields = {
                column.name
                for column in SettingsTable.__table__.columns
                if column.name not in blocked_fields
            }

            update_data = {
                key: self._normalize_setting_value(value)
                for key, value in payload.items()
                if key in allowed_fields
            }

            invalid_fields = sorted(set(payload.keys()) - allowed_fields - blocked_fields)
            if invalid_fields:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid settings field(s): {', '.join(invalid_fields)}"
                )

            if not update_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No settings data provided"
                )

            for field, value in update_data.items():
                setattr(settings, field, value)

            self.db.commit()
            self.db.refresh(settings)

            return GlobalResponse(
                status_code=status.HTTP_200_OK,
                success=True,
                action="settings_updated",
                message="Settings updated successfully",
                data={"settings": self._serialize_settings(settings)},
                next_step={}
            )

        except HTTPException:
            self.db.rollback()
            raise

        except Exception as e:
            self.db.rollback()
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)


    # a function to get user session information
    def get_sessions(
        self,
        start: int = 0,
        end: int = 5
    ) -> GlobalResponse:
        try:
            if start < 0 or end < 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="start and end must be greater than or equal to 0"
                )

            if end <= start:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="end must be greater than start"
                )

            access_token = Helpers.authorization(self.authorization)

            # verify user
            user_verification_service = UserVerificationService(
                db=self.db,
                background_tasks=self.background_tasks,
                request=self.request,
                authorization=self.authorization
            )
            user_id = user_verification_service.verify_access_token(
                access_token=access_token
            )

            query = self.db.query(SessionTable).filter(
                SessionTable.user_id == user_id
            ).order_by(SessionTable.id.asc())

            total = query.count()
            sessions = query.offset(start).limit(end - start).all()
            data = {
                "start": start,
                "end": end,
                "count": len(sessions),
                "total": total,
                "sessions": [
                    self._serialize_session(session)
                    for session in sessions
                ]
            }


            return GlobalResponse(
                status_code=status.HTTP_200_OK,
                success=True,
                action="sessions_fetched",
                message="Sessions fetched successfully",
                data=data,
                next_step={}
            )
        
        except HTTPException:
            raise

        except Exception as e:
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)


    # a function to get user edit information
    def edit_info(self):
        try:
            # print(f"Profile attempt: {request}")
            
            access_token = Helpers.authorization(self.authorization)

            # verify user
            user_verification_service = UserVerificationService(
                db=self.db,
                background_tasks=self.background_tasks,
                request=self.request,
                authorization=self.authorization
            )
            user_id = user_verification_service.verify_access_token(
                access_token=access_token
            )

            user = self.db.query(UserTable).filter(
                UserTable.user_id == user_id
            ).first()

            return GlobalResponse(
                status_code=status.HTTP_200_OK,
                success=True,
                action="profile_edit_info_fetched",
                message="Profile Edit Info",
                data={
                    "full_name": user.full_name,
                    "gender": self._enum_value(user.user_gender),
                    "date_of_birth": self._format_date_of_birth(user.date_of_birth),
                    "profile_picture": user.profile_image_url
                },
                next_step={}
            )
        
        except HTTPException:
            raise

        except Exception as e:
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)
    
    def update_profile(
        self,
        user_id: str,
        access_token: str,
        device_id: str,
        device_uuid: str,
        full_name: Optional[str] = None,
        gender: Optional[str] = None,
        date_of_birth: Optional[date] = None,
        profile_photo: Optional[UploadFile] = None
    ) -> GlobalResponse:
        try:
            print(
                f"{AnsiColor.BLUE}INFO{AnsiColor.RESET}: /profile/update content-type="
                f"{self.request.headers.get('content-type')}"
            )

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
                device_id=device_id,
                device_uuid=device_uuid,
                password=None,
                advance_check=False
            )

            if full_name is not None:
                user.full_name = full_name

            if gender is not None:
                normalized_gender = gender.strip().lower()
                if normalized_gender not in ["male", "female", "other", "undefined"]:
                    raise HTTPException(status_code=400, detail="Invalid gender value")
                user.user_gender = normalized_gender

            if date_of_birth is not None:
                user.date_of_birth = date_of_birth

            if profile_photo is not None:
                print(
                    f"{AnsiColor.BLUE}INFO{AnsiColor.RESET}: profile photo received "
                    f"filename={profile_photo.filename}, content_type={profile_photo.content_type}"
                )

                if profile_photo.content_type and profile_photo.content_type not in ALLOWED_TYPES:
                    raise HTTPException(
                        status_code=400,
                        detail="Only JPG, PNG, WEBP images allowed"
                    )

                profile_photo.file.seek(0, 2)
                size = profile_photo.file.tell()
                profile_photo.file.seek(0)

                if size > MAX_SIZE:
                    raise HTTPException(
                        status_code=400,
                        detail="Image size must be under 5MB"
                    )

                try:
                    cloudinaryStorage = CloudinaryStorage(db=self.db)

                    upload_result = cloudinaryStorage.upload_file(
                        file_path=profile_photo.file,
                        public_id=f"{user.user_id}/profile_photo",
                        file_type="image"
                    )
                    uploaded_url = upload_result.get("secure_url") or upload_result.get("url")
                    print(
                        f"{AnsiColor.BLUE}INFO{AnsiColor.RESET}: cloudinary upload success "
                        f"secure_url={uploaded_url}"
                    )
                except Exception as upload_error:
                    print(f"{AnsiColor.RED}ERROR{AnsiColor.RESET}: Cloudinary upload failed -> {upload_error}")
                    traceback.print_exc()
                    raise HTTPException(
                        status_code=502,
                        detail=f"Cloudinary upload failed: {str(upload_error)}"
                    )

                user.profile_image_url = upload_result.get("secure_url") or upload_result.get("url")

                if not user.profile_image_url:
                    raise HTTPException(status_code=502, detail="Cloudinary upload failed: image URL missing")
            else:
                print(
                    f"{AnsiColor.YELLOW}INFO{AnsiColor.RESET}: no profile photo received. "
                    "Use one file key: profile_photo/avatar/photo/file/profile_picture"
                )

            self.db.commit()
            self.db.refresh(user)

            return GlobalResponse(
                status_code=status.HTTP_200_OK,
                success=True,
                action="profile_updated",
                message="Profile updated successfully",
                data={
                    "profile_picture": user.profile_image_url
                },
                next_step={}
            )
        
        except HTTPException:
            raise

        except Exception as e:
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)

    @staticmethod
    def _serialize_kyc(kyc: KYCTable | None) -> dict:
        if not kyc:
            return {
                "status": "not_submitted",
                "document_type": None,
                "rejection_reason": None,
                "submitted_at": None,
                "updated_at": None
            }

        return {
            "status": kyc.kyc_status.value if hasattr(kyc.kyc_status, "value") else kyc.kyc_status,
            "document_type": kyc.document_type,
            "rejection_reason": kyc.rejection_reason,
            "submitted_at": kyc.created_at.isoformat() if kyc.created_at else None,
            "updated_at": kyc.updated_at.isoformat() if kyc.updated_at else None
        }

    def get_kyc_status(self) -> GlobalResponse:
        try:
            userVerificationService = UserVerificationService(
                db=self.db,
                background_tasks=self.background_tasks,
                request=self.request,
                authorization=self.authorization
            )
            user_id: str = userVerificationService.verify_authorization(authorization=self.authorization)

            kyc = self.db.query(KYCTable).filter(
                KYCTable.user_id == user_id
            ).first()

            return GlobalResponse(
                status_code=status.HTTP_200_OK,
                success=True,
                action="kyc_status_fetched",
                message="KYC status fetched successfully",
                data={"kyc": self._serialize_kyc(kyc)},
                next_step={}
            )

        except HTTPException:
            raise

        except Exception as e:
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)

    # a function to submit kyc information
    def kyc_submit(
        self,
        document_type: str,
        user_id: str,
        access_token: str,
        device_id: str,
        device_uuid: str,
        front_image: UploadFile,
        back_image: UploadFile,
        user_face_image: UploadFile
    ):
        try:
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
                device_id=device_id,
                device_uuid=device_uuid,
                password=None,
                advance_check=False
            )

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            old_kyc = self.db.query(KYCTable).filter(
                KYCTable.user_id == user.user_id
            ).first()

            old_status = self._enum_value(old_kyc.kyc_status) if old_kyc else None
            if old_status == KYCStatus.VERIFIED.value:
                raise HTTPException(
                    status_code=400,
                    detail="KYC already verified. If you want to update your KYC, please contact support."
                )

            elif old_status == KYCStatus.PENDING.value:
                raise HTTPException(
                    status_code=400,
                    detail="KYC already pending. We are reviewing your documents and will update your KYC status accordingly."
                )

            cloudinaryStorage = CloudinaryStorage(db=self.db)
            url_results = []

            for file in [front_image, back_image, user_face_image]:
                if file.content_type and not file.content_type.startswith("image/"):
                    raise HTTPException(
                        status_code=400,
                        detail="Only image files allowed"
                    )

                file.file.seek(0, 2)
                size = file.file.tell()
                file.file.seek(0)

                if size > MAX_SIZE:
                    raise HTTPException(
                        status_code=400,
                        detail="Image size must be under 5MB"
                    )

                image_url = cloudinaryStorage.upload_file(
                    file_path=file.file,
                    public_id=f"{user.user_id}/kyc/{file.filename}",
                    file_type="image"
                )

                url_results.append(image_url.get("secure_url") or image_url.get("url"))
            
            if old_status == KYCStatus.REJECTED.value:
                # update kyc info
                old_kyc.document_type = document_type
                old_kyc.front_image_url = url_results[0]
                old_kyc.back_image_url = url_results[1]
                old_kyc.user_face_image_url = url_results[2]
                old_kyc.kyc_status = KYCStatus.PENDING.value
                old_kyc.updated_at = datetime.utcnow()

                self.db.commit()
                self.db.refresh(old_kyc)

                return GlobalResponse(
                    status_code=status.HTTP_200_OK,
                    message="KYC documents resubmitted successfully. Your KYC status is now pending. We will review your documents and update your KYC status accordingly.",
                    data={
                        "kyc_status": "pending"
                    },
                    next_step={}
                )

            # update user kyc info
            user_kyc = KYCTable(
                user_id=user.user_id,
                document_type=document_type,
                front_image_url=url_results[0],
                back_image_url=url_results[1],
                user_face_image_url=url_results[2]
            )

            self.db.add(user_kyc)
            self.db.commit()
            self.db.refresh(user_kyc)

            return GlobalResponse(
                status_code=status.HTTP_200_OK,
                message="KYC documents submitted successfully. Your KYC status is now pending. We will review your documents and update your KYC status accordingly.",
                action="kyc_submitted",
                data={
                    "kyc_status": "pending"
                },
                next_step={}
            )
            
        except HTTPException:
            raise
            
        except Exception as e:
            print(f"{AnsiColor.RED}ERROR{AnsiColor.RESET}:     {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)
            





# ==============================================================================
# ==============================================================================
