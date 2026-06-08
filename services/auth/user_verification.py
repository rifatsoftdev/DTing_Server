from fastapi import HTTPException, status, Request, BackgroundTasks
from sqlalchemy.orm import Session
from jose import JWTError

from app.constants import AnsiColor, String

from app.utils.hashing import Hashing
from app.enums import KYCStatus
from app.model import UserTable, SettingsTable, SessionTable, AdminTable, KYCTable

from services.auth.token_service import TokenGenerators



class UserVerificationService(TokenGenerators):
    def __init__(
        self,
        db: Session = None,
        background_tasks: BackgroundTasks = None,
        request: Request = None,
        authorization: str = None
    ):
        self.db = db
        self.background_tasks = background_tasks
        self.request = request
        self.authorization = authorization
        super().__init__()

    def verify_access_token(self, access_token: str, advanced: bool = False) -> str:
        # verify token
        payload = self._decode_token(access_token)

        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=String.INVALID_TOKEN
            )

        if (payload.get("type") != "access"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=String.INVALID_TOKEN_TYPE
            )

        # if payload.get("user_id") != user_id:
        #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=String.INVALID_TOKEN)

        #print(payload.get("user_id"), payload.get("admin_id"))

        return payload.get("user_id") or payload.get("admin_id")
    
    def verify_app_token(self, access_token: str, advanced: bool = False):
        payload = self._decode_token(access_token)

        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid App Token"
            )

        if (payload.get("type") != "app"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=String.INVALID_TOKEN_TYPE
            )

        # if payload.get("user_id") != user_id:
        #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=String.INVALID_TOKEN)
        
        return payload.get("app_id")

    def verify_authorization(self, authorization: str, advanced: bool = False) -> str:
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing Authorization header"
            )

        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format"
            )
        
        # print(authorization.split(" ")[1])
        return self.verify_access_token(authorization.split(" ")[1])

    def verify_user(
        self,
        user_id: str,
        access_token: str,
        device_id: str = None,
        device_uuid: str = None,
        password: str = None,
        advance_check: bool = False,
        db: Session = None,
        android_id: str = None,
        android_uuid: str = None,
    ) -> UserTable:
        
        try:
            db_session = db or self.db
            device_id = device_id or android_id
            device_uuid = device_uuid or android_uuid

            if db_session is None:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=String.SERVER_ERROR
                )

            # fetch user
            user = db_session.query(UserTable).filter(
                UserTable.user_id == user_id
            ).first()
            
            # print(user)
            # print(user_id)

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=String.USER_NOT_FOUND
                )

            user_id = self.verify_access_token(access_token)
            
            if user_id != user.user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=String.INVALID_TOKEN
                )
            
            if (advance_check and not user.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=String.PASSWORD_NOT_SET
                )

            # verify password
            if password:
                if not Hashing.verify_password(password, user.password_hash):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=String.INVALID_PASSWORD
                    )
            
            # fetch settings
            settings = db_session.query(SettingsTable).filter(
                SettingsTable.user_id == user_id
            ).first()

            if not settings:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=String.SETTINGS_NOT_FOUND
                )

            if (settings.account_deactivated):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=String.ACCOUNT_LOCKED
                )

            kyc = db_session.query(KYCTable).filter(
                KYCTable.user_id == user_id
            ).first()

            if (advance_check and (not kyc or kyc.kyc_status != KYCStatus.VERIFIED)):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=String.VERIFY_KYC_FIRST
                )

            # fetch session
            session = db_session.query(SessionTable).filter(
                SessionTable.user_id == user_id,
                SessionTable.device_id == device_id,
                SessionTable.device_uuid == device_uuid,
                SessionTable.is_login == True
            ).first()

            if not session:
                # print(7)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=String.SESSION_NOT_FOUND
                )
            
            if not session.otp_verified:
                # print(8)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=String.OTP_NOT_VERIFIED
                )
            
            if not session.is_login:
                # print(9)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=String.USER_NOT_LOGIN
                )

            return user

        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=String.INVALID_OR_EXPIRED_TOKEN
            )
        
        except HTTPException:
            raise

        except Exception as e:
            # print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=String.SERVER_ERROR
            )
        
    def verify_admin(
        self, 
        user_id: str,
        access_token: str,
        device_id: str,
        device_uuid: str,
        password: str
    ) -> AdminTable:
        try:
            db_session = self.db

            if db_session is None:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=String.SERVER_ERROR
                )

            # fetch admin
            admin = db_session.query(AdminTable).filter(
                AdminTable.admin_id == user_id
            ).first()

            if not admin:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=String.ADMIN_NOT_FOUND
                )

            # verify password
            if not Hashing.verify_password(password, admin.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=String.INVALID_PASSWORD
                )

            # fetch session
            session = db_session.query(AdminSessionTable).filter(
                AdminSessionTable.admin_id == user_id,
                AdminSessionTable.device_id == device_id,
                AdminSessionTable.device_uuid == device_uuid,
                AdminSessionTable.is_login == True
            ).first()

            if not session:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=String.SESSION_NOT_FOUND
                )
            
            if not session.is_login:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=String.ADMIN_NOT_LOGIN
                )

            return admin

        except HTTPException:
            raise

        except Exception as e:
            # print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=String.SERVER_ERROR
            )





# ==============================================================================
# ==============================================================================
