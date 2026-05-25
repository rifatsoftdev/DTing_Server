import traceback
from typing import Optional

from fastapi import HTTPException, Request, BackgroundTasks, UploadFile, status
from sqlalchemy.orm import Session
from datetime import date, datetime

from app.constants import AnsiColor, String, ENV
from app.enums import KYCStatus
from app.schema import GlobalResponse, KYCRequest
from app.model import SessionTable, UserTable, SettingsTable, KYCTable, TwoFactorTable
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
    
    def get_profile(self):
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

            settings: SettingsTable = user.settings
            user_kyc: KYCTable = user.user_kyc

            # get session detals
            session = self.db.query(SessionTable).filter(SessionTable.user_id == user.user_id).first()
            enabled_tfa_methods = self.db.query(TwoFactorTable).filter(
                TwoFactorTable.user_id == user.user_id,
                TwoFactorTable.is_enabled == True
            ).all()
            two_factor_methods = [
                method.method_type.value if hasattr(method.method_type, "value") else str(method.method_type).lower()
                for method in enabled_tfa_methods
            ]

            return GlobalResponse(
                success=True,
                message="Profile fetched successfully",
                data={
                    "profile": {
                        "user_id": user.user_id,
                        "full_name": user.full_name,
                        "email_address": user.email_address,
                        "phone_number": f"{user.country_code or ''}{user.phone_number or ''}",
                        "country_code": user.country_code,
                        "gender": user.user_gender,
                        "date_of_birth": self._format_date_of_birth(user.date_of_birth),
                        "phone_verified": user.phone_verified,
                        "email_verified": user.email_verified,
                        "link_google": user.link_google,
                        "profile_picture": user.profile_image_url,
                        "created_at": user.created_at.isoformat() if user.created_at else None
                    },
                    "settings": {
                        "allow_notifications": settings.allow_notifications if settings else None,
                        "dark_mode": settings.dark_mode if settings else None,
                        "country": settings.country if settings else None,
                        "language": settings.language if settings else None,

                        "totp_tfa_enabled": "totp" in two_factor_methods,
                        "sms_tfa_enabled": "sms" in two_factor_methods,
                        "email_tfa_enabled": "email" in two_factor_methods,
                        "biometric_enabled": settings.biometric_enabled if settings else None,
                        "account_locked": settings.account_locked if settings else None,

                        "kyc_status": user_kyc.kyc_status if user_kyc else None,
                        "kyc_verified_at": user_kyc.updated_at.isoformat() if user_kyc and user_kyc.updated_at else None
                    },
                    "session": {
                        "device_type": session.device_type if session else None,
                        "device_name": session.device_name if session else None,
                        "last_ip_address": session.last_ip_address if session else None,
                        "login_at": session.login_at.isoformat() if session and session.login_at else None
                    }
                }
            )
        
        except HTTPException:
            raise

        except Exception as e:
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)

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
                success=True,
                message="Profile Edit Info",
                data={
                    "full_name": user.full_name,
                    "gender": user.user_gender,
                    "date_of_birth": self._format_date_of_birth(user.date_of_birth),
                    "profile_picture": user.profile_image_url
                }
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
                success=True,
                message="Profile updated successfully",
                data={
                    "profile_picture": user.profile_image_url
                }
            )
        
        except HTTPException:
            raise

        except Exception as e:
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)

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
            user_id = user_verification_service.verify_access_token(
                access_token=access_token
            )

            user = self.db.query(UserTable).filter(
                UserTable.user_id == user_id
            ).first()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            

            cloudinaryStorage = CloudinaryStorage(db=self.db)

            # Validate file size (5MB limit)
            MAX_SIZE = 5 * 1024 * 1024  # 5MB
            size = 0

            url_results = []
            
            for file in [front_image, back_image, user_face_image]:
                if file.content_type and not file.content_type.startswith("image/"):
                    raise HTTPException(
                        status_code=400,
                        detail="Only image files allowed"
                    )

                # move cursor to end
                file.file.seek(0, 2)
                # get size
                size = file.file.tell()
                # reset cursor
                file.file.seek(0)

                if size > MAX_SIZE:
                    raise HTTPException(
                        status_code=400,
                        detail="Image size must be under 5MB"
                    )
                
                image_url = cloudinaryStorage.upload_file(
                    file_path=file.file,
                    public_id=f"{file.filename}",
                    file_type="image"
                )

                url_results.append(image_url["url"])

            access_token = Helpers.authorization(self.authorization)

            old_kyc = self.db.query(KYCTable).filter(
                KYCTable.user_id == user_id
            ).first()

            if (old_kyc and old_kyc.kyc_status == KYCStatus.VERIFIED.value):
                raise HTTPException(
                    status_code=400,
                    detail="KYC already verified. If you want to update your KYC, please contact support."
                )
            
            elif (old_kyc and old_kyc.kyc_status == KYCStatus.PENDING.value):
                raise HTTPException(
                    status_code=400,
                    detail="KYC already pending. We are reviewing your documents and will update your KYC status accordingly."
                )
            
            elif (old_kyc and old_kyc.kyc_status == KYCStatus.REJECTED.value):
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
                    success=True,
                    message="KYC documents resubmitted successfully. Your KYC status is now pending. We will review your documents and update your KYC status accordingly.",
                    data={
                        "kyc_status": "pending"
                    }
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
                success=True,
                message="KYC documents submitted successfully. Your KYC status is now pending. We will review your documents and update your KYC status accordingly.",
                data={
                    "kyc_status": "pending"
                }
            )
            
        except HTTPException:
            raise
            
        except Exception as e:
            print(f"{AnsiColor.RED}ERROR{AnsiColor.RESET}:     {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)
            

