from fastapi import APIRouter, Header, Request, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.utils.helpers import Helpers
from app.schema import GlobalResponse



template_router = APIRouter()


template_router.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
TMP_DIR = Path("uploads/tmp")




# ==============================================================================
""" Server Web Page Templates """
# ==============================================================================

# ==============================================================================

@template_router.get("/terms-and-conditions", tags=["UI"], response_class=HTMLResponse)
def terms_page(request: Request):
    """Signup page"""
    return templates.TemplateResponse("server/terms_and_conditions.html", {"request": request})





# ==============================================================================
""" User Web Page Templates """
# ==============================================================================


# ==============================================================================

@template_router.get("/login", tags=["UI"], response_class=HTMLResponse)
def login_page(request: Request):
    """Login page"""
    return templates.TemplateResponse("user/user_login.html", {"request": request})




# ==============================================================================

@template_router.get("/forget-password", tags=["UI"], response_class=HTMLResponse)
def forget_password_page(request: Request):
    """Forget password page"""
    return templates.TemplateResponse("user/forget_password.html", {"request": request})





# ==============================================================================

@template_router.get("/verification", tags=["UI"], response_class=HTMLResponse)
def verification_page(request: Request):
    """Email verification page"""
    return templates.TemplateResponse("user/verification.html", {"request": request})





# ==============================================================================

@template_router.get("/account", tags=["UI"], response_class=HTMLResponse)
def account_page(request: Request):
    """Account management page"""
    return templates.TemplateResponse("account.html", {"request": request})





# ==============================================================================

@template_router.get("/signup", tags=["UI"], response_class=HTMLResponse)
def signup_page(request: Request):
    """Signup page"""
    return templates.TemplateResponse("user/user_signup.html", {"request": request})





# ==============================================================================

@template_router.get("/privacy", tags=["UI"], response_class=HTMLResponse)
def privacy_page(request: Request):
    """Privacy policy page"""
    return templates.TemplateResponse("server/privacy.html", {"request": request})












# ==============================================================================
""" Admin Web Page Templates """
# ==============================================================================



# ==============================================================================

@template_router.get("/admin")
async def admin_dashboard():
    return RedirectResponse("/admin/dashboard")



# ==============================================================================

@template_router.get("/admin/login")
async def admin_login():
    return templates.TemplateResponse("admin/admin_login.html", {"request": {}})



@template_router.get("/admin/dashboard")
async def admin_dashboard(request: Request):
    # Check if admin is logged in via cookie or token
    access_token = request.cookies.get("admin_access_token")
    
    if not access_token:
        # Redirect to login page if not authenticated
        return RedirectResponse("/admin/login")

    # Add token to headers for API calls
    request.headers.__dict__["_list"].append(
        (b"authorization", f"Bearer {access_token}".encode())
    )

    # Render dashboard template
    return templates.TemplateResponse("admin/dashboard.html", {"request": request})




# ==============================================================================

@template_router.get("/admin/users")
async def admin_users(request: Request):
    # Check if admin is logged in via cookie or token
    access_token = request.cookies.get("admin_access_token")

    if not access_token:
        # Redirect to login page if not authenticated
        return RedirectResponse("/admin/login")

    # Add token to headers for API calls
    request.headers.__dict__["_list"].append(
        (b"authorization", f"Bearer {access_token}".encode())
    )

    # Render users template
    return templates.TemplateResponse("admin/users_list.html", {"request": request})




# ==============================================================================

# @template_router.get("/admin/transactions")
# async def admin_transactions(request: Request):
#     # Check if admin is logged in via cookie or token
#     access_token = request.cookies.get("admin_access_token")

#     if not access_token:
#         # Redirect to login page if not authenticated
#         return RedirectResponse("/admin/login")

#     # Add token to headers for API calls
#     request.headers.__dict__["_list"].append(
#         (b"authorization", f"Bearer {access_token}".encode())
#     )

#     # Render transactions template
#     return templates.TemplateResponse("transactions.html", {"request": request})




# ==============================================================================

# @template_router.get("/admin/wallets")
# async def admin_wallets(request: Request):
#     # Check if admin is logged in via cookie or token
#     access_token = request.cookies.get("admin_access_token")

#     if not access_token:
#         # Redirect to login page if not authenticated
#         return RedirectResponse("/admin/login")

#     # Add token to headers for API calls
#     request.headers.__dict__["_list"].append(
#         (b"authorization", f"Bearer {access_token}".encode())
#     )

#     # Render wallets template
#     return templates.TemplateResponse("wallets.html", {"request": request})




# ==============================================================================

# @template_router.get("/admin/donations/create")
# async def admin_donation_create(request: Request):
#     # Check if admin is logged in via cookie or token
#     access_token = request.cookies.get("admin_access_token")

#     if not access_token:
#         # Redirect to login page if not authenticated
#         return RedirectResponse("/admin/login")

#     # Render donation create template
#     return templates.TemplateResponse("donation_manager.html", {"request": request})




# ==============================================================================

@template_router.get("/admin/countries")
async def admin_countries(request: Request):
    # Check if admin is logged in via cookie or token
    access_token = request.cookies.get("admin_access_token")

    if not access_token:
        # Redirect to login page if not authenticated
        return RedirectResponse("/admin/login")

    # Add token to headers for API calls
    request.headers.__dict__["_list"].append(
        (b"authorization", f"Bearer {access_token}".encode())
    )

    return templates.TemplateResponse("admin/country_manage.html", {"request": request})




# ==============================================================================

# @template_router.get("/admin/bill-providers")
# async def admin_bill_providers(request: Request):
#     # Check if admin is logged in via cookie or token
#     access_token = request.cookies.get("admin_access_token")

#     if not access_token:
#         # Redirect to login page if not authenticated
#         return RedirectResponse("/admin/login")

#     # Add token to headers for API calls
#     request.headers.__dict__["_list"].append(
#         (b"authorization", f"Bearer {access_token}".encode())
#     )

#     # Render bill providers template
#     return templates.TemplateResponse("bill_provider.html", {"request": request})




# ==============================================================================

# @template_router.get("/admin/mobile-operators")
# async def admin_mobile_operators(request: Request):
#     # Check if admin is logged in via cookie or token
#     access_token = request.cookies.get("admin_access_token")

#     if not access_token:
#         # Redirect to login page if not authenticated
#         return RedirectResponse("/admin/login")

#     # Add token to headers for API calls
#     request.headers.__dict__["_list"].append(
#         (b"authorization", f"Bearer {access_token}".encode())
#     )

#     # Render mobile operators template
#     return templates.TemplateResponse("mobile_operators.html", {"request": request})




# ==============================================================================

@template_router.get("/admin/offers")
async def admin_offers(request: Request):
    # Check if admin is logged in via cookie or token
    access_token = request.cookies.get("admin_access_token")

    if not access_token:
        # Redirect to login page if not authenticated
        return RedirectResponse("/admin/login")

    # Add token to headers for API calls
    request.headers.__dict__["_list"].append(
        (b"authorization", f"Bearer {access_token}".encode())
    )

    return templates.TemplateResponse("server/offer_manage.html", {"request": request})




# ==============================================================================

@template_router.get("/admin/kyc-requests")
async def admin_kyc_requests(request: Request):
    access_token = request.cookies.get("admin_access_token")

    if not access_token:
        return RedirectResponse("/admin/login")

    request.headers.__dict__["_list"].append(
        (b"authorization", f"Bearer {access_token}".encode())
    )

    return templates.TemplateResponse("admin/kyc_requests.html", {"request": request})




# ==============================================================================

@template_router.get("/admin/delete-account-requests")
async def admin_delete_account_requests(request: Request):
    access_token = request.cookies.get("admin_access_token")

    if not access_token:
        return RedirectResponse("/admin/login")

    request.headers.__dict__["_list"].append(
        (b"authorization", f"Bearer {access_token}".encode())
    )

    return templates.TemplateResponse("admin/delete_account_requests.html", {"request": request})




# ==============================================================================

# @template_router.get("/admin/profile")
# async def admin_profile(request: Request):
#     # Check if admin is logged in via cookie or token
#     access_token = request.cookies.get("admin_access_token")

#     if not access_token:
#         # Redirect to login page if not authenticated
#         return RedirectResponse("/admin/login")

#     # Render profile template
#     return templates.TemplateResponse("profile.html", {"request": request})




# ==============================================================================

# @template_router.get("/admin/admins/create")
# async def admin_create(request: Request):
#     # Check if admin is logged in via cookie or token
#     access_token = request.cookies.get("admin_access_token")

#     if not access_token:
#         # Redirect to login page if not authenticated
#         return RedirectResponse("/admin/login")

#     # Render create admin template
#     return templates.TemplateResponse("admin_create.html", {"request": request})




# ==============================================================================

# @template_router.get("/admin/create")
# async def admin_create_legacy(request: Request):
#     # Legacy GET route to avoid 405 when visiting /admin/create in browser
#     return RedirectResponse("/admin/admins/create")





# ==============================================================================
# ==============================================================================
