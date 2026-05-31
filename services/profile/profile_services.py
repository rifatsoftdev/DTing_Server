from datetime import date
import traceback

from fastapi import BackgroundTasks, Request, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.constants import AnsiColor, String, ENV
from app.model import UserTable, SessionTable, SettingsTable
from app.schema import GlobalResponse



ALLOWED_TYPES = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
MAX_SIZE = 5 * 1024 * 1024  # 5MB



class ProfileServices():
    def __init__(
        self,
        db: Session = None,
        background_tasks: BackgroundTasks = None,
        request: Request = None,
        authorization: str = None
    ):
        self.__db = db
        self.__background_tasks = background_tasks
        self.__request = request
        self.__authorization = authorization
    
    def get_user_data(self, request_state) -> GlobalResponse:
        try:
            # print(request_state)

            user: UserTable = getattr(request_state, "user", None)
            settings: SettingsTable  = getattr(request_state, "settings", None)
            session: SessionTable = getattr(request_state, "session", None)

            print(settings)

            if not user:
                raise HTTPException(status_code=401, detail=String.USER_NOT_LOGIN)

            return GlobalResponse(
                success=True,
                message="Profile fetched successfully",
                data={
                    "profile": {
                        "user_id": user.user_id,
                        "full_name": user.full_name,
                        "email_address": user.email_address,
                        "phone_number": user.phone_number,
                        "country_code": user.country_code,
                        "gender": user.user_gender.value if user.user_gender else None,
                        "user_type": user.user_type.value if user.user_type else None,
                        "date_of_birth": user.date_of_birth.isoformat() if user.date_of_birth else None,
                        "phone_verified": user.phone_verified,
                        "email_verified": user.email_verified,
                        "auth_enabled": user.auth_enabled,
                        "link_google": user.link_google,
                        "profile_picture": user.profile_image_url,
                        "created_at": user.created_at.isoformat() if user.created_at else None
                    },
                    "settings": {
                        "allow_notifications": settings.allow_notifications if settings else None,
                        "email_notifications": settings.email_notifications if settings else None,
                        "sms_notifications": settings.sms_notifications if settings else None,
                        "push_notifications": settings.push_notifications if settings else None,
                        "marketing_emails": settings.marketing_emails if settings else None,
                        "dark_mode": settings.dark_mode if settings else None,
                        "country": settings.country if settings else None,
                        "location": settings.location if settings else None,
                        "language": settings.language if settings else None,
                        "timezone": settings.timezone if settings else None,
                        "date_format": settings.date_format if settings else None,
                        "kyc_status": settings.kyc_status if settings else None,
                        "kyc_verified_by": settings.kyc_verified_by if settings else None,
                        "kyc_verified_at": settings.kyc_verified_at.isoformat() if settings and settings.kyc_verified_at else None,

                        "totp_enabled": settings.totp_enabled if settings else None,
                        "biometric_enabled": settings.biometric_enabled if settings else None,
                        "account_locked": settings.account_locked if settings else None
                    },
                    "session": {
                        "device_type": session.device_type if session else None,
                        "device_name": session.device_name if session else None,
                        "last_ip_address": session.last_ip_address if session else None,
                        "last_seen_at": session.last_seen_at.isoformat() if session and session.last_seen_at else None,
                        "created_at": session.created_at.isoformat() if session and session.created_at else None
                    }
                }
            )
        
        except HTTPException:
            raise

        except Exception as e:
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)

    def update_profile(
        self,
        full_name: str = None,
        gender: str = None,
        date_of_birth: date = None,
        avatar: UploadFile = None,
        photo: UploadFile = None,
        file: UploadFile = None,
        request_state: any = None
    ) -> GlobalResponse:
        try:
            user: UserTable = getattr(request_state, "user", None)
            db = self.__db

            if not user:
                raise HTTPException(status_code=401, detail=String.USER_NOT_LOGIN)
                
            if full_name is not None:
                user.full_name = full_name

            if gender is not None:
                normalized_gender = gender.strip().lower()
                if normalized_gender not in ["male", "female", "other", "undefined"]:
                    raise HTTPException(status_code=400, detail="Invalid gender value")
                user.user_gender = normalized_gender

            if date_of_birth is not None:
                user.date_of_birth = date_of_birth

            upload_file = avatar or photo or file
            upload_field = "avatar" if avatar else ("photo" if photo else ("file" if file else None))

            if upload_file is not None:
                # print(
                #     f"{AnsiColor.BLUE}INFO{AnsiColor.RESET}: upload field={upload_field}, "
                #     f"filename={upload_file.filename}, content_type={upload_file.content_type}"
                # )

                # if upload_file.content_type and upload_file.content_type not in ALLOWED_TYPES:
                #     raise HTTPException(
                #         status_code=400,
                #         detail="Only JPG, PNG, WEBP images allowed"
                #     )

                upload_file.file.seek(0, 2)
                size = upload_file.file.tell()
                upload_file.file.seek(0)

                if size > MAX_SIZE:
                    raise HTTPException(
                        status_code=400,
                        detail="Image size must be under 5MB"
                    )

                try:
                    print(
                        f"{AnsiColor.BLUE}INFO{AnsiColor.RESET}: cloudinary config loaded "
                        f"(cloud_name={bool(ENV.CLOUDINARY_CLOUD_NAME)}, "
                        f"api_key={bool(ENV.CLOUDINARY_API_KEY)}, "
                        f"api_secret={bool(ENV.CLOUDINARY_API_SECRET)}), "
                        f"size={size}"
                    )
                    upload_result = cloudinary.uploader.upload(
                        upload_file.file,
                        folder="uploads/profile",
                        resource_type="image"
                    )
                    print(
                        f"{AnsiColor.BLUE}INFO{AnsiColor.RESET}: cloudinary upload success "
                        f"secure_url={upload_result.get('secure_url')}"
                    )
                except Exception as upload_error:
                    print(f"{AnsiColor.RED}ERROR{AnsiColor.RESET}: Cloudinary upload failed -> {upload_error}")
                    traceback.print_exc()
                    raise HTTPException(
                        status_code=502,
                        detail=f"Cloudinary upload failed: {str(upload_error)}"
                    )

                user.profile_image_url = upload_result.get("secure_url")
                if not user.profile_image_url:
                    raise HTTPException(status_code=502, detail="Cloudinary upload failed: secure_url missing")
            else:
                print(
                    f"{AnsiColor.YELLOW}INFO{AnsiColor.RESET}: no file received in form-data. "
                    "Use one file key: avatar/photo/file"
                )

            db.commit()
            db.refresh(user)

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





# ==============================================================================
# ==============================================================================
        