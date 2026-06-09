from fastapi import APIRouter, Depends, Request, BackgroundTasks, Header
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.model import AppConfigTable, AdminTable
from app.schema.global_schema import GlobalResponse
from admin.schema.admin_schema import AppConfigRequest
from services.admin.access_services import AdminAccessServices


server_router = APIRouter()


# ============================================================================

@server_router.get("/app-config", response_model=GlobalResponse)
async def get_app_config(
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    adminAccessServices = AdminAccessServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )
    
    return adminAccessServices.get_app_config()


# ============================================================================

@server_router.get("/app-config/{key}", response_model=GlobalResponse)
async def get_config_by_key(
    key: str,
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    adminAccessServices = AdminAccessServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )
    
    return adminAccessServices.get_config_by_key(key=key)


# ============================================================================

@server_router.put("/app-config", response_model=GlobalResponse)
async def update_app_config(
    payload: AppConfigRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    adminAccessServices = AdminAccessServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )
    
    return adminAccessServices.update_app_config(payload=payload)