from fastapi import BackgroundTasks, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, desc
from datetime import timedelta
from typing import Optional
from decimal import Decimal
from datetime import datetime, timezone, timedelta


from app.constants import AnsiColor, String
from app.enums import NotificationType, NotificationCreator, TransactionStatus, KYCStatus
from app.model import (
    DeletedUserTable, NotificationTable, SettingsTable,
    AdminTable, UserTable, KYCTable
)
from app.schema import GlobalResponse, KYCUpdateRequest, AdminNotyfyResuest
from app.utils import Helpers, Generators, Hashing

from admin.schema.admin_schema import *

from app.model.admin_table import AdminRole
from services.auth.user_verification import UserVerificationService
from services.notification.notification_services import NotificationData, NotificationServices
from app.schema.auth_schemas import DeleteAccountRequest
from services.auth.user_verification import UserVerificationService


today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)


class AdminAccessServices(UserVerificationService):
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
    
    def get_dashboard_stats(self) -> GlobalResponse:
        try:
            # Basic counts
            total_users = self.db.query(UserTable).count()

            active_users = self.db.query(SettingsTable).filter(
                SettingsTable.account_locked == False
            ).count()
            
            deactive_user = total_users - active_users
            # Today's stats
            new_users_today = self.db.query(UserTable).filter(
                UserTable.created_at >= today_start
            ).count()
            
            # Transaction stats
            total_transactions = self.db.query(TransactionTable).count()
            total_tx_amount = self.db.query(func.sum(TransactionTable.amount)).scalar() or 0
            total_profite = self.db.query(func.sum(TransactionTable.service_charge)).scalar() or 0
            transactions_today = self.db.query(TransactionTable).filter(
                TransactionTable.created_at >= today_start
            ).count()

            status_counts = {
                "pending": self.db.query(TransactionTable).filter(TransactionTable.status == TransactionStatus.PENDING.value).count(),
                "success": self.db.query(TransactionTable).filter(TransactionTable.status == TransactionStatus.SUCCESS.value).count(),
                "failed": self.db.query(TransactionTable).filter(TransactionTable.status == TransactionStatus.FAILED.value).count(),
                "cancelled": self.db.query(TransactionTable).filter(TransactionTable.status == TransactionStatus.CANCELLED.value).count(),
                "refunded": self.db.query(TransactionTable).filter(TransactionTable.status == TransactionStatus.REFUNDED.value).count(),
            }


            # Wallet balance
            total_wallets_balance = self.db.query(func.sum(WalletTable.balance)).scalar() or 0
            
            amount_today = self.db.query(func.sum(TransactionTable.amount)).filter(
                TransactionTable.created_at >= today_start
            ).scalar() or 0

            # Recent activity
            recent_transactions = self.db.query(TransactionTable).order_by(
                desc(TransactionTable.created_at
            )).limit(5).all()
            recent_users = self.db.query(UserTable).order_by(desc(
                UserTable.created_at
            )).limit(5).all()
            
            # print(f"{total_users} {active_users} {total_transactions} {total_tx_amount} {total_wallets_balance} {new_users_today} {transactions_today} {amount_today}")
            
            return GlobalResponse(
                success=True,
                message="Dashboard statistics retrieved successfully",
                data={
                    "total_users": total_users,
                    "active_users": active_users,
                    "deactive_user": deactive_user,
                    "new_users_today": new_users_today,
                    "total_profite": float(total_profite),
                    "total_transactions": total_transactions,
                    "total_transaction_amount": float(total_tx_amount),
                    "total_wallets_balance": float(total_wallets_balance),
                    "transactions_today": transactions_today,
                    "amount_today": float(amount_today),
                    "status_counts": status_counts,
                    "recent_transactions": [
                        {
                            "transaction_id": tx.transaction_id,
                            "transaction_type": str(tx.transaction_type),
                            "amount": float(tx.amount),
                            "currency": tx.currency,
                            "status": str(tx.status),
                            "created_at": tx.created_at
                        } for tx in recent_transactions
                    ],
                    "recent_users": [
                        {
                            "user_id": user.user_id,
                            "full_name": user.full_name,
                            "email": user.email_address,
                            "phone": user.country_code+user.phone_number if (user.country_code and user.phone_number) else "None",
                            "created_at": user.created_at
                        } for user in recent_users
                    ]
                }
            )
            
        except HTTPException:
            raise

        except Exception as e:
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    def list_users(
        self,
        page: int,
        limit: int,
        search: Optional[str] = None,
        kyc_status: Optional[str] = None,
        is_active: Optional[bool] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> GlobalResponse:
        try:
            # Build query with joins
            query = self.db.query(UserTable).join(SettingsTable).join(WalletTable).outerjoin(KYCTable)
            
            # Apply filters
            if search:
                query = query.filter(
                    or_(
                        UserTable.full_name.ilike(f"%{search}%"),
                        UserTable.email_address.ilike(f"%{search}%"),
                        UserTable.phone_number.ilike(f"%{search}%"),
                        UserTable.user_id.ilike(f"%{search}%")
                    )
                )
            if kyc_status:
                query = query.filter(KYCTable.kyc_status == kyc_status)
                
            if is_active is not None:
                query = query.filter(SettingsTable.account_locked == (not is_active))
            
            # Get total count
            total = query.count()
            
            # Apply sorting
            if sort_by == "created_at":
                sort_column = UserTable.created_at
            elif sort_by == "full_name":
                sort_column = UserTable.full_name
            elif sort_by == "wallet_balance":
                sort_column = WalletTable.balance
            
            if sort_order == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(sort_column)
            
            # Apply pagination
            offset = (page - 1) * limit
            users = query.offset(offset).limit(limit).all()
            
            # Format response
            user_list = []
            for user in users:
                wallet = self.db.query(WalletTable).filter(WalletTable.user_id == user.user_id).first()
                settings = self.db.query(SettingsTable).filter(SettingsTable.user_id == user.user_id).first()
                kyc = self.db.query(KYCTable).filter(KYCTable.user_id == user.user_id).first()

                phone = (
                    f"{user.country_code or ''}{user.phone_number}"
                    if user.phone_number
                    else None
                )

                user_list.append({
                    "user_id": user.user_id,
                    "full_name": user.full_name,
                    "email": user.email_address,
                    "phone": phone,
                    "profile_image_url": user.profile_image_url,
                    "phone_verified": user.phone_verified,
                    "email_verified": user.email_verified,
                    "kyc_status": kyc.kyc_status if kyc else "pending",
                    "is_active": not settings.account_locked if settings else False,
                    "wallet_balance": float(wallet.balance) if wallet else 0,
                    "wallet_currency": wallet.currency if wallet else "BDT",
                    "created_at": user.created_at
                })
            
            return GlobalResponse(
                success=True,
                message="Users retrieved successfully",
                data={"users": user_list},
                pagination={
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "total_pages": (total + limit - 1) // limit
                }
            )
            
        except HTTPException:
            raise

        except Exception as e:
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    def list_transactions(
        self,
        page: int,
        limit: int,
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
    ) -> GlobalResponse:
        try:
            query = self.db.query(TransactionTable)
            
            # Apply filters
            if search:
                query = query.filter(
                    or_(
                        TransactionTable.transaction_id.ilike(f"%{search}%"),
                        TransactionTable.sender_user_id.ilike(f"%{search}%"),
                        TransactionTable.receiver_user_id.ilike(f"%{search}%"),
                        TransactionTable.reference.ilike(f"%{search}%"),
                        TransactionTable.account_name.ilike(f"%{search}%")
                    )
                )
            if transaction_id:
                query = query.filter(TransactionTable.transaction_id == transaction_id)
            if sender_id:
                query = query.filter(TransactionTable.sender_user_id.ilike(f"%{sender_id}%"))
            if receiver_id:
                query = query.filter(TransactionTable.receiver_user_id.ilike(f"%{receiver_id}%"))
            if transaction_type:
                query = query.filter(TransactionTable.transaction_type == transaction_type)
            if status:
                query = query.filter(TransactionTable.status == status)
            if created_from:
                query = query.filter(TransactionTable.created_at >= created_from)
            if created_to:
                query = query.filter(TransactionTable.created_at <= created_to)
            if min_amount is not None:
                query = query.filter(TransactionTable.amount >= min_amount)
            if max_amount is not None:
                query = query.filter(TransactionTable.amount <= max_amount)
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * limit
            transactions = query.order_by(desc(TransactionTable.created_at)).offset(offset).limit(limit).all()
            
            # Format response
            transaction_list = []
            for tx in transactions:
                transaction_list.append({
                    "transaction_id": tx.transaction_id,
                    "sender_user_id": tx.sender_user_id,
                    "receiver_user_id": tx.receiver_user_id,
                    "transaction_type": tx.transaction_type.value if tx.transaction_type else None,
                    "amount": float(tx.amount),
                    "currency": tx.currency,
                    "status": tx.status.value if tx.status else None,
                    "description": tx.reference or "",
                    "created_at": tx.created_at.isoformat() if tx.created_at else None
                })
            
            return GlobalResponse(
                success=True,
                message="Transactions retrieved successfully",
                data={"transactions": transaction_list},
                pagination={
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "total_pages": (total + limit - 1) // limit
                }
            )
            
        except HTTPException:
            raise
        
        except Exception as e:
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    def get_transaction_details(
        self,
        transaction_id: str
    ) -> GlobalResponse:
        try:
            transaction = self.db.query(TransactionTable).filter(
                TransactionTable.transaction_id == transaction_id
            ).first()
            
            if not transaction:
                raise HTTPException(status_code=404, detail="Transaction not found")
            
            return GlobalResponse(
                success=True,
                message="Transaction details retrieved successfully",
                data={
                    "transaction_id": transaction.transaction_id,
                    "sender_user_id": transaction.sender_user_id,
                    "receiver_user_id": transaction.receiver_user_id,
                    "transaction_type": transaction.transaction_type,
                    "amount": float(transaction.amount),
                    "currency": transaction.currency,
                    "status": transaction.status,
                    "description": transaction.description,
                    "fee": float(transaction.fee) if transaction.fee else 0,
                    "net_amount": float(transaction.net_amount) if transaction.net_amount else 0,
                    "reference_id": transaction.reference_id,
                    "created_at": transaction.created_at,
                    "updated_at": transaction.updated_at
                }
            )
            
        except HTTPException:
            raise

        except Exception as e:
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    def cancel_transaction(
        self,
        transaction_id: str,
        payload: TransactionActionRequest
    ) -> GlobalResponse:
        try:
            transaction = self.db.query(TransactionTable).filter(
                TransactionTable.transaction_id == transaction_id
            ).first()
            
            if not transaction:
                raise HTTPException(status_code=404, detail="Transaction not found")
            
            if transaction.status not in [TransactionStatus.PENDING.value, TransactionStatus.SUCCESS.value]:
                raise HTTPException(status_code=400, detail=f"Cannot cancel transaction with status: {transaction.status}")
            
            # Update transaction status
            old_status = transaction.status
            transaction.status = TransactionStatus.CANCELLED.value
            transaction.updated_at = datetime.now(timezone.utc)
            
            # If transaction was successful, refund to sender
            if old_status == TransactionStatus.SUCCESS.value:
                sender_wallet = self.db.query(WalletTable).filter(
                    WalletTable.user_id == transaction.sender_user_id
                ).first()
                
                if sender_wallet:
                    # Credit back the amount (including fee reversal logic could be added)
                    sender_wallet.balance += Decimal(str(transaction.amount))
                    sender_wallet.last_updated = datetime.now(timezone.utc)
                    
                    # Create refund transaction record
                    refund_tx = TransactionTable(
                        transaction_id=Generators.generate_transaction_id(),
                        sender_user_id="SYSTEM_REFUND",
                        receiver_user_id=transaction.sender_user_id,
                        transaction_type="refund",
                        amount=transaction.amount,
                        currency=transaction.currency,
                        status=TransactionStatus.SUCCESS.value,
                        description=f"Refund for cancelled transaction {transaction_id}",
                        reference_id=transaction_id,
                        fee=0,
                        net_amount=transaction.amount
                    )
                    self.db.add(refund_tx)
            
            self.db.commit()
            
            return GlobalResponse(
                success=True,
                message="Transaction cancelled successfully",
                data={
                    "transaction_id": transaction_id,
                    "action": "cancel",
                    "previous_status": old_status,
                    "status": TransactionStatus.CANCELLED.value,
                    "reason": payload.reason,
                    "processed_by": self.authorization,
                    "processed_at": datetime.now(timezone.utc)
                }
            )
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    def list_wallets(
        self,
        page: int,
        limit: int,
        search: Optional[str] = None,
        min_balance: Optional[float] = None,
        max_balance: Optional[float] = None
    ) -> GlobalResponse:
        try:
            # Join query for wallets with users
            query = self.db.query(WalletTable).join(UserTable)
            
            # Apply filters
            if search:
                query = query.filter(
                    or_(
                        UserTable.full_name.ilike(f"%{search}%"),
                        UserTable.email_address.ilike(f"%{search}%"),
                        UserTable.phone_number.ilike(f"%{search}%"),
                        WalletTable.user_id.ilike(f"%{search}%")
                    )
                )
            if min_balance is not None:
                query = query.filter(WalletTable.balance >= min_balance)
            if max_balance is not None:
                query = query.filter(WalletTable.balance <= max_balance)
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * limit
            wallets = query.order_by(desc(WalletTable.last_updated)).offset(offset).limit(limit).all()
            
            # Format response
            wallet_list = []
            for wallet in wallets:
                user = self.db.query(UserTable).filter(UserTable.user_id == wallet.user_id).first()
                wallet_list.append({
                    "user_id": wallet.user_id,
                    "full_name": user.full_name if user else "Unknown",
                    "email": user.email_address if user else "Unknown",
                    "phone": user.phone_number if user else "Unknown",
                    "balance": float(wallet.balance),
                    "currency": wallet.currency,
                    "last_updated": wallet.last_updated.isoformat() if wallet.last_updated else None
                })
            
            return GlobalResponse(
                success=True,
                message="Wallets retrieved successfully",
                data={"wallets": wallet_list},
                pagination={
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "total_pages": (total + limit - 1) // limit
                }
            )
            
        except HTTPException:
            raise

        except Exception as e:
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    def list_kyc_request(self) -> GlobalResponse:
        # verify admin
        kycLists = self.db.query(KYCTable).filter(
            KYCTable.kyc_status == KYCStatus.PENDING
        ).order_by(desc(KYCTable.created_at)).all()

        kyc_pending_list = []

        for kycList in kycLists:
            user = self.db.query(UserTable).filter(UserTable.user_id == kycList.user_id).first()

            kyc_pending_list.append({
                "kyc_id": None,
                "user_id": kycList.user_id,
                "full_name": user.full_name if user else "Unknown",
                "email_address": user.email_address if user else "Unknown",
                "document_type": kycList.document_type,
                "document_number": kycList.document_number,
                "front_image_url": kycList.front_image_url,
                "back_image_url": kycList.back_image_url,
                "selfie_image_url": kycList.user_face_image_url,
                "kyc_status": kycList.kyc_status.value if kycList.kyc_status else None,
                "submitted_at": kycList.created_at
            })

        return GlobalResponse(
            success=True,
            message="KYC requests retrieved successfully",
            data={
                "kyc_request": kyc_pending_list
            }
        )

    def kyc_request_details(self) -> GlobalResponse:
        try:
            # Extract user_id from path parameters via request
            user_id = self.request.path_params.get("user_id")
            
            kyc_record = self.db.query(KYCTable).filter(
                KYCTable.user_id == user_id
            ).first()

            if not kyc_record:
                raise HTTPException(status_code=404, detail="KYC request not found for this user")

            user = self.db.query(UserTable).filter(UserTable.user_id == user_id).first()

            return GlobalResponse(
                success=True,
                message="KYC request details retrieved successfully",
                data={
                    "user_id": kyc_record.user_id,
                    "full_name": user.full_name if user else "Unknown",
                    "email_address": user.email_address if user else "Unknown",
                    "phone_number": user.phone_number if user else "Unknown",
                    "document_type": kyc_record.document_type,
                    "document_number": kyc_record.document_number,
                    "front_image_url": kyc_record.front_image_url,
                    "back_image_url": kyc_record.back_image_url,
                    "selfie_image_url": kyc_record.user_face_image_url,
                    "kyc_status": kyc_record.kyc_status.value if kyc_record.kyc_status else None,
                    "rejection_reason": kyc_record.rejection_reason,
                    "submitted_at": kyc_record.created_at,
                    "updated_at": kyc_record.updated_at
                }
            )
        except HTTPException:
            raise

        except Exception as e:
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    def update_kyc_request(self, payload: KYCUpdateRequest) -> GlobalResponse:
        try:
            kyc_record: KYCTable = self.db.query(KYCTable).filter(
                KYCTable.user_id == payload.user_id
            ).first()

            if not kyc_record:
                raise HTTPException(
                    status_code=404,
                    detail="KYC record not found"
                )

            try:
                new_status = KYCStatus(payload.kyc_status)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid KYC status"
                )

            if new_status == KYCStatus.REJECTED and not payload.rejection_reason:
                raise HTTPException(
                    status_code=400,
                    detail="Rejection reason is required"
                )

            # Update KYC status
            kyc_record.kyc_status = new_status
            kyc_record.rejection_reason = payload.rejection_reason if new_status == KYCStatus.REJECTED else None
            kyc_record.updated_at = datetime.now(timezone.utc)

            notification_title = "KYC Verification Update"
            notification_body = (
                f"Your KYC verification has been {new_status.value}. "
                + (f"Reason: {payload.rejection_reason}" if payload.rejection_reason else "")
            )

            # Create notification for the user
            notification = NotificationTable(
                target_id=payload.user_id,
                type=NotificationType.ALERT,
                title=notification_title,
                body=notification_body,
                creator=NotificationCreator.ADMIN
            )
            self.db.add(notification)

            try:
                notification_service = NotificationServices(
                    db=self.db,
                    background_tasks=self.background_tasks
                )
                notification_service.send_notification(
                    NotificationData(
                        user_id=payload.user_id,
                        template="kyc.updated",
                        context={
                            "status": new_status.value,
                            "reason": payload.rejection_reason,
                        },
                        noty_type=NotificationType.ALERT,
                        data={
                            "kyc_status": new_status.value,
                            "rejection_reason": payload.rejection_reason,
                        },
                        push=True,
                        email=False,
                        sms=False
                    )
                )
            except Exception as e:
                print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     KYC notification failed: {e}")

            self.db.commit()

            return GlobalResponse(
                success=True,
                message=f"KYC status updated to {new_status.value} successfully",
                data={
                    "user_id": payload.user_id,
                    "kyc_status": new_status.value,
                    "updated_at": kyc_record.updated_at
                }
            )
        except HTTPException:
            raise

        except Exception as e:
            self.db.rollback()
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")


    def notify_user(self, user_id: str, payload: AdminNotyfyResuest):
        try:
            target_user_id = user_id or payload.user_id
            notification_type = payload.notification_type or payload.type or NotificationType.ALERT
            notification_body = payload.message or payload.body

            if not target_user_id:
                raise HTTPException(status_code=400, detail="User ID is required")

            if not notification_body:
                raise HTTPException(status_code=400, detail="Notification message is required")

            user = self.db.query(UserTable).filter(
                UserTable.user_id == target_user_id
            ).first()
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            settings: SettingsTable = user.settings
            push_allowed = payload.send_push and (settings.allow_notifications if settings else True)

            # Store notification in DB
            notification = NotificationTable(
                target_id=target_user_id,
                type=notification_type,
                title=payload.title,
                body=notification_body,
                img_url=payload.image_url,
                meta_data={
                    "button_text": payload.button_text,
                    "button_link": payload.button_link,
                    "send_push": push_allowed,
                    "send_email": payload.send_email,
                    "send_sms": payload.send_sms,
                },
                creator=NotificationCreator.ADMIN
            )
            self.db.add(notification)
            self.db.commit()

            try:
                notification_service = NotificationServices(
                    db=self.db,
                    background_tasks=self.background_tasks
                )
                notification_service.send_notification(
                    NotificationData(
                        user_id=target_user_id,
                        title=payload.title,
                        template="admin.custom",
                        context={
                            "body": notification_body,
                            "button_text": payload.button_text,
                            "button_link": payload.button_link,
                        },
                        noty_type=notification_type,
                        data={
                            "button_text": payload.button_text,
                            "button_link": payload.button_link,
                        },
                        image_url=payload.image_url,
                        push=push_allowed,
                        email=payload.send_email,
                        sms=payload.send_sms
                    )
                )
            except Exception as e:
                print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     Admin notification delivery failed: {e}")

            return GlobalResponse(
                success=True,
                message="Notification queued successfully",
                data={
                    "user_id": target_user_id,
                    "title": payload.title,
                    "send_push": push_allowed,
                    "send_email": payload.send_email,
                    "send_sms": payload.send_sms
                }
            )

        except HTTPException:
            raise
        
        except Exception as e:
            self.db.rollback()
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    def list_delete_account_requests(
        self,
        page: int,
        limit: int,
        search: Optional[str] = None,
        status: str = "pending"
    ) -> GlobalResponse:
        try:
            query = self.db.query(DeletedUserTable)

            if status == "pending":
                query = query.filter(DeletedUserTable.is_processed == False)
            elif status == "processed":
                query = query.filter(DeletedUserTable.is_processed == True)

            if search:
                query = query.filter(
                    or_(
                        DeletedUserTable.user_id.ilike(f"%{search}%"),
                        DeletedUserTable.full_name.ilike(f"%{search}%"),
                        DeletedUserTable.email_address.ilike(f"%{search}%"),
                        DeletedUserTable.phone_number.ilike(f"%{search}%")
                    )
                )

            total = query.count()
            offset = (page - 1) * limit
            delete_requests = query.order_by(
                desc(DeletedUserTable.requested_at)
            ).offset(offset).limit(limit).all()

            request_list = []
            for delete_request in delete_requests:
                user = self.db.query(UserTable).filter(
                    UserTable.user_id == delete_request.user_id
                ).first()
                wallet = self.db.query(WalletTable).filter(
                    WalletTable.user_id == delete_request.user_id
                ).first()
                transaction_count = self.db.query(TransactionTable).filter(
                    or_(
                        TransactionTable.sender_user_id == delete_request.user_id,
                        TransactionTable.receiver_user_id == delete_request.user_id
                    )
                ).count()

                request_list.append({
                    "id": delete_request.id,
                    "user_id": delete_request.user_id,
                    "full_name": delete_request.full_name,
                    "email_address": delete_request.email_address,
                    "phone_number": (
                        f"{delete_request.country_code or ''}{delete_request.phone_number or ''}"
                        if delete_request.phone_number else None
                    ),
                    "reason": delete_request.reason,
                    "requested_at": delete_request.requested_at,
                    "scheduled_delete_at": delete_request.scheduled_delete_at,
                    "is_processed": delete_request.is_processed,
                    "processed_at": delete_request.processed_at,
                    "account_exists": user is not None,
                    "wallet_balance": float(wallet.balance) if wallet else 0,
                    "wallet_currency": wallet.currency if wallet else "BDT",
                    "transaction_count": transaction_count
                })

            return GlobalResponse(
                success=True,
                message="Delete account requests retrieved successfully",
                data={"delete_requests": request_list},
                pagination={
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "total_pages": (total + limit - 1) // limit
                }
            )

        except HTTPException:
            raise

        except Exception as e:
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    def approve_delete_account_request(
        self,
        request_id: int,
        payload: DeleteAccountReviewRequest
    ) -> GlobalResponse:
        try:
            delete_request = self.db.query(DeletedUserTable).filter(
                DeletedUserTable.id == request_id
            ).first()

            if not delete_request:
                raise HTTPException(status_code=404, detail="Delete account request not found")

            if delete_request.is_processed:
                raise HTTPException(status_code=400, detail="Delete account request already processed")

            user = self.db.query(UserTable).filter(
                UserTable.user_id == delete_request.user_id
            ).first()

            if not user:
                delete_request.is_processed = True
                delete_request.processed_at = Helpers.utc6dhaka()
                delete_request.updated_at = Helpers.utc6dhaka()
                self.db.commit()

                return GlobalResponse(
                    success=True,
                    message="Delete account request marked as processed",
                    data={"request_id": request_id}
                )

            sessions = self.db.query(SessionTable).filter(
                SessionTable.user_id == user.user_id
            ).all()
            for session in sessions:
                session.is_login = False
                session.access_token_hash = None
                session.refresh_token_hash = None
                session.fcm_token = None
                session.logout_at = Helpers.utc6dhaka()

            if user.settings:
                user.settings.account_locked = True

            anonymized_email = f"d{delete_request.id}@deleted.local"
            user.full_name = "Deleted User"
            user.email_address = anonymized_email
            user.country_code = None
            user.phone_number = None
            user.password_hash = None
            user.profile_image_url = None
            user.phone_verified = False
            user.email_verified = False
            user.link_google = None
            user.updated_at = Helpers.utc6dhaka()

            delete_request.is_processed = True
            delete_request.processed_at = Helpers.utc6dhaka()
            delete_request.updated_at = Helpers.utc6dhaka()

            self.db.commit()

            return GlobalResponse(
                success=True,
                message="Account deletion request approved successfully",
                data={
                    "request_id": request_id,
                    "user_id": delete_request.user_id,
                    "processed_at": delete_request.processed_at,
                    "note": payload.note
                }
            )

        except HTTPException:
            raise

        except Exception as e:
            self.db.rollback()
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    def reject_delete_account_request(
        self,
        request_id: int,
        payload: DeleteAccountReviewRequest
    ) -> GlobalResponse:
        try:
            delete_request = self.db.query(DeletedUserTable).filter(
                DeletedUserTable.id == request_id
            ).first()

            if not delete_request:
                raise HTTPException(status_code=404, detail="Delete account request not found")

            if delete_request.is_processed:
                raise HTTPException(status_code=400, detail="Delete account request already processed")

            user = self.db.query(UserTable).filter(
                UserTable.user_id == delete_request.user_id
            ).first()

            user_id = delete_request.user_id

            if user and user.settings:
                user.settings.account_locked = False

            self.db.delete(delete_request)
            self.db.commit()

            return GlobalResponse(
                success=True,
                message="Delete account request rejected successfully",
                data={
                    "request_id": request_id,
                    "user_id": user_id,
                    "note": payload.note
                }
            )

        except HTTPException:
            raise

        except Exception as e:
            self.db.rollback()
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
