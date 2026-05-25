from fastapi import APIRouter, Depends, BackgroundTasks, Header
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from sqlalchemy.orm import Session

from app.core.database import get_db

from app.schema import (
    TOTPSetupRequest, TOTPConfirmRequest, TOTPAuthDisableRequest,
    EmailTFASetupRequest, EmailTFAConfirmRequest, EmailTFADisableRequest,
    SMSTFASetupRequest, SMSTFAConfirmRequest, SMSTFADisableRequest,
)
from services import (
    GoogleOauth, TFAServices,
    RegistrationService,
    PasswordService, AccountServices
)



tfa_router = APIRouter()




# ==============================================================================

@tfa_router.post("/totp-tfa-setup")
async def totp_setup(
    payload: TOTPSetupRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    tfaService = TFAServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return tfaService.totp_setup(payload=payload)




# ==============================================================================

@tfa_router.post("/totp-tfa-confirm")
async def totp_confirm(
    payload: TOTPConfirmRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    tfaService = TFAServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return tfaService.totp_confirm(payload=payload)




# ==============================================================================

@tfa_router.post("/totp-tfa-disable")
async def totp_disable(
    payload: TOTPAuthDisableRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    tfaService = TFAServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return tfaService.totp_disable(payload=payload)




# ==============================================================================

@tfa_router.post("/email-tfa-confirm")
async def email_tfa_confirm(
    payload: EmailTFAConfirmRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    tfaService = TFAServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return tfaService.email_confirm(payload=payload)




# ==============================================================================

@tfa_router.post("/email-tfa-disable")
async def email_tfa_disable(
    payload: EmailTFADisableRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    tfaService = TFAServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return tfaService.email_disable(payload=payload)





# ==============================================================================

@tfa_router.post("/sms-tfa-setup")
async def sms_tfa_setup(
    payload: SMSTFASetupRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    tfaService = TFAServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return tfaService.sms_setup(payload=payload)




# ==============================================================================

@tfa_router.post("/sms-tfa-confirm")
async def sms_tfa_confirm(
    payload: SMSTFAConfirmRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    tfaService = TFAServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return tfaService.sms_confirm(payload=payload)




# ==============================================================================

@tfa_router.post("/sms-tfa-disable")
async def sms_tfa_disable(
    payload: SMSTFADisableRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    tfaService = TFAServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return tfaService.sms_disable(payload=payload)




# ==============================================================================
# ==============================================================================
