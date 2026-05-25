from fastapi import FastAPI, Header, Request, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from pathlib import Path

from app.core.database import SessionLocal
from app.constants import ENV
from app.schema.global_schema import GlobalResponse
from app.middleware.auth_middleware import AuthMiddleware


from app.router.auth_router import auth_router
from app.router.country_router import country_router
from app.router.dev_router import dev_router
from app.router.history_router import history_router
from app.router.notify_router import notyfy_router
from app.router.offer_router import offer_router
from app.router.template_router import template_router
from app.router.settings_router import settings_router
from app.router.tfa_router import tfa_router
from app.router.user_router import user_router

from services.setup.setup_services import SetupServices



# create FastAPI
app = FastAPI(
    title="PocketPay API",
    description="A complete digital wallet and payment solution",
    version=ENV.VERSION,
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# 
app.add_middleware(
    AuthMiddleware,
    public_paths=[
        "/country/counties",
    ],
    protected_prefixes=[
        "/bank",
        "/bill",
        "/country",
        "/dev",
        "/donation",
        "/history",
        "/offer",
        "/qr",
        "/recharge",
        "/tfa",
        "/user",
        "/wallet",
    ]
)

# 
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
TMP_DIR = Path("uploads/tmp")

# 
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],
    storage_uri=ENV.REDIS_URL,
    headers_enabled=True,
)


@app.on_event("startup")
def create_default_admin_on_startup():
    db = SessionLocal()
    try:
        setupServices = SetupServices(
            db=db,
            background_tasks=None,
            request=None,
            authorization=None
        )

        if all([ENV.DEFAULT_ADMIN_EMAIL, ENV.DEFAULT_ADMIN_PASSWORD, ENV.DEFAULT_ADMIN_NAME]):
            setupServices.create_default_admin(
                email=ENV.DEFAULT_ADMIN_EMAIL,
                password=ENV.DEFAULT_ADMIN_PASSWORD,
                full_name=ENV.DEFAULT_ADMIN_NAME
            )
        else:
            print("Default admin skipped: DEFAULT_ADMIN_EMAIL, DEFAULT_ADMIN_PASSWORD, or DEFAULT_ADMIN_NAME is missing.")

        setupServices.add_default_countries()

        setupServices.create_default_user(
            email=ENV.DEFAULT_USER_EMAIL,
            password=ENV.DEFAULT_USER_PASSWORD,
            full_name=ENV.DEFAULT_USER_NAME
        )

        setupServices.create_settings()

    finally:
        db.close()




@app.on_event("shutdown")
def shutdown_event():
    print("Shutting down application... Cleaning up resources if needed.")




# Custom exception handlers
@app.exception_handler(404)
async def custom_404_handler(request: Request, exc: HTTPException):
    message = exc.detail if getattr(exc, "detail", None) else "Not Found"

    return HTMLResponse(
        content=templates.get_template("404.html").render(request=request, message=message),
        status_code=status.HTTP_404_NOT_FOUND
    )




# Custom exception handlers
@app.exception_handler(Exception)
async def server_exception_handler(request: Request, exc: Exception):
    return HTMLResponse(
        content=templates.get_template("500.html").render(request=request, message=str(exc)),
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )




# ==============================================================================

@app.get("/")
async def root(
    request: Request,
    authorization: str = Header(None)
):
    # import json
    # firebase_json = json.loads(ENV.POCKETPAY_ADMINSDK)
    # print(firebase_json)

    # Helpers.authorization(authorization)
    # print(Hashing.create_hash("1s22s22p6"))
    return GlobalResponse(
        success=True,
        message="Welcome to PocketPay API",
        data={
            "app": "PocketPay",
            "version": ENV.VERSION,
            "description": "A complete digital wallet and payment solution"
        }
    )




@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/favicon.ico")




# Include routers
# app.include_router(admin_access_router, prefix="/admin", tags=["Admin Management"]) # check
# app.include_router(admin_auth_router, prefix="/admin", tags=["Admin Management"])   # check

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])            # check
app.include_router(country_router, prefix="/country", tags=["Countries"])           # check
app.include_router(dev_router, prefix="/dev", tags=["Development"])                 # check
app.include_router(history_router, prefix="/history", tags=["Transaction History"]) # check
app.include_router(notyfy_router, prefix="/ws", tags=["Notifications"])             # check
app.include_router(offer_router, prefix="/offer", tags=["Offers"])                  # check
app.include_router(template_router, prefix="", tags=["Templates"])                  # check
app.include_router(settings_router, prefix="/admin/settings", tags=["Admin Settings"]) # check
app.include_router(tfa_router, prefix="/tfa", tags=["Two-Factor Authentication"])   # check
app.include_router(user_router, prefix="/user", tags=["User Data"])                 # check




# ==============================================================================
# ==============================================================================
