from typing import Any, Dict

from fastapi import APIRouter, Body, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.model.admin_table import AdminPermissions

from services.settings.settings_services import SettingsServices
from app.schema import GlobalResponse

settings_router = APIRouter()
templates = Jinja2Templates(directory="templates")


@settings_router.get("", response_class=HTMLResponse)
@settings_router.get("/", response_class=HTMLResponse)
async def settings_page(request: Request):
    access_token = request.cookies.get("admin_access_token")

    if not access_token:
        return RedirectResponse("/admin/login")

    request.headers.__dict__["_list"].append(
        (b"authorization", f"Bearer {access_token}".encode())
    )

    return templates.TemplateResponse("settings_manager.html", {"request": request})


@settings_router.get("/settings", response_class=HTMLResponse)
async def legacy_settings_page():
    return RedirectResponse("/admin/settings")


# @settings_router.get(
#     "/fetch",
#     response_model=GlobalResponse,
#     dependencies=[Depends(admin_auth.require_permission(AdminPermissions.CAN_VIEW_SETTINGS))]
# )
# async def fetch_settings(db: Session = Depends(get_db)):
#     return SettingsServices(db).get_settings()


# @settings_router.post(
#     "/update/{key}",
#     response_model=GlobalResponse,
#     dependencies=[Depends(admin_auth.require_permission(AdminPermissions.CAN_EDIT_SETTINGS))]
# )
async def update_setting(
    key: str,
    payload: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    return SettingsServices(db).update_setting(key, payload)
