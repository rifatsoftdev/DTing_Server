from fastapi import HTTPException, Request, BackgroundTasks, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import or_
from decimal import Decimal

from app.constants import String, AnsiColor
from app.enums import TransactionType, PaymentMethods, TransactionDirection, TransactionStatus, NotificationType
from app.schema import PaymentRequest, GlobalResponse, GlobalRequest
from app.model import DevTable, UserTable
from app.utils import Generators, Helpers

from services.auth.user_verification import UserVerificationService
from services.notification.noticication_services import NotificationServices, NotificationData


class HistoryServices:
    def __init__(
        self,
        db: Session,
        background_tasks: BackgroundTasks,
        request: Request,
        authorization: str
    ):
        self.db = db
        self.background_tasks = background_tasks
        self.request = request
        self.authorization = authorization
    
    def all_notifications(self, user_id: str) -> GlobalResponse:
        try:
            notifications_list = []

            user: UserTable = self.db.query(UserTable).filter(
                UserTable.user_id == user_id
            ).first()

            for tx in user.notifications:
                notifications_list.append({
                    "id": tx.id,
                    "type": tx.type,
                    "title": tx.title,
                    "body": tx.body,
                    "img_url": tx.img_url,
                    "created_at": tx.created_at.isoformat() if tx.created_at else None,
                    "is_read": tx.is_read
                })

            return GlobalResponse(
                success=True,
                message="All transactions fetched successfully",
                data={
                    "notifications": notifications_list[::-1]
                }
            )
        
        except HTTPException:
            raise

        except Exception as e:
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)

    