from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks, Request, Header
from sqlalchemy.orm import Session

from app.constants.colors import AnsiColor
from app.constants.string import String

from app.schema.dev_schema import PaymentRequest
from app.schema.global_schema import GlobalResponse, GlobalRequest

from app.model.dev_table import DevTable

from app.enums.transactions_enum import TransactionType, TransactionStatus, TransactionDirection

from app.utils.generators import Generators
from app.utils.helpers import utc6dhaka
from services.auth.user_verification import UserVerificationService
from services.dev.developer_services import DeveloperServices

from app.core.database import get_db, SessionLocal




dev_router = APIRouter()



# ==============================================================================

@dev_router.post("/make-payment")
def auto_payment(
    payload: PaymentRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    developerServices = DeveloperServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return developerServices.auto_payment(payload=payload)




# ==============================================================================
@dev_router.websocket("/connect/{user_id}")
async def dev_connect(websocket: WebSocket, user_id: str):
    db = SessionLocal()
    try:
        developerServices = DeveloperServices(
            db=db,
            background_tasks=None, # WebSocket connection doesn't need BG tasks
            request=None,
            authorization=None
        )
        await developerServices.dev_connect(websocket=websocket, user_id=user_id)
    finally:
        db.close()




# ==============================================================================
@dev_router.post("/request-developer")
async def request_developer(
    payload: GlobalRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    developerServices = DeveloperServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return developerServices.request_developer(payload=payload)




# ==============================================================================
@dev_router.post("/cancel-developer")
async def cancel_developer(
    payload: GlobalRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    developerServices = DeveloperServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return developerServices.cancel_developer(payload=payload)







# ==============================================================================
# ==============================================================================
