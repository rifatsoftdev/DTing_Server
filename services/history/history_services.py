from fastapi import HTTPException, Request, BackgroundTasks, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from decimal import Decimal

from app.constants import String, AnsiColor
from app.enums import TransactionType, PaymentMethods, TransactionDirection, TransactionStatus, NotificationType
from app.schema import PaymentRequest, GlobalResponse, GlobalRequest
from app.model import DevTable, NotificationTable, UserTable
from app.utils import Generators, Helpers

from services.auth.user_verification import UserVerificationService
from services.notification.notification_services import NotificationServices


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
                    "created_at": tx.created_at.strftime("%Y:%m:%d %I:%M:%S %p") if tx.created_at else None,
                    "is_read": tx.is_read
                })

            return GlobalResponse(
                status_code=status.HTTP_200_OK,
                success=True,
                action="fetch_notifications",
                message="All transactions fetched successfully",
                data={
                    "notifications": notifications_list[::-1]
                },
                next_step={}
            )
        
        except HTTPException:
            raise

        except Exception as e:
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)

    def mark_notification_read(self, user_id: str, notification_id: int) -> GlobalResponse:
        try:
            notification: NotificationTable = self.db.query(NotificationTable).filter(
                NotificationTable.id == notification_id,
                NotificationTable.target_id == user_id
            ).first()

            if not notification:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Notification not found"
                )

            notification.is_read = True
            notification.read_at = Helpers.utc6dhaka()

            self.db.commit()
            self.db.refresh(notification)

            return GlobalResponse(
                status_code=status.HTTP_200_OK,
                success=True,
                action="mark_notification_read",
                message="Notification marked as read successfully",
                data={
                    "notification_id": notification.id,
                    "is_read": notification.is_read,
                    "read_at": notification.read_at.strftime("%Y:%m:%d %I:%M:%S %p") if notification.read_at else None
                },
                next_step={}
            )

        except HTTPException:
            raise

        except Exception as e:
            self.db.rollback()
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)

    



# ==============================================================================
# ==============================================================================
