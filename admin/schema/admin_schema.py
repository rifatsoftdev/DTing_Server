from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
from app.enums.notification_enum import NotificationType


# Enums
class AdminRoleEnum(str, Enum):
    SUPER_ADMIN = "super_admin"
    MODERATOR = "moderator"
    VIEWER = "viewer"


# ============================================================================
# Request Schemas
# ============================================================================

class AdminCreateRequest(BaseModel):
    """Request schema for creating a new admin (super_admin only)"""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Minimum 8 characters")
    full_name: str = Field(..., min_length=2, max_length=100)
    role: AdminRoleEnum = AdminRoleEnum.VIEWER
    profile_image_url: Optional[str] = None


class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str
    device_id: Optional[str] = None
    device_uuid: Optional[str] = None


class AdminLogoutRequest(BaseModel):
    admin_id: str
    access_token: str
    device_id: Optional[str] = None
    device_uuid: Optional[str] = None


class AdminRefreshTokenRequest(BaseModel):
    refresh_token: str
    device_id: Optional[str] = None
    device_uuid: Optional[str] = None


class AdminUpdateRequest(BaseModel):
    """Request schema for updating admin details"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    role: Optional[AdminRoleEnum] = None
    is_active: Optional[bool] = None
    profile_image_url: Optional[str] = None


class AdminSelfUpdateRequest(BaseModel):
    """Request schema for updating own profile"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    profile_image_url: Optional[str] = None


class AdminUserNotifyRequest(BaseModel):
    """Request schema for sending notification/email to a user"""
    title: str = Field(..., min_length=3, max_length=120)
    message: str = Field(..., min_length=5, max_length=1000)
    notification_type: NotificationType = NotificationType.ALERT
    image_url: Optional[str] = None
    send_push: bool = True
    send_email: bool = False
    send_sms: bool = False
    button_text: Optional[str] = None
    button_link: Optional[str] = None


class AdminPasswordUpdateRequest(BaseModel):
    """Request schema for changing admin password (self or super_admin)"""
    admin_id: str
    current_password: Optional[str] = None  # Required for self-change, not for super_admin
    new_password: str = Field(..., min_length=8, description="Minimum 8 characters")


class AdminFilterRequest(BaseModel):
    """Request schema for filtering admin list"""
    search: Optional[str] = None
    email: Optional[str] = None
    role: Optional[AdminRoleEnum] = None
    is_active: Optional[bool] = None
    created_from: Optional[datetime] = None
    created_to: Optional[datetime] = None
    page: int = 1
    limit: int = 20


class UserFilterRequest(BaseModel):
    """Request schema for filtering user list"""
    search: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    kyc_status: Optional[str] = None
    is_active: Optional[bool] = None
    created_from: Optional[datetime] = None
    created_to: Optional[datetime] = None
    page: int = 1
    limit: int = 20


class UserUpdateStatusRequest(BaseModel):
    """Request schema for updating user status (lock/unlock)"""
    is_active: bool
    reason: Optional[str] = None


class TransactionFilterRequest(BaseModel):
    """Request schema for filtering transaction list"""
    search: Optional[str] = None
    transaction_id: Optional[str] = None
    sender_id: Optional[str] = None
    receiver_id: Optional[str] = None
    transaction_type: Optional[str] = None
    status: Optional[str] = None
    created_from: Optional[datetime] = None
    created_to: Optional[datetime] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    page: int = 1
    limit: int = 20


class TransactionActionRequest(BaseModel):
    """Request schema for transaction actions (refund/cancel)"""
    reason: str = Field(..., min_length=10, max_length=500)
    reference_id: Optional[str] = None


class DeleteAccountReviewRequest(BaseModel):
    """Request schema for reviewing account deletion requests"""
    note: Optional[str] = Field(None, max_length=500)


class TransactionActionResponse(BaseModel):
    """Response schema for transaction action"""
    transaction_id: str
    action: str
    status: str
    reason: str
    processed_by: str
    processed_at: datetime
    refund_amount: Optional[float] = None


# ============================================================================
# Response Schemas
# ============================================================================

class AdminResponse(BaseModel):
    admin_id: str
    email: str
    full_name: str
    role: str
    is_active: bool
    is_super_admin: bool
    last_login_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class AdminLoginResponse(BaseModel):
    admin_id: str
    email: str
    full_name: str
    role: str
    permissions: List[str]
    access_token: str
    refresh_token: str


class AdminProfileResponse(BaseModel):
    admin_id: str
    email: str
    full_name: str
    role: str
    permissions: List[str]
    is_active: bool
    is_super_admin: bool
    profile_image_url: Optional[str]
    last_login_at: Optional[datetime]
    created_at: datetime


class PaginatedResponse(BaseModel):
    success: bool
    message: str
    data: dict
    pagination: dict


class UserListItem(BaseModel):
    user_id: str
    full_name: str
    email: str
    phone: str
    profile_image_url: Optional[str]
    phone_verified: bool
    email_verified: bool
    kyc_status: str
    is_active: bool
    wallet_balance: float
    wallet_currency: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserDetailResponse(BaseModel):
    user_id: str
    full_name: str
    email: str
    phone: str
    profile_image_url: Optional[str]
    phone_verified: bool
    email_verified: bool
    kyc_status: str
    kyc_verified_at: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    wallet_balance: float
    wallet_currency: str
    wallet_last_updated: datetime
    
    settings: dict
    
    transactions: List[dict]
    notifications: List[dict]

    class Config:
        from_attributes = True


class TransactionListItem(BaseModel):
    transaction_id: str
    sender_user_id: str
    receiver_user_id: Optional[str]
    transaction_type: str
    amount: float
    currency: str
    status: str
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class WalletResponse(BaseModel):
    user_id: str
    full_name: str
    email: str
    phone: str
    balance: float
    currency: str
    last_updated: datetime

    class Config:
        from_attributes = True


class WalletAdjustmentRequest(BaseModel):
    """Request schema for adjusting wallet balance (super_admin only)"""
    amount: float = Field(..., description="Positive for credit, negative for debit")
    reason: str = Field(..., min_length=5, max_length=500)
    reference_id: Optional[str] = None


class WalletAdjustmentResponse(BaseModel):
    """Response schema for wallet adjustment"""
    user_id: str
    previous_balance: float
    adjusted_amount: float
    new_balance: float
    currency: str
    reason: str
    transaction_id: str
    adjusted_by: str
    adjusted_at: datetime


class DashboardStats(BaseModel):
    """Response schema for dashboard statistics"""
    total_users: int
    active_users: int
    total_transactions: int
    total_transaction_amount: float
    total_wallets_balance: float
    new_users_today: int
    transactions_today: int
    amount_today: float


class AdminListItem(BaseModel):
    admin_id: str
    email: str
    full_name: str
    role: str
    is_active: bool
    is_super_admin: bool
    last_login_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Global Response Wrapper
# ============================================================================

class GlobalAdminResponse(BaseModel):
    success: bool
    message: str
    data: dict = {}
