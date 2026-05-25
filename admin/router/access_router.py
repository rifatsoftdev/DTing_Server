from fastapi import APIRouter, Depends, Request, Query, BackgroundTasks, Header
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional

from app.core.database import get_db
from app.schema import GlobalResponse, KYCUpdateRequest, AdminNotyfyResuest

from admin.schema.admin_schema import *

from app.services.admin.admin_services import AdminManagementServices
from app.services.admin.access_services import AdminAccessServices



admin_access_router = APIRouter()

today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)




# ==============================================================================

@admin_access_router.get("/dashboard/stats", response_model=GlobalResponse)
async def get_dashboard_stats(
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

    return adminAccessServices.get_dashboard_stats()




# ==============================================================================

@admin_access_router.get("/users-list")
async def list_users(
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db),

    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    kyc_status: Optional[str] = None,
    is_active: Optional[bool] = None,
    sort_by: Optional[str] = Query("created_at", regex="^(created_at|full_name|wallet_balance)$"),
    sort_order: Optional[str] = Query("desc", regex="^(asc|desc)$")
):
    
    adminAccessServices = AdminAccessServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return adminAccessServices.list_users(
        page=page,
        limit=limit,
        search=search,
        kyc_status=kyc_status,
        is_active=is_active,
        sort_by=sort_by,
        sort_order=sort_order
    )




# ==============================================================================

@admin_access_router.get("/transactions-list", response_model=GlobalResponse)
async def list_transactions(
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db),

    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    transaction_id: Optional[str] = None,
    sender_id: Optional[str] = None,
    receiver_id: Optional[str] = None,
    transaction_type: Optional[str] = None,
    status: Optional[str] = None,
    created_from: Optional[datetime] = None,
    created_to: Optional[datetime] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
):
    adminAccessServices = AdminAccessServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return adminAccessServices.list_transactions(
        page=page,
        limit=limit,
        search=search,
        transaction_id=transaction_id,
        sender_id=sender_id,
        receiver_id=receiver_id,
        transaction_type=transaction_type,
        status=status,
        created_from=created_from,
        created_to=created_to,
        min_amount=min_amount,
        max_amount=max_amount
    )




# ==============================================================================

@admin_access_router.get("/transactions/{transaction_id}", response_model=GlobalResponse)
async def get_transaction_details(
    transaction_id: str,
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

    return adminAccessServices.get_transaction_details(transaction_id=transaction_id)




# ==============================================================================

@admin_access_router.post("/transactions/{transaction_id}/cancel", response_model=GlobalResponse)
async def cancel_transaction(
    transaction_id: str,
    payload: TransactionActionRequest,

    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    adminAccessServices = AdminAccessServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return adminAccessServices.cancel_transaction(
        transaction_id=transaction_id,
        payload=payload
    )

 


# ==============================================================================

@admin_access_router.get("/wallets-list", response_model=GlobalResponse)
async def list_wallets(
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db),

    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    min_balance: Optional[float] = None,
    max_balance: Optional[float] = None
):
    adminAccessServices = AdminAccessServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return adminAccessServices.list_wallets(
        page=page,
        limit=limit,
        search=search,
        min_balance=min_balance,
        max_balance=max_balance
    )

    


# ==============================================================================

@admin_access_router.get("/list-kyc-request", response_model=GlobalResponse)
async def list_kyc_request(
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

    return adminAccessServices.list_kyc_request()





# ==============================================================================

@admin_access_router.get("/kyc-request-details/{user_id}", response_model=GlobalResponse)
async def kyc_request_details(
    user_id: str,
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

    return adminAccessServices.kyc_request_details()




# ==============================================================================

@admin_access_router.post("/update-kyc-request", response_model=GlobalResponse)
async def update_kyc_request(
    payload: KYCUpdateRequest,
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

    return adminAccessServices.update_kyc_request(payload=payload)




# ==============================================================================

@admin_access_router.post("/users/{user_id}/notify", response_model=GlobalResponse)
async def notify_user(
    user_id: str,
    payload: AdminNotyfyResuest,

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

    return adminAccessServices.notify_user(user_id=user_id, payload=payload)



# ==============================================================================

@admin_access_router.get("/delete-account-requests-list", response_model=GlobalResponse)
async def list_delete_account_requests(
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db),

    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = Query("pending", regex="^(pending|processed|all)$")
):
    adminAccessServices = AdminAccessServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return adminAccessServices.list_delete_account_requests(
        page=page,
        limit=limit,
        search=search,
        status=status
    )




# ==============================================================================

@admin_access_router.post("/delete-account-requests/{request_id}/approve", response_model=GlobalResponse)
async def approve_delete_account_request(
    request_id: int,
    payload: DeleteAccountReviewRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    adminAccessServices = AdminAccessServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return adminAccessServices.approve_delete_account_request(
        request_id=request_id,
        payload=payload
    )




# ==============================================================================

@admin_access_router.post("/delete-account-requests/{request_id}/reject", response_model=GlobalResponse)
async def reject_delete_account_request(
    request_id: int,
    payload: DeleteAccountReviewRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    adminAccessServices = AdminAccessServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return adminAccessServices.reject_delete_account_request(
        request_id=request_id,
        payload=payload
    )




# ==============================================================================
# ==============================================================================
