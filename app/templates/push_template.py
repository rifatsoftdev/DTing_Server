from enum import Enum
from typing import Any, Dict, List

from app.constants import String


def _pack(title: str, body: str) -> Dict[str, str]:
    return {"title": title, "body": body}


class PushTemplate:
    @staticmethod
    def welcome_push_template(name: str):
        return _pack(
            f"Welcome to {String.COMPANY_NAME}!",
            f"Hello {name}, your account is ready. Thanks for joining us.",
        )

    @staticmethod
    def otp_push_template(name: str, email: str, otp: str):
        return _pack(
            "Your OTP Code",
            f"Hello {name}, your OTP is {otp}. Valid for 5 minutes.",
        )

    @staticmethod
    def login_alert_push_template(name: str, email: str, ip_address: str):
        return PushTemplate.new_device_login_push_template(
            name=name,
            device="Unknown device",
            ip_address=ip_address,
            email=email,
        )

    @staticmethod
    def kyc_update_push_template(name: str, status: str):
        return _pack(
            "KYC Verification Update",
            f"Hello {name}, your KYC status is now {status.upper()}.",
        )

    @staticmethod
    def reset_password_push_template(name: str, email: str, reset_link: str):
        return _pack(
            "Reset Your Password",
            f"Hello {name}, a password reset was requested for {email}. Tap to reset it.",
        )

    @staticmethod
    def general_notification_push_template(name: str, title: str, message: str, button_text: str = None, button_link: str = None):
        return _pack(title, f"Hello {name}, {message}")

    @staticmethod
    def password_changed_push_template(name: str, changed_at: str, ip_address: str) -> Dict[str, str]:
        return _pack(
            "Password Changed",
            f"Hello {name}, your password was changed from IP {ip_address}. Secure your account if this was not you.",
        )

    @staticmethod
    def email_changed_push_template(name: str, old_email: str, new_email: str) -> Dict[str, str]:
        return _pack(
            "Email Address Changed",
            f"Hello {name}, your email changed to {new_email}. Contact support if this was not you.",
        )

    @staticmethod
    def two_factor_enabled_push_template(name: str) -> Dict[str, str]:
        return _pack(
            "Two-Factor Authentication Enabled",
            f"Hello {name}, two-factor authentication is now enabled.",
        )

    @staticmethod
    def two_factor_disabled_push_template(name: str) -> Dict[str, str]:
        return _pack(
            "Two-Factor Authentication Disabled",
            f"Hello {name}, two-factor authentication was disabled. Secure your account if this was not you.",
        )

    @staticmethod
    def new_device_login_push_template(name: str, device: str, ip_address: str, location: str = None, email: str = None) -> Dict[str, str]:
        location_text = f" near {location}" if location else ""
        return _pack(
            "New Login Detected",
            f"Hello {name}, new login from {device}, IP {ip_address}{location_text}.",
        )

    @staticmethod
    def account_locked_push_template(name: str, unlock_time: str = None) -> Dict[str, str]:
        unlock_text = f" Try again after {unlock_time}." if unlock_time else ""
        return _pack(
            "Account Locked",
            f"Hello {name}, your account is temporarily locked.{unlock_text}",
        )

    @staticmethod
    def account_unlocked_push_template(name: str) -> Dict[str, str]:
        return _pack(
            "Account Unlocked",
            f"Hello {name}, your account has been unlocked.",
        )

    @staticmethod
    def email_verification_push_template(name: str, verification_link: str) -> Dict[str, str]:
        return _pack(
            "Verify Your Email Address",
            f"Hello {name}, tap to verify your email address.",
        )

    @staticmethod
    def password_reset_success_push_template(name: str) -> Dict[str, str]:
        return _pack(
            "Password Reset Successful",
            f"Hello {name}, your password has been reset successfully.",
        )

    @staticmethod
    def recovery_code_push_template(name: str, recovery_codes: List[str]) -> Dict[str, str]:
        return _pack(
            "Your Recovery Codes",
            f"Hello {name}, new recovery codes were generated. Keep them secure.",
        )

    @staticmethod
    def account_deleted_push_template(name: str) -> Dict[str, str]:
        return _pack(
            "Account Deleted",
            f"Hello {name}, your account has been deleted successfully.",
        )

    @staticmethod
    def account_deactivated_push_template(name: str, reason: str = None) -> Dict[str, str]:
        reason_text = f" Reason: {reason}." if reason else ""
        return _pack(
            "Account Deactivated",
            f"Hello {name}, your account has been deactivated.{reason_text}",
        )

    @staticmethod
    def account_reactivated_push_template(name: str) -> Dict[str, str]:
        return _pack(
            "Account Reactivated",
            f"Hello {name}, your account has been reactivated.",
        )

    @staticmethod
    def subscription_expiry_push_template(name: str, expiry_date: str) -> Dict[str, str]:
        return _pack(
            "Subscription Expiry Notice",
            f"Hello {name}, your subscription expires on {expiry_date}.",
        )

    @staticmethod
    def maintenance_notification_push_template(name: str, maintenance_time: str) -> Dict[str, str]:
        return _pack(
            "Scheduled Maintenance",
            f"{String.COMPANY_NAME} maintenance is scheduled for {maintenance_time}.",
        )

    @staticmethod
    def terms_update_push_template(name: str) -> Dict[str, str]:
        return _pack(
            "Terms and Conditions Updated",
            f"Hello {name}, our terms and conditions have been updated.",
        )

    @staticmethod
    def admin_alert_push_template(title: str, message: str) -> Dict[str, str]:
        return _pack(title, f"Admin alert: {message}")

    @staticmethod
    def api_key_created_push_template(name: str, key_name: str) -> Dict[str, str]:
        return _pack(
            "API Key Created",
            f"Hello {name}, API key '{key_name}' was created.",
        )

    @staticmethod
    def api_key_revoked_push_template(name: str, key_name: str) -> Dict[str, str]:
        return _pack(
            "API Key Revoked",
            f"Hello {name}, API key '{key_name}' was revoked.",
        )

    @staticmethod
    def transaction_push_template(
        transaction_type: str,
        amount: float,
        status: str = "success",
        **kwargs: Any
    ):
        def clean(value: Any, default: str = "") -> str:
            if value is None:
                return default
            if isinstance(value, Enum):
                return str(value.value)
            return str(value)

        def money(value: Any) -> str:
            try:
                number = float(value)
                return f"{number:,.2f}".rstrip("0").rstrip(".")
            except (TypeError, ValueError):
                return clean(value, "0")

        tx_type = clean(transaction_type).lower().replace("_", "").replace("-", "").replace(" ", "")
        status_text = clean(status, "success").lower()
        is_success = status_text in ["success", "successful", "completed", "complete"]
        status_label = "Successful" if is_success else status_text.title()
        sent_status_label = "Successfully" if is_success else status_label
        amount_text = f"{money(amount)} TK"

        receiver = clean(kwargs.get("receiver") or kwargs.get("recipient") or kwargs.get("receiver_account"), "recipient")
        sender = clean(kwargs.get("sender") or kwargs.get("sender_account"), "sender")
        account = clean(kwargs.get("account") or kwargs.get("bill_account") or kwargs.get("number"))
        provider = clean(kwargs.get("provider") or kwargs.get("account_name") or kwargs.get("organization"))
        reference = clean(kwargs.get("reference"))
        service_charge = kwargs.get("service_charge") or kwargs.get("charge")
        total = kwargs.get("total") or kwargs.get("total_deducted")

        details = []
        if service_charge is not None:
            details.append(f"Service Charge: {money(service_charge)} TK")
        if total is not None:
            details.append(f"Total Deducted: {money(total)} TK")
        if reference and reference.upper() != "N/A":
            details.append(f"Reference: {reference}")

        suffix = f" {'; '.join(details)}." if details else ""

        templates = {
            "sendmoney": {
                "title": f"Money Sent {sent_status_label}",
                "body": f"You have sent {amount_text} to {receiver}.{suffix}"
            },
            "sentmoney": {
                "title": f"Money Sent {sent_status_label}",
                "body": f"You have sent {amount_text} to {receiver}.{suffix}"
            },
            "receivemoney": {
                "title": "Money Received",
                "body": f"You have received {amount_text} from {sender}.{suffix}"
            },
            "receivedmoney": {
                "title": "Money Received",
                "body": f"You have received {amount_text} from {sender}.{suffix}"
            },
            "recharge": {
                "title": f"Mobile Recharge {status_label}",
                "body": f"Recharge of {amount_text} to {account or receiver} was {status_label.lower()}.{suffix}"
            },
            "mobilerecharge": {
                "title": f"Mobile Recharge {status_label}",
                "body": f"Recharge of {amount_text} to {account or receiver} was {status_label.lower()}.{suffix}"
            },
            "donation": {
                "title": f"Donation {status_label}",
                "body": f"You have donated {amount_text}{f' to {provider}' if provider else ''}.{suffix}"
            },
            "billpay": {
                "title": f"Pay Bill {status_label}",
                "body": f"You have paid {amount_text}{f' to {provider}' if provider else ''}{f' for account {account}' if account else ''}.{suffix}"
            },
            "paybill": {
                "title": f"Pay Bill {status_label}",
                "body": f"You have paid {amount_text}{f' to {provider}' if provider else ''}{f' for account {account}' if account else ''}.{suffix}"
            },
            "deposit": {
                "title": f"Deposit {status_label}",
                "body": f"{amount_text} has been added to your wallet.{suffix}"
            },
            "withdraw": {
                "title": f"Withdraw {status_label}",
                "body": f"You have withdrawn {amount_text}{f' to {account}' if account else ''}.{suffix}"
            },
            "reward": {
                "title": f"Reward {status_label}",
                "body": f"You have received a reward of {amount_text}.{suffix}"
            },
            "cashback": {
                "title": f"Cashback {status_label}",
                "body": f"You have received cashback of {amount_text}.{suffix}"
            },
        }

        return templates.get(tx_type, {
            "title": f"{clean(transaction_type).title()} {status_label}",
            "body": f"Your transaction of {amount_text} was {status_label.lower()}. Tap to see details."
        })
