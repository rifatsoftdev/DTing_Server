from fastapi import APIRouter, Depends, Request, Query, BackgroundTasks, Header
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from admin.schema.admin_schema import *
from app.schema.global_schema import GlobalResponse
from app.services.admin.admin_services import AdminManagementServices



admin_auth_router = APIRouter()




# ==============================================================================

@admin_auth_router.post("/login", response_model=GlobalResponse)
async def admin_login(
    payload: AdminLoginRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    adminManagementServices = AdminManagementServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return adminManagementServices.admin_login(payload=payload)

    


# ==============================================================================

@admin_auth_router.post("/logout")
async def admin_logout(
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    adminManagementServices = AdminManagementServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return adminManagementServices.admin_logout()




# ==============================================================================

@admin_auth_router.post("/refresh", response_model=GlobalResponse)
async def refresh_admin_token(
    payload: AdminRefreshTokenRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    adminManagementServices = AdminManagementServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return adminManagementServices.refresh_admin_token(payload=payload)




# ==============================================================================

@admin_auth_router.get("/profile-data", response_model=GlobalResponse)
async def get_admin_profile(
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    adminManagementServices = AdminManagementServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return adminManagementServices.get_admin_profile()




# ==============================================================================

@admin_auth_router.put("/profile", response_model=GlobalResponse)
async def update_own_profile(
    payload: AdminSelfUpdateRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    adminManagementServices = AdminManagementServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return adminManagementServices.update_own_profile(payload=payload)




# ==============================================================================

@admin_auth_router.post("/create", response_model=GlobalResponse)
async def create_admin(
    payload: AdminCreateRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    adminManagementServices = AdminManagementServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return adminManagementServices.create_admin(payload=payload)




# ==============================================================================

@admin_auth_router.get("/list", response_model=GlobalResponse)
async def list_admins(
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db),

    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    role: Optional[AdminRoleEnum] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
):
    adminManagementServices = AdminManagementServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return adminManagementServices.update_own_profile(
        page=page,
        limit=limit,
        role=role,
        is_active=is_active,
        search=search 
    )




# ==============================================================================

@admin_auth_router.put("/{admin_id}", response_model=GlobalResponse)
async def update_admin(
    admin_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    adminManagementServices = AdminManagementServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return adminManagementServices.update_admin(admin_id=admin_id)




# ==============================================================================

@admin_auth_router.post("/{admin_id}/reset-password", response_model=GlobalResponse)
async def reset_admin_password(
    payload: AdminPasswordUpdateRequest,

    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    adminManagementServices = AdminManagementServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return adminManagementServices.reset_admin_password(payload=payload)




# ==============================================================================

@admin_auth_router.delete("/{admin_id}", response_model=GlobalResponse)
async def delete_admin(
    admin_id: str,

    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    adminManagementServices = AdminManagementServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return adminManagementServices.delete_admin(admin_id=admin_id)




# ==============================================================================

@admin_auth_router.post("/change-password", response_model=GlobalResponse)
async def change_own_password(
    payload: AdminPasswordUpdateRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    adminManagementServices = AdminManagementServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return adminManagementServices.change_own_password(payload=payload)
    



# ==============================================================================

@admin_auth_router.get("/users/{user_id}", response_model=GlobalResponse)
async def get_user_details(
    user_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    adminManagementServices = AdminManagementServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return adminManagementServices.get_user_details(user_id=user_id)

    


# ==============================================================================
# ==============================================================================
