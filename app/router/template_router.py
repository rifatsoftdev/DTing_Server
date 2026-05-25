from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates



template_router = APIRouter()

templates = Jinja2Templates(directory="templates")




# ==============================================================================
# ==============================================================================

@template_router.get("/login", tags=["UI"], response_class=HTMLResponse)
def login_page(request: Request):
    """Login page"""
    return templates.TemplateResponse("login.html", {"request": request})





# ==============================================================================
# ==============================================================================

@template_router.get("/signup", tags=["UI"], response_class=HTMLResponse)
def signup_page(request: Request):
    """Signup page"""
    return templates.TemplateResponse("signup.html", {"request": request})





# ==============================================================================
# ==============================================================================

@template_router.get("/forget-password", tags=["UI"], response_class=HTMLResponse)
def forget_password_page(request: Request):
    """Forget password page"""
    return templates.TemplateResponse("forget.html", {"request": request})





# ==============================================================================
# ==============================================================================

@template_router.get("/verification", tags=["UI"], response_class=HTMLResponse)
def verification_page(request: Request):
    """Email verification page"""
    return templates.TemplateResponse("verification.html", {"request": request})





# ==============================================================================
# ==============================================================================

@template_router.get("/account", tags=["UI"], response_class=HTMLResponse)
def account_page(request: Request):
    """Account management page"""
    return templates.TemplateResponse("account.html", {"request": request})





# ==============================================================================
# ==============================================================================

@template_router.get("/signup", tags=["UI"], response_class=HTMLResponse)
def signup_page(request: Request):
    """Signup page"""
    return templates.TemplateResponse("signup.html", {"request": request})





# ==============================================================================
# ==============================================================================

@template_router.get("/terms", tags=["UI"], response_class=HTMLResponse)
def terms_page(request: Request):
    """Signup page"""
    return templates.TemplateResponse("terms.html", {"request": request})




# ==============================================================================
# ==============================================================================

@template_router.get("/terms", tags=["UI"], response_class=HTMLResponse)
def terms_page(request: Request):
    """Terms of service page"""
    return templates.TemplateResponse("terms.html", {"request": request})




# ==============================================================================
# ==============================================================================

@template_router.get("/privacy", tags=["UI"], response_class=HTMLResponse)
def privacy_page(request: Request):
    """Privacy policy page"""
    return templates.TemplateResponse("privacy.html", {"request": request})
