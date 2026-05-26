from fastapi import APIRouter, Depends, BackgroundTasks, Request, Header
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.constants import AnsiColor, String

from services.auth.user_verification import UserVerificationService
from services.history.history_services import HistoryServices
from app.utils import Helpers

from app.schema.global_schema import GlobalRequest, GlobalResponse



history_router = APIRouter()







# ==============================================================================

@history_router.get("/all-notifications")
@history_router.post("/all-notifications")
async def all_notifications(
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
    authorization: str = Header(None)
):
    access_token = Helpers.authorization(authorization)

    # verify user
    userVerificationService = UserVerificationService(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    user_id: str = userVerificationService.verify_access_token(access_token=access_token)   

    historyServices = HistoryServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )
    
    return historyServices.all_notifications(user_id)






# ==============================================================================
# ==============================================================================
