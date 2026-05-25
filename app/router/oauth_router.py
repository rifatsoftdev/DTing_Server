from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from pydantic import EmailStr
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from google.oauth2 import id_token
from google.auth.transport import requests

from app.constants.string import String
from app.constants.colors import AnsiColor
from app.constants.env import ENV

from app.core.database import get_db

from app.enums import NotificationTypeEnum, NotificationCreatorEnum

from app.model.user_table import UserTable
from app.model.otp_table import OTPTable
from app.model.sessions_table import SessionTable
from app.model.settings_table import SettingsTable
from app.model.notification_table import NotificationTable
from app.model.password_reset_table import ResetPasswordTable
from app.model.delete_user_table import DeletedUserTable

from app.schema import GoogleLoginRequest, GlobalResponse

from app.utils import Hashing, Generators, utc6dhaka
from services.auth.token_services import UserTokenService
from services.auth.user_verification import verify_user


oauth_router = APIRouter()




# ==============================================================================

@oauth_router.post("/google-login")
async def google_login(
    payload: GoogleLoginRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    try:
        # get data
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

        # Request info
        ip:str = request.client.host
        user_agent:str = request.headers.get("user-agent")
        auth:str = request.headers.get("authorization")
        path:str = request.url.path
        query:dict = dict(request.query_params)
        cookies:dict = request.cookies

        # print(f"{email_address} {email_verified}")
        if (not email_address or not email_verified):
            raise HTTPException(status_code=404, detail=String.EMAIL_OR_PHONE_REQUIRED)

        # Check if user exists
        existing_user = db.query(UserTable).filter(
            UserTable.email_address == email_address
        ).first()
        created_user = None
        
        if existing_user:
            if existing_user.link_google and existing_user.link_google != google_id:
                raise HTTPException(status_code=409, detail=String.USER_ALRADY_EXISTS)

            if not existing_user.link_google:
                existing_user.link_google = google_id
                db.commit()
                db.refresh(existing_user)

            created_user = existing_user

        # User already exists
        if not existing_user:
            new_user_service = NewUserService(
                full_name=full_name,
                email_address=email_address,
                phone_number=None,
                country_code=None,
                user_password=None,
                profile_image_url=profile_image_url,
                device_id=device_id,
                device_uuid=device_uuid,
                ip=ip,
                db=db,
                background_tasks=background_tasks
            )

            created_user = new_user_service.create_user()
            
            # if (not user):
            #     raise HTTPException(status_code=s)

            # email verified
            created_user.email_verified = True
            db.commit()
            db.refresh(created_user)

        token_service = UserTokenService(
            created_user.user_id,
            email_address=email_address,
            device_id=device_id,
            device_uuid=device_uuid
        )

        # Generate access token
        access_token = token_service.create_access_token()
        # Generate refresh token
        refresh_token = token_service.create_refresh_token()

        # Update session
        session = db.query(SessionTable).filter(
            SessionTable.user_id == created_user.user_id,
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
            session.login_at = utc6dhaka()
            db.commit()
            db.refresh(session)
        else:
            session = SessionTable(
                user_id=created_user.user_id,
                fcm_token=None,
                access_token_hash=Hashing.create_hash(access_token),
                refresh_token_hash=Hashing.create_hash(refresh_token),
                device_uuid=device_uuid,
                device_id=device_id,
                last_ip_address=ip,
                is_login=True,
                otp_verified=True,
            )
            db.add(session)

            # all commit and refresh
            db.commit()
            if created_user:
                db.refresh(created_user)
            db.refresh(session)

        # if (ENV.DEBUG):
        #     print(f"access_token={access_token}, user_id={new_user.user_id}")

        return GlobalResponse(
            success=True,
            message="Login Successful",
            data={
                "user_id": created_user.user_id,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "email_address": created_user.email_address,
                "phone_number": None
            }
        )

    except HTTPException:
        db.rollback()
        raise

    except ValueError:
        db.rollback()
        raise HTTPException(status_code=401, detail=String.INVALID_TOKEN)

    except Exception as e:
        db.rollback()
        print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
        raise HTTPException(status_code=500, detail=String.SERVER_ERROR)





# ==============================================================================

@oauth_router.post("/facebook-login")
async def facebook_login():
    pass
