from fastapi import APIRouter, Depends, UploadFile, File, Request, Header, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.core.database import get_db

from app.constants import AnsiColor, String, ENV
from app.schema import GlobalResponse
from services import UserServices
from app.utils import Helpers



me_router = APIRouter()



ALLOWED_TYPES = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
MAX_SIZE = 5 * 1024 * 1024  # 5MB



# ==============================================================================

@me_router.get("/profile", response_model=GlobalResponse)
async def profile(
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    userServices = UserServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return userServices.profile()
    



# ==============================================================================

@me_router.get("/sessions", response_model=GlobalResponse)
async def sessions(
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    userServices = UserServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return userServices.sessions()




# ==============================================================================

@me_router.get("/settings", response_model=GlobalResponse)
async def settings(
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    userServices = UserServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return userServices.settings()   




# ==============================================================================

@me_router.get("/edit-info", response_model=GlobalResponse)
async def edit_info(
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    userServices = UserServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return userServices.edit_info()



# ==============================================================================

@me_router.post("/profile/update")
async def update_profile(
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db),

    user_id: str = Form(...),
    access_token: str = Form(...),
    device_id: str = Form(...),
    device_uuid: str = Form(...),

    full_name: Optional[str] = Form(None),
    gender: Optional[str] = Form(None),
    date_of_birth: Optional[date] = Form(None),
    profile_photo: Optional[UploadFile] = File(None),
    avatar: Optional[UploadFile] = File(None),
    photo: Optional[UploadFile] = File(None),
    file: Optional[UploadFile] = File(None),
    profile_picture: Optional[UploadFile] = File(None)
):
    userServices = UserServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return userServices.update_profile(
        user_id=user_id,
        access_token=access_token,
        device_id=device_id,
        device_uuid=device_uuid,

        full_name=full_name,
        gender=gender,
        date_of_birth=date_of_birth,
        profile_photo=profile_photo or avatar or photo or file or profile_picture
    )




# ==============================================================================

@me_router.post("/kyc/submit")
async def totp_enable(
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db),

    document_type: str = Form(...),
    user_id: str = Form(...),
    access_token: str = Form(...),
    device_id: str = Form(...),
    device_uuid: str = Form(...),

    front_image: UploadFile = File(...),
    back_image: UploadFile = File(...),
    user_face_image: UploadFile = File(...)
):
    userServices = UserServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return userServices.kyc_submit(
        document_type=document_type,
        user_id=user_id,
        access_token=access_token,
        device_id=device_id,
        device_uuid=device_uuid,
        front_image=front_image,
        back_image=back_image,
        user_face_image=user_face_image
    )




# ==============================================================================
# ==============================================================================
