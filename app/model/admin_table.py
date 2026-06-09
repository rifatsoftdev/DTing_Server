from sqlalchemy import Column, String, Integer, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum

from app.core.database import Base
from app.utils.helpers import utc6dhaka





class AdminRole(str, PyEnum):
    SUPER_ADMIN = "super_admin"
    MODERATOR = "moderator"
    VIEWER = "viewer"


class AdminPermissions:
    """
    Permission constants for admin roles.
    Each permission is a string identifier that can be checked against.
    """
    # User management
    CAN_VIEW_USERS = "can_view_users"
    CAN_CREATE_USERS = "can_create_users"
    CAN_EDIT_USERS = "can_edit_users"
    CAN_DELETE_USERS = "can_delete_users"
    CAN_LOCK_USERS = "can_lock_users"
    
    # Transaction management
    CAN_VIEW_TRANSACTIONS = "can_view_transactions"
    CAN_REFUND_TRANSACTIONS = "can_refund_transactions"
    CAN_CANCEL_TRANSACTIONS = "can_cancel_transactions"
    
    # Wallet management
    CAN_VIEW_WALLETS = "can_view_wallets"
    CAN_ADJUST_WALLETS = "can_adjust_wallets"
    
    # Admin management
    CAN_VIEW_ADMINS = "can_view_admins"
    CAN_CREATE_ADMINS = "can_create_admins"
    CAN_EDIT_ADMINS = "can_edit_admins"
    CAN_DELETE_ADMINS = "can_delete_admins"
    
    # System management
    CAN_VIEW_LOGS = "can_view_logs"
    CAN_VIEW_SETTINGS = "can_view_settings"
    CAN_EDIT_SETTINGS = "can_edit_settings"


# Role-based permission mapping
ROLE_PERMISSIONS = {
    AdminRole.SUPER_ADMIN: [
        # All permissions
        AdminPermissions.CAN_VIEW_USERS,
        AdminPermissions.CAN_CREATE_USERS,
        AdminPermissions.CAN_EDIT_USERS,
        AdminPermissions.CAN_DELETE_USERS,
        AdminPermissions.CAN_LOCK_USERS,
        AdminPermissions.CAN_VIEW_TRANSACTIONS,
        AdminPermissions.CAN_REFUND_TRANSACTIONS,
        AdminPermissions.CAN_CANCEL_TRANSACTIONS,
        AdminPermissions.CAN_VIEW_WALLETS,
        AdminPermissions.CAN_ADJUST_WALLETS,
        AdminPermissions.CAN_VIEW_ADMINS,
        AdminPermissions.CAN_CREATE_ADMINS,
        AdminPermissions.CAN_EDIT_ADMINS,
        AdminPermissions.CAN_DELETE_ADMINS,
        AdminPermissions.CAN_VIEW_LOGS,
        AdminPermissions.CAN_VIEW_SETTINGS,
        AdminPermissions.CAN_EDIT_SETTINGS,
    ],
    AdminRole.MODERATOR: [
        # All except wallet adjustment and admin management
        AdminPermissions.CAN_VIEW_USERS,
        AdminPermissions.CAN_CREATE_USERS,
        AdminPermissions.CAN_EDIT_USERS,
        AdminPermissions.CAN_DELETE_USERS,
        AdminPermissions.CAN_LOCK_USERS,
        AdminPermissions.CAN_VIEW_TRANSACTIONS,
        AdminPermissions.CAN_REFUND_TRANSACTIONS,
        AdminPermissions.CAN_CANCEL_TRANSACTIONS,
        AdminPermissions.CAN_VIEW_WALLETS,
        # NO: CAN_ADJUST_WALLETS
        # NO: CAN_VIEW_ADMINS
        # NO: CAN_CREATE_ADMINS
        # NO: CAN_EDIT_ADMINS
        # NO: CAN_DELETE_ADMINS
        AdminPermissions.CAN_VIEW_LOGS,
        AdminPermissions.CAN_VIEW_SETTINGS,
        # NO: CAN_EDIT_SETTINGS
    ],
    AdminRole.VIEWER: [
        # View only - no write permissions
        AdminPermissions.CAN_VIEW_USERS,
        # NO: CAN_CREATE_USERS
        # NO: CAN_EDIT_USERS
        # NO: CAN_DELETE_USERS
        # NO: CAN_LOCK_USERS
        AdminPermissions.CAN_VIEW_TRANSACTIONS,
        # NO: CAN_REFUND_TRANSACTIONS
        # NO: CAN_CANCEL_TRANSACTIONS
        AdminPermissions.CAN_VIEW_WALLETS,
        # NO: CAN_ADJUST_WALLETS
        AdminPermissions.CAN_VIEW_ADMINS,
        # NO: CAN_CREATE_ADMINS
        # NO: CAN_EDIT_ADMINS
        # NO: CAN_DELETE_ADMINS
        AdminPermissions.CAN_VIEW_LOGS,
        AdminPermissions.CAN_VIEW_SETTINGS,
        # NO: CAN_EDIT_SETTINGS
    ],
}


class AdminTable(Base):
    __tablename__ = "admin_list"

    id = Column(Integer, autoincrement=True, index=True)

    admin_id = Column(
        String,
        primary_key=True,
        unique=True,
        nullable=False
    )
    
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    
    full_name = Column(String, nullable=False)
    profile_image_url = Column(String, nullable=True)
    
    # Secrutry
    totp_enabled = Column(Boolean, nullable=False, default=False)
    totp_secret = Column(String, nullable=True)
    
    role = Column(Enum(AdminRole), default=AdminRole.VIEWER)
    permissions = Column(String, nullable=True)  # JSON string of permissions
    
    is_active = Column(Boolean, default=True)
    is_super_admin = Column(Boolean, default=False)
    
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    last_ip_address = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=utc6dhaka)
    updated_at = Column(DateTime(timezone=True), onupdate=utc6dhaka)

    # Session relationship for one-to-many mapping between admin and sessions
    sessions = relationship(
        "SessionTable",
        foreign_keys="SessionTable.admin_id",
        back_populates="admin",
        cascade="all, delete-orphan"
    )
