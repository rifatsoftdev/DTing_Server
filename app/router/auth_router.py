from fastapi import APIRouter, Depends, BackgroundTasks, Header
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from sqlalchemy.orm import Session

from app.core.database import get_db

from app.schema import (
    GlobalResponse, FCMTokenRequest, ForgetPasswordRequest, GoogleLoginRequest,
    LoginRequest, RegisterRequest, OTPRequest, VerifyOTPRequest, LogoutAllRequest,
    ChangePasswordRequest, CancelDeleteAccountRequest, LinkGoogleAccountRequest,
    DeleteAccountRequest, ResetPasswordRequest, LogoutRequest, TOTPSetupRequest,
    AccessTokenRequest, FinalSetupRequest
)
from services import (
    GoogleOauth, TFAServices,
    RegistrationService,
    PasswordService, AccountServices
)




auth_router = APIRouter()





# ==============================================================================

@auth_router.post("/register", response_model=GlobalResponse)
async def register(
    payload: RegisterRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    registrationService = RegistrationService(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return registrationService.register(payload=payload)




# ==============================================================================

@auth_router.post("/google-login")
async def google_login(
    payload: GoogleLoginRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    google0auth = GoogleOauth(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return google0auth.google_login(payload=payload)




# ==============================================================================

@auth_router.post("/login")
async def login(
    payload: LoginRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """User login endpoint."""
    accountServices = AccountServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return accountServices.login(payload=payload)

    


# ==============================================================================

@auth_router.post("/logout")
async def logout(
    payload: LogoutRequest, 
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    accountServices = AccountServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return accountServices.logout(payload=payload)




@auth_router.post("/final-setup", response_model=GlobalResponse)
async def final_setup(
    payload: FinalSetupRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    registrationService = RegistrationService(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return registrationService.final_setup(payload=payload)




# ==============================================================================

@auth_router.post("/send-otp", response_model=GlobalResponse)
async def send_otp(
    payload: OTPRequest, 

    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    accountServices = AccountServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return accountServices.send_otp(payload=payload)




# ==============================================================================

@auth_router.post("/verify-otp", response_model=GlobalResponse)
async def verify_otp(
    payload: VerifyOTPRequest, 
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    accountServices = AccountServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return accountServices.verify_otp(payload=payload)




# ==============================================================================

@auth_router.post("/send-fcm-token")
async def receive_fcm_token(
    payload: FCMTokenRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    accountServices = AccountServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return accountServices.receive_fcm_token(payload=payload)




# ==============================================================================

@auth_router.post("/new-access-token")
async def access_token(
    payload: AccessTokenRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    accountServices = AccountServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return accountServices.get_new_access_token(payload=payload)




# ==============================================================================

@auth_router.post("/reset-password")
def reset_password(
    payload: ForgetPasswordRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    passwordService = PasswordService(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return passwordService.reset_password(payload=payload)




# ==============================================================================

@auth_router.get("/reset-password/{password_token}", response_class=HTMLResponse)
def reset_password_page(
    request: Request, 
    password_token: str,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    passwordService = PasswordService(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return passwordService.reset_password_page(password_token=password_token)




# ==============================================================================

@auth_router.post("/set-password")
def set_password(
    payload: ResetPasswordRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    passwordService = PasswordService(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return passwordService.set_password(payload=payload)




# ==============================================================================

@auth_router.post("/delete-account")
def delete_account(
    payload: DeleteAccountRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    accountServices = AccountServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return accountServices.delete_account(payload=payload)




# ==============================================================================

@auth_router.post("/cancel-delete")
def cancel_delete_account(
    payload: CancelDeleteAccountRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    accountServices = AccountServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return accountServices.cancel_delete_account(payload=payload)




# ==============================================================================

@auth_router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    passwordService = PasswordService(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return passwordService.change_password(payload=payload)




# ==============================================================================

@auth_router.post("/logout-all")
def logout_all(
    payload: LogoutAllRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    accountServices = AccountServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return accountServices.logout_all(payload=payload)




# ==============================================================================

@auth_router.post("/link-google")
def link_google(
    payload: LinkGoogleAccountRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    googleOauth = GoogleOauth()
    return googleOauth.link_google(
        payload=payload,
        request=request,
        background_tasks=background_tasks,
        db=db
    )




# ==============================================================================
# ==============================================================================
