from fastapi import BackgroundTasks, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, desc
from datetime import timedelta
from typing import Optional
from decimal import Decimal
from datetime import datetime, timezone, timedelta
import json


from app.constants import AnsiColor, String
from app.enums import NotificationType, NotificationCreator, TransactionStatus, KYCStatus
from app.model import (
    DeletedUserTable, NotificationTable, SettingsTable,
    AdminTable, UserTable, KYCTable, AppConfigTable
)
from app.model.sessions_table import SessionTable
from app.schema import GlobalResponse, KYCUpdateRequest, AdminNotyfyResuest
from app.utils import Helpers, Generators, Hashing

from admin.schema.admin_schema import *

from app.model.admin_table import AdminRole
from services.auth.user_verification import UserVerificationService
from services.notification.notification_services import NotificationData, NotificationServices
from app.schema.auth_schemas import DeleteAccountRequest


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
            # Total API Requests
            # Failed API Requests
            # Total Revenue
            # Pending Payments
            # Total Notifications Sent
            # Total Emails Sent
            # Total Chat Messages
            # System Health
            now = datetime.now(timezone.utc)

            today_start = now.replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )

            seven_days_ago = now - timedelta(days=7)
            thirty_days_ago = now - timedelta(days=30)


            # Total Users
            total_users = self.db.query(UserTable).count()


            # Active Users (today, 7 day, 30 day)
            active_users_today = (
                self.db.query(UserTable)
                .filter(UserTable.last_active_at >= today_start)
                .count()
            )

            active_users_7_days = (
                self.db.query(UserTable)
                .filter(UserTable.last_active_at >= seven_days_ago)
                .count()
            )

            active_users_30_days = (
                self.db.query(UserTable)
                .filter(UserTable.last_active_at >= thirty_days_ago)
                .count()
            )


            # New Registrations
            new_registrations_today = (
                self.db.query(UserTable)
                .filter(UserTable.created_at >= today_start)
                .count()
            )

            new_registrations_7_days = (
                self.db.query(UserTable)
                .filter(UserTable.created_at >= seven_days_ago)
                .count()
            )

            new_registrations_30_days = (
                self.db.query(UserTable)
                .filter(UserTable.created_at >= thirty_days_ago)
                .count()
            )


# Online Users
            online_users = 0
            # online_users = (
            #     self.db.query(UserTable)
            #     .filter(UserTable.is_online == True)
            #     .count()
            # )

            # KYC
            pending_kyc = (
                self.db.query(KYCTable)
                .filter(KYCTable.kyc_status == KYCStatus.PENDING)
                .count()
            )
            
            approved_kyc = (
                self.db.query(KYCTable)
                .filter(KYCTable.kyc_status == KYCStatus.VERIFIED)
                .count()
            )

            rejected_kyc = (
                self.db.query(KYCTable)
                .filter(KYCTable.kyc_status == KYCStatus.REJECTED)
                .count()
            )


            # Notifications
            total_notifications = (
                self.db.query(NotificationTable)
                .count()
            )

            # Deleted Accounts
            deleted_accounts = (
                self.db.query(DeletedUserTable)
                .count()
            )

            return GlobalResponse(
                status_code=200,
                success=True,
                action="",
                message="Dashboard statistics retrieved successfully",
                data={
                    "users": {
                        "total": total_users,
                        "online": online_users,
                        "active_today": active_users_today,
                        "active_7_days": active_users_7_days,
                        "active_30_days": active_users_30_days,
                    },
                    "registrations": {
                        "today": new_registrations_today,
                        "last_7_days": new_registrations_7_days,
                        "last_30_days": new_registrations_30_days,
                    },
                    "kyc": {
                        "pending": pending_kyc,
                        "approved": approved_kyc,
                        "rejected": rejected_kyc,
                    },
                    "notifications": {
                        "total": total_notifications,
                    },
                    "deleted_accounts": deleted_accounts,
                }
            )

        except HTTPException:
            raise

        except Exception as e:
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}: {e}")
            raise HTTPException(
                status_code=500,
                detail="Internal server error"
            )

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
            query = self.db.query(UserTable).join(SettingsTable).outerjoin(KYCTable)
            
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
                query = query.filter(SettingsTable.account_deactivated == (not is_active))
            
            # Get total count
            total = query.count()
            
            # Apply sorting
            if sort_by == "created_at":
                sort_column = UserTable.created_at
            elif sort_by == "full_name":
                sort_column = UserTable.full_name
            else:
                sort_column = UserTable.created_at
            
            if sort_order == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(sort_column)
            
            # Apply pagination
            offset = (page - 1) * limit
            users: UserTable = query.offset(offset).limit(limit).all()
            
            # Format response
            user_list = []
            for user in users:
                settings: SettingsTable = user.settings
                kyc: KYCTable = user.user_kyc

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
                    "kyc_status": kyc.kyc_status.value if kyc and kyc.kyc_status else "pending",
                    "is_active": not (settings.account_deactivated if settings else True),
                    "created_at": user.created_at
                })
            
            return GlobalResponse(
                status_code=200,
                success=True,
                action="",
                message="Users retrieved successfully",
                data={"users": user_list},
                next_step={},
                pagination={
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "total_pages": (total + limit - 1) // limit
                }
            )
            
        except HTTPException as e:
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
            raise

        except Exception as e:
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    def get_user_details(self, user_id: str) -> GlobalResponse:
        try:
            user = self.db.query(UserTable).filter(
                UserTable.user_id == user_id
            ).first()

            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            settings: SettingsTable = user.settings
            user_kyc: KYCTable = user.user_kyc

            phone = (
                f"{user.country_code or ''}{user.phone_number}"
                if user.phone_number
                else None
            )
            
            return GlobalResponse(
                status_code=200,
                success=True,
                action="",
                message="User details retrieved successfully",
                data={
                    "user": {
                        "user_id": user.user_id,
                        "full_name": user.full_name,
                        "email": user.email_address,
                        "phone": phone,
                        "profile_image_url": user.profile_image_url,
                        "phone_verified": user.phone_verified,
                        "email_verified": user.email_verified,
                        "created_at": user.created_at,
                        "updated_at": user.updated_at
                    },
                    "settings": {
                        "allow_notifications": settings.allow_notifications if settings else True,
                        "dark_mode": settings.dark_mode if settings else False,
                        "language": settings.language if settings else "en",
                        "account_locked": settings.account_deactivated if settings else False,
                        "kyc_status": user_kyc.kyc_status if user_kyc else "pending",
                        "kyc_verified_at": user_kyc.updated_at if user_kyc else None,
                    }
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
            status_code=200,
            success=True,
            action="",
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
                status_code=200,
                success=True,
                action="",
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
                status_code=200,
                success=True,
                action="",
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
                status_code=200,
                success=True,
                action="",
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

    def get_app_config(self) -> GlobalResponse:
        try:
            configs = self.db.query(AppConfigTable).all()
            
            config_dict = {}
            for config in configs:
                config_dict[config.key] = config.value
            
            return GlobalResponse(
                status_code=200,
                success=True,
                action="",
                message="App configuration retrieved successfully",
                data=config_dict
            )
        
        except HTTPException:
            raise
        
        except Exception as e:
            self.db.rollback()
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    def get_config_by_key(self, key: str) -> GlobalResponse:
        try:
            config = self.db.query(AppConfigTable).filter(
                AppConfigTable.key == key
            ).first()
            
            if not config:
                raise HTTPException(status_code=404, detail="Configuration not found")
            
            return GlobalResponse(
                status_code=200,
                success=True,
                action="",
                message="Configuration retrieved successfully",
                data={"key": config.key, "value": config.value}
            )
        
        except HTTPException:
            raise
        
        except Exception as e:
            self.db.rollback()
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    def update_app_config(self, payload: AppConfigRequest) -> GlobalResponse:
        try:
            admin_id = self.verify_authorization(self.authorization)
            
            current_admin = self.db.query(AdminTable).filter(
                AdminTable.admin_id == admin_id
            ).first()
            
            if not current_admin:
                raise HTTPException(status_code=401, detail="Unauthorized")
            
            if current_admin.role != AdminRole.SUPER_ADMIN:
                raise HTTPException(status_code=403, detail="Only super admins can update configurations")
            
            config_keys = ["service_enabled", "sms_enabled", "maintenance_mode"]
            updated_configs = []
            
            for key in config_keys:
                if getattr(payload, key) is not None:
                    value = getattr(payload, key)
                    
                    config = self.db.query(AppConfigTable).filter(
                        AppConfigTable.key == key
                    ).first()
                    
                    if config:
                        config.value = json.dumps({"enabled": value})
                        config.updated_at = datetime.now(timezone.utc)
                    else:
                        config = AppConfigTable(
                            key=key,
                            value=json.dumps({"enabled": value})
                        )
                        self.db.add(config)
                    
                    updated_configs.append(key)
            
            self.db.commit()
            
            return GlobalResponse(
                status_code=200,
                success=True,
                action="",
                message=f"Configuration updated successfully: {', '.join(updated_configs)}",
                data={"updated_keys": updated_configs}
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
                    "account_exists": user is not None
                })

            return GlobalResponse(
                status_code=200,
                success=True,
                action="",
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
                status_code=200,
                success=True,
                action="",
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
                status_code=200,
                success=True,
                action="",
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




